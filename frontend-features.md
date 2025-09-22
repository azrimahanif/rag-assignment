# DOSM Population Data Chatbot - Frontend Features

## Overview
A modern React-based chatbot interface for querying Malaysia's Department of Statistics (DOSM) population data with built-in RAG (Retrieval-Augmented Generation) capabilities.

## Core Features

### 🗨️ **Chat Interface**
- **Real-time Messaging**: Interactive chat with AI assistant
- **Message History**: Persistent conversation storage using localStorage
- **Session Management**: Multiple chat sessions with create, switch, and delete functionality
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 📊 **Structured Responses**
- **Smart Analysis**: Automatic parsing of structured data responses
- **Interactive Charts**: QuickChart.io integration for data visualization
- **Multi-format Support**: Handles tables, lists, and structured text
- **Expandable Sections**: Collapsible detailed analysis panels

### 📚 **Source & Citation System**
- **Source Citations**: Automatic source attribution for all responses
- **Three-Column Layout**: Sidebar | Chat | Sources panel structure
- **Source Panel**: Dedicated panel for viewing referenced documents
- **External Links**: Direct access to original data sources
- **Copy & Share**: One-click URL copying and source sharing

### 🎨 **User Experience**
- **ChatGPT-Style Layout**: Full-width message display for optimal readability
- **Theme Switching**: Light, dark, and system theme options
- **Keyboard Shortcuts**: 
  - `Esc` - Close source panel
  - `Ctrl/Cmd + W` - Close source panel
  - `Ctrl/Cmd + K` - Focus input
- **Quick Actions**: Pre-defined population data query buttons
- **Auto-scroll**: Smooth scrolling to latest messages

### 🔧 **Technical Features**
- **TypeScript**: Full type safety throughout the application
- **Responsive Layout**: Mobile-first design with Tailwind CSS
- **Error Handling**: Graceful error recovery and user feedback
- **Performance**: Optimized rendering and state management
- **Accessibility**: Keyboard navigation and screen reader support

### 📱 **Mobile Optimization**
- **Progressive Web App**: Mobile-friendly interface
- **Touch Gestures**: Swipe and tap interactions
- **Bottom Sheet UI**: Mobile-optimized source panel
- **Responsive Sidebar**: Collapsible sidebar for mobile screens

### 🎯 **Data Coverage**
- **Geographic Scope**: Malaysia, Kedah, Selangor
- **Time Range**: Historical data from 1970 to 2025
- **Data Types**: Population statistics, demographics, trends
- **Real-time Updates**: Latest available data from DOSM

### 🛠️ **Development Tools**
- **Hot Reload**: Vite-based development server
- **Build Optimization**: Production-ready builds with tree-shaking
- **Linting**: Code quality and consistency checks
- **Component Library**: Reusable UI components

## User Interface Components

### ChatSidebar
- Session history management
- Theme switching controls
- Search functionality
- Session statistics

### SourcePanel
- Document source display
- Metadata visualization
- Full-text expansion
- Source action buttons

### StructuredResponseComponent
- Data table rendering
- Chart visualization
- Statistical analysis
- Interactive elements

### SourceBadge
- Source count indicator
- Click-to-view functionality
- Visual feedback

## API Integration
- **n8n Webhook**: Real-time communication with backend
- **Streaming Support**: Real-time response streaming
- **Error Recovery**: Automatic retry mechanisms
- **Session Persistence**: Conversation state management

## Performance Features
- **Lazy Loading**: Optimized component loading
- **Image Optimization**: Lazy-loaded chart images
- **Caching**: Local storage for offline access
- **Minification**: Production build optimization

## Future Enhancements
- [ ] Voice input support
- [ ] Advanced filtering options
- [ ] Export functionality (PDF, CSV)
- [ ] Data comparison tools
- [ ] Offline mode support
- [ ] Multi-language support

---

**Built with**: React, TypeScript, Tailwind CSS, Vite  
**Data Source**: DOSM Open Data Portal  
**AI Integration**: Custom RAG system with n8n workflow automation