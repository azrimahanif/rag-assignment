import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MessageSquare, Send, Bot, User, Menu, X, Loader2 } from 'lucide-react';
import { ChatSidebar } from './components/ChatSidebar';
import { SourcePanel } from './components/SourcePanel';
import { SourceBadge } from './components/SourceBadge';
import { StructuredResponseComponent } from './components/StructuredResponseComponent';
import { parseStructuredResponse } from './utils/markdownParser';
import {
  sendMessageToWebhook,
  getOrCreateSessionId,
  getNextConversationId,
  getNextMessageId,
  createChatSession,
  getSessionMessages,
  listChatSessions,
  deleteChatSession
} from './lib/api';
import type { Message, SourceItem, StructuredResponse, ChatSession } from './types';

// Theme type
type Theme = 'light' | 'dark' | 'system';

interface LocalSession {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

function App() {
  // Theme state - forced to light mode
  const [theme, setTheme] = useState<Theme>('light');

  // Apply theme to document - forced to light mode
  useEffect(() => {
    const root = window.document.documentElement;
    root.className = 'light';
  }, []);

  // Add download function to global scope for HTML onclick handlers
  useEffect(() => {
    // Import the download utilities
    import('./lib/utils').then(({ downloadImageAsPng, generateChartFilename }) => {
      // Add downloadChart function to global window object
      (window as any).downloadChart = async (url: string, title: string) => {
        try {
          const filename = generateChartFilename(title, 0);
          await downloadImageAsPng(url, filename, title);
        } catch (error) {
          console.error('❌ Failed to download chart:', error);
          // Show user-friendly error message
          const errorMessage = document.createElement('div');
          errorMessage.textContent = 'Download failed. Please try again.';
          errorMessage.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
          `;
          document.body.appendChild(errorMessage);

          // Remove error message after 3 seconds
          setTimeout(() => {
            if (errorMessage.parentNode) {
              errorMessage.parentNode.removeChild(errorMessage);
            }
          }, 3000);
        }
      };
    });
  }, []);

  // Session management
  const [sessionId, setSessionId] = useState(() => getOrCreateSessionId());
  const [localSessions, setLocalSessions] = useState<LocalSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSwitchingSession, setIsSwitchingSession] = useState(false);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedSources, setSelectedSources] = useState<SourceItem[]>([]);
  const [currentSourceMessageId, setCurrentSourceMessageId] = useState<string | null>(null);
  const [isSourcePanelOpen, setIsSourcePanelOpen] = useState(false);

  // UI state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load sessions from localStorage
  useEffect(() => {
    const savedSessions = localStorage.getItem('chatSessions');
    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions);
        if (Array.isArray(parsed)) {
          const sessions = parsed.map(session => ({
            ...session,
            createdAt: new Date(session.createdAt),
            updatedAt: new Date(session.updatedAt)
          }));
          setLocalSessions(sessions);
        }
      } catch (error) {
        console.error('Failed to parse saved sessions:', error);
      }
    }
  }, []);

  // Auto-select session or create new one
  useEffect(() => {
    if (localSessions.length > 0 && !currentSessionId) {
      setCurrentSessionId(localSessions[0].id);
    } else if (localSessions.length === 0 && !currentSessionId) {
      createNewSession();
    }
  }, [localSessions, currentSessionId]);

  // Load messages for current session
  useEffect(() => {
    if (currentSessionId) {
      const sessionMessages = localStorage.getItem(`messages_${currentSessionId}`);
      if (sessionMessages) {
        try {
          const parsed = JSON.parse(sessionMessages);
          if (Array.isArray(parsed)) {
            const messages = parsed.map(msg => ({
              ...msg,
              timestamp: new Date(msg.timestamp)
            }));
            setMessages(messages);
          }
        } catch (error) {
          console.error('Failed to parse session messages:', error);
        }
      } else {
        setMessages([]);
      }
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  // Save sessions to localStorage
  const saveSessions = useCallback((sessions: LocalSession[]) => {
    localStorage.setItem('chatSessions', JSON.stringify(sessions));
    setLocalSessions(sessions);
  }, []);

  // Save messages to localStorage
  const saveMessages = useCallback((sessionId: string, messages: Message[]) => {
    localStorage.setItem(`messages_${sessionId}`, JSON.stringify(messages));
  }, []);

  // Create new session
  const createNewSession = useCallback(() => {
    const newSession: LocalSession = {
      id: getOrCreateSessionId(),
      title: 'New Chat',
      createdAt: new Date(),
      updatedAt: new Date(),
      messageCount: 0
    };

    const updatedSessions = [newSession, ...localSessions];
    saveSessions(updatedSessions);
    setCurrentSessionId(newSession.id);
    setMessages([]);
    setIsSidebarOpen(false);
  }, [localSessions, saveSessions]);

  // Delete session
  const deleteSession = useCallback((sessionId: string) => {
    const updatedSessions = localSessions.filter(session => session.id !== sessionId);
    saveSessions(updatedSessions);
    localStorage.removeItem(`messages_${sessionId}`);

    if (currentSessionId === sessionId) {
      if (updatedSessions.length > 0) {
        setCurrentSessionId(updatedSessions[0].id);
      } else {
        createNewSession();
      }
    }
  }, [localSessions, saveSessions, currentSessionId, createNewSession]);

  // Switch session
  const switchSession = useCallback(async (sessionId: string) => {
    if (sessionId === currentSessionId || isSwitchingSession) return;

    setIsSwitchingSession(true);
    try {
      setCurrentSessionId(sessionId);
      setIsSidebarOpen(false);
    } catch (error) {
      console.error('Failed to switch session:', error);
    } finally {
      setIsSwitchingSession(false);
    }
  }, [currentSessionId, isSwitchingSession]);

  // Clear all sessions
  const clearAllSessions = useCallback(() => {
    if (window.confirm('Are you sure you want to clear all chat sessions? This action cannot be undone.')) {
      // Clear all messages
      localSessions.forEach(session => {
        localStorage.removeItem(`messages_${session.id}`);
      });

      // Clear sessions
      localStorage.removeItem('chatSessions');
      setLocalSessions([]);
      setCurrentSessionId(null);
      setMessages([]);

      // Create new session
      createNewSession();
    }
  }, [localSessions, createNewSession]);

  // Generate session title
  const generateSessionTitle = useCallback((messages: Message[]) => {
    const userMessages = messages.filter(msg => msg.role === 'user');
    if (userMessages.length === 0) return 'New Chat';

    const firstMessage = userMessages[0].content;
    // Use first 30 chars of first message as title
    return firstMessage.length > 30
      ? firstMessage.substring(0, 30) + '...'
      : firstMessage;
  }, []);

  // Update session title
  const updateSessionTitle = useCallback((sessionId: string, title: string) => {
    const updatedSessions = localSessions.map(session =>
      session.id === sessionId
        ? { ...session, title, updatedAt: new Date() }
        : session
    );
    saveSessions(updatedSessions);
  }, [localSessions, saveSessions]);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  
  // Focus input when switching to chat
  useEffect(() => {
    if (!isSidebarOpen && !isSourcePanelOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isSidebarOpen, isSourcePanelOpen]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Focus input with Ctrl+K
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Get messages with sources for navigation
  const messagesWithSources = messages.filter(msg => msg.sources && msg.sources.length > 0);

  // Find current source message index
  const currentSourceMessageIndex = currentSourceMessageId
    ? messagesWithSources.findIndex(msg => msg.id === currentSourceMessageId)
    : -1;

  // Navigate between message sources
  const navigateMessageSources = useCallback((direction: 'next' | 'prev') => {
    if (messagesWithSources.length <= 1) return;

    let newIndex;
    if (direction === 'next') {
      newIndex = currentSourceMessageIndex >= 0
        ? (currentSourceMessageIndex + 1) % messagesWithSources.length
        : 0;
    } else {
      newIndex = currentSourceMessageIndex > 0
        ? currentSourceMessageIndex - 1
        : messagesWithSources.length - 1;
    }

    const targetMessage = messagesWithSources[newIndex];
    setCurrentSourceMessageId(targetMessage.id);
    setSelectedSources(targetMessage.sources);
  }, [messagesWithSources, currentSourceMessageIndex]);

  // Set sources from message (called when clicking SourceBadge)
  const setMessageSources = useCallback((messageId: string, sources: SourceItem[]) => {
    setCurrentSourceMessageId(messageId);
    setSelectedSources(sources);
  }, []);

  // Send message
  const sendMessage = useCallback(async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      content: inputValue.trim(),
      role: 'user',
      timestamp: new Date()
    };

    // Add user message
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    saveMessages(currentSessionId!, updatedMessages);

    // Clear input
    setInputValue('');
    setIsTyping(true);

    // Create new abort controller for this request
    abortControllerRef.current = new AbortController();

    try {
      // Get backend session if available
      let backendSession = null;
      try {
        backendSession = await createChatSession({
          session_id: currentSessionId!,
          title: generateSessionTitle(updatedMessages)
        });
      } catch (error) {
        console.warn('Failed to create backend session:', error);
      }

      const conversationId = getNextConversationId();
      const messageId = getNextMessageId();

      const response = await sendMessageToWebhook({
        sessionId: currentSessionId!,
        chatInput: userMessage.content,
        conversation_id: conversationId,
        message_id: messageId
      }, abortControllerRef.current.signal);

      // Parse structured response
      const structuredResponse = parseStructuredResponse(response.content);

      // Simple chart URL detection and conversion with download buttons
      const processedContent = convertChartUrlsToImages(response.content);

      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        content: processedContent,
        role: 'assistant',
        timestamp: new Date(),
        sources: response.sources,
        structuredResponse
      };

      // Add assistant message
      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);
      saveMessages(currentSessionId!, finalMessages);

      // Update session title if first exchange
      if (messages.length === 0) {
        updateSessionTitle(currentSessionId!, generateSessionTitle(finalMessages));
      }

      // Set sources for source panel and set as current message
      if (response.sources && response.sources.length > 0) {
        setSelectedSources(response.sources);
        setCurrentSourceMessageId(assistantMessage.id);
      }

    } catch (error) {
      if (error.name === 'AbortError') {
          return;
      }

      console.error('Error sending message:', error);

      const errorMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      };

      const errorMessages = [...updatedMessages, errorMessage];
      setMessages(errorMessages);
      saveMessages(currentSessionId!, errorMessages);

    } finally {
      setIsTyping(false);
      abortControllerRef.current = null;
    }
  }, [inputValue, isTyping, messages, currentSessionId, saveMessages, generateSessionTitle, updateSessionTitle]);

  // Handle input key press
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }, [sendMessage]);

  // Cancel current request
  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsTyping(false);
  }, []);

  // Quick action buttons
  const quickActions = [
    { label: 'Population of Malaysia', query: 'What is the current population of Malaysia?' },
    { label: 'Population by State', query: 'Show population breakdown by state in Malaysia' },
    { label: 'Population Growth', query: 'Show population growth rate trend for Malaysia from 2020-2024' },
    { label: 'Compare Kedah vs Selangor population for 2024', query: 'Compare population between Kedah and Selangor 2024' }
  ];

  const handleQuickAction = useCallback((query: string) => {
    setInputValue(query);
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  }, []);

  // Simple function to convert chart URLs to img tags with download buttons
  const convertChartUrlsToImages = useCallback((content: string): string => {
    // Improved regex that handles complex URLs with parentheses and special characters
    const chartUrlPattern = /https?:\/\/quickchart\.io\/chart\?[^\s<]+/gi;
    let chartIndex = 0;

    return content.replace(chartUrlPattern, (url) => {
      chartIndex++;
      const chartId = `chart-${Date.now()}-${chartIndex}`;

      // Extract title from URL if possible, otherwise use default
      const titleMatch = url.match(/title%22%3A%22([^%]+)/);
      const title = titleMatch ? decodeURIComponent(titleMatch[1]) : `Chart ${chartIndex}`;

      return `
<div class="chart-container" style="position: relative; display: inline-block; margin: 15px 0;">
  <img
    src="${url}"
    alt="${title}"
    style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
  />
  <button
    onclick="downloadChart('${url.replace(/'/g, "\\'")}', '${title.replace(/'/g, "\\'")}')"
    class="chart-download-btn"
    style="
      position: absolute;
      top: 10px;
      right: 10px;
      background: rgba(59, 130, 246, 0.9);
      color: white;
      border: none;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      backdrop-filter: blur(4px);
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    "
    onmouseover="this.style.background='rgba(37, 99, 235, 0.95)'; this.style.transform='scale(1.05)'"
    onmouseout="this.style.background='rgba(59, 130, 246, 0.9)'; this.style.transform='scale(1)'"
    title="Download chart as PNG"
  >
    📥 Download
  </button>
</div>`;
    });
  }, []);

  // Render message content
  const renderMessageContent = useCallback((message: Message) => {
    if (message.role === 'user') {
      return <div className="text-gray-900 whitespace-pre-wrap">{message.content}</div>;
    }

    // Assistant message
    const elements = [];

    // Add structured response if available
    if (message.structuredResponse) {
      elements.push(
        <div key="structured" className="mb-4">
          <StructuredResponseComponent response={message.structuredResponse} />
        </div>
      );
    }

    // Add text content (which now includes converted chart images)
    if (message.content) {
      elements.push(
        <div
          key="text"
          className="text-gray-900 mb-4"
          dangerouslySetInnerHTML={{ __html: message.content }}
        />
      );
    }

    // Add source badge if sources are available
    if (message.sources && message.sources.length > 0) {
      elements.push(
        <div key="sources" className="mt-4">
          <SourceBadge
            sourceCount={message.sources.length}
            isActive={currentSourceMessageId === message.id}
            onClick={() => {
              setMessageSources(message.id, message.sources!);
            }}
          />
        </div>
      );
    }

    return elements;
  }, []);

  // Current session for sidebar
  const currentSession = localSessions.find(session => session.id === currentSessionId);

  return (
    <div className={`flex h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Sidebar */}
      <ChatSidebar
        sessions={localSessions}
        currentSessionId={currentSessionId}
        onSelectSession={switchSession}
        onNewSession={createNewSession}
        onDeleteSession={deleteSession}
        onClearAllSessions={clearAllSessions}
        isOpen={isSidebarOpen}
        isSwitchingSession={isSwitchingSession}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        theme={theme}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className={`flex items-center justify-between p-4 border-b ${
          theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        }`}>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 lg:hidden"
            >
              <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>

            <div className="flex items-center gap-3">
              <MessageSquare className="w-6 h-6 text-blue-600" />
              <div>
                <h1 className={`text-lg font-semibold ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>
                  DOSM Population Data Chatbot
                </h1>
                {currentSession && (
                  <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                    {currentSession.title}
                  </p>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className={`w-16 h-16 mb-4 ${theme === 'dark' ? 'text-gray-600' : 'text-gray-400'}`} />
              <h2 className={`text-2xl font-semibold mb-2 ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>
                Welcome to DOSM Population Data Chatbot
              </h2>
              <p className={`text-lg mb-8 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                Ask questions about Malaysia's population data
              </p>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action.query)}
                    className={`p-4 text-left rounded-lg border transition-colors ${
                      theme === 'dark'
                        ? 'bg-gray-800 border-gray-700 hover:bg-gray-700 text-gray-100'
                        : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-900'
                    }`}
                  >
                    <div className="font-medium mb-1">{action.label}</div>
                    <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                      {action.query}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    theme === 'dark' ? 'bg-blue-600' : 'bg-blue-500'
                  }`}>
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-3xl px-4 py-3 rounded-2xl ${
                    message.role === 'user'
                      ? theme === 'dark'
                        ? 'bg-blue-600 text-white'
                        : 'bg-blue-500 text-white'
                      : theme === 'dark'
                        ? 'bg-gray-800 text-gray-100'
                        : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  {renderMessageContent(message)}
                  <div className={`text-xs mt-2 ${
                    message.role === 'user'
                      ? 'text-blue-100'
                      : theme === 'dark'
                        ? 'text-gray-500'
                        : 'text-gray-400'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
                {message.role === 'user' && (
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    theme === 'dark' ? 'bg-gray-600' : 'bg-gray-300'
                  }`}>
                    <User className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                  </div>
                )}
              </div>
            ))
          )}

          {isTyping && (
            <div className="flex gap-3">
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                theme === 'dark' ? 'bg-blue-600' : 'bg-blue-500'
              }`}>
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div
                className={`px-4 py-3 rounded-2xl ${
                  theme === 'dark'
                    ? 'bg-gray-800 text-gray-100'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                  <span className="text-gray-600 dark:text-gray-400">Thinking...</span>
                  <button
                    onClick={cancelRequest}
                    className="ml-2 text-sm text-red-500 hover:text-red-600"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className={`p-4 border-t ${
          theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        }`}>
          {/* Quick Actions - Always Visible */}
          <div className="mb-4">
            <div className="flex flex-wrap gap-2 max-w-4xl mx-auto">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action.query)}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    theme === 'dark'
                      ? 'bg-gray-700 border-gray-600 hover:bg-gray-600 text-gray-100'
                      : 'bg-gray-50 border-gray-200 hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 max-w-4xl mx-auto">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask about Malaysia's population data..."
              className={`flex-1 px-4 py-3 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400'
                  : 'bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500'
              }`}
              rows={1}
              disabled={isTyping}
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isTyping}
              className={`px-4 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                !inputValue.trim() || isTyping
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed dark:bg-gray-600 dark:text-gray-400'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              {isTyping ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Source Panel */}
      <SourcePanel
        sources={selectedSources}
        theme={theme}
        currentMessageId={currentSourceMessageId}
        currentMessageIndex={currentSourceMessageIndex}
        totalMessagesWithSources={messagesWithSources.length}
        onNavigateMessage={navigateMessageSources}
      />
    </div>
  );
}

export default App;