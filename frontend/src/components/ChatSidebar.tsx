import React, { useState, useEffect, useCallback } from 'react';
import { MessageSquare, Settings, Plus, Search, Trash2, Clock } from 'lucide-react';
import { debounce } from '../lib/utils';

interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

interface ChatSidebarProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewSession: () => void;
  onDeleteSession: (sessionId: string) => void;
  onClearAllSessions: () => void;
  isOpen: boolean;
  isSwitchingSession: boolean;
  onToggle: () => void;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onClearAllSessions,
  isOpen,
  isSwitchingSession,
  onToggle
}) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const root = window.document.documentElement;
    const currentTheme = root.className;
    if (currentTheme === 'dark' || currentTheme === 'light') {
      setTheme(currentTheme);
    }
  }, []);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  
  // Debounce search term to prevent rapid filtering
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm]);

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(debouncedSearchTerm.toLowerCase())
  );

  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (date: Date) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  if (!isOpen) {
    // Collapsed sidebar for mobile
    return (
      <div className={`w-16 flex flex-col items-center py-4 space-y-4 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
        <button
          onClick={onToggle}
          className={`p-2 rounded-lg transition-colors ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          title="Open sidebar"
        >
          <MessageSquare className={`w-6 h-6 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`} />
        </button>
      </div>
    );
  }

  return (
    <div className={`w-80 flex flex-col h-full ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
      {/* Header */}
      <div className={`p-4 ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className={`text-lg font-semibold ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>Chats</h2>
          <button
            onClick={onToggle}
            className={`p-2 rounded-lg transition-colors lg:hidden ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            title="Close sidebar"
          >
            <MessageSquare className={`w-5 h-5 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`} />
          </button>
        </div>
        
        <button
          onClick={onNewSession}
          disabled={isSwitchingSession}
          className={`w-full flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            isSwitchingSession
              ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
              : theme === 'dark'
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Search */}
      <div className={`p-4 ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="relative">
          <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`} />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              theme === 'dark'
                ? 'bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400'
                : 'border border-gray-300'
            }`}
          />
        </div>
      </div>

      {/* Chat Sessions */}
      <div className="flex-1 overflow-y-auto">
        {filteredSessions.length === 0 ? (
          <div className="p-4 text-center">
            <MessageSquare className={`w-12 h-12 mx-auto mb-2 ${theme === 'dark' ? 'text-gray-600' : 'text-gray-300'}`} />
            <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>No chat history found</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredSessions.map((session) => (
              <div
                key={session.id}
                className={`group relative px-4 py-3 cursor-pointer transition-colors ${
                  currentSessionId === session.id
                    ? theme === 'dark'
                      ? 'bg-blue-900 border-r-2 border-blue-400'
                      : 'bg-blue-50 border-r-2 border-blue-600'
                    : theme === 'dark'
                      ? 'hover:bg-gray-700'
                      : 'hover:bg-gray-50'
                } ${isSwitchingSession ? 'pointer-events-none opacity-75' : ''}`}
                onClick={() => onSelectSession(session.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className={`text-sm font-medium truncate ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>
                      {session.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                        {formatDate(session.updatedAt)}
                      </span>
                      <span className={`text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>•</span>
                      <span className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                        {formatTime(session.updatedAt)}
                      </span>
                    </div>
                    <p className={`text-xs mt-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                      {session.messageCount} messages
                    </p>
                  </div>
                  
                  {isSwitchingSession && currentSessionId === session.id && (
                    <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    className={`${isSwitchingSession ? 'opacity-0' : 'opacity-0 group-hover:opacity-100'} p-1 rounded transition-all ${theme === 'dark' ? 'hover:bg-red-900' : 'hover:bg-red-50'}`}
                    title="Delete chat"
                    disabled={isSwitchingSession}
                  >
                    <Trash2 className={`w-4 h-4 ${theme === 'dark' ? 'text-red-400' : 'text-red-500'}`} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Settings */}
      <div className={`p-4 border-t border-gray-200`}>
        <div className="flex items-center gap-2 mb-3">
          <Settings className={`w-4 h-4 text-gray-600`} />
          <span className={`text-sm font-medium text-gray-900`}>Settings</span>
        </div>
        
        <div className="flex items-center justify-between text-xs">
            <span className="text-gray-600">Total sessions: {sessions.length}</span>
            <button
              onClick={onClearAllSessions}
              disabled={sessions.length === 0}
              className={`${sessions.length === 0 ? 'text-gray-400 cursor-not-allowed' : 'text-red-600 hover:text-red-700'}`}
            >
              Clear All
            </button>
          </div>
      </div>
    </div>
  );
};