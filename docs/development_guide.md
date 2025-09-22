# Development Guide

This guide provides detailed information for developers working on the RAG Assignment project.

## 🛠️ Development Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Docker (optional)

### Initial Setup

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd RAG-Assignment
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   cd frontend && npm install
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Database Initialization**
   ```bash
   python init_database.py
   python prepare_data.py
   ```

## 📁 Project Structure

### Root Directory
```
RAG-Assignment/
├── frontend/           # React/TypeScript frontend
├── service2/          # Backend services
├── debug/             # Debug utilities and tests
├── docs/              # Documentation
├── data/              # Data files
├── requirements.txt   # Python dependencies
└── README.md         # Project overview
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/    # Reusable React components
│   │   ├── Message.tsx      # Individual message display
│   │   ├── ChatInterface.tsx # Chat interface
│   │   ├── SourcePanel.tsx   # Source management
│   │   ├── SourceBadge.tsx   # Source count badge
│   │   └── LoadingSpinner.tsx # Loading indicator
│   ├── utils/          # Utility functions
│   │   ├── chartRenderer.tsx # Chart processing
│   │   └── responseAnalyzer.ts # Response analysis
│   ├── lib/            # Library functions
│   │   └── utils.ts         # Common utilities
│   ├── hooks/          # Custom React hooks
│   ├── types/          # TypeScript type definitions
│   └── App.tsx         # Main application component
├── public/             # Static assets
└── package.json        # Node.js dependencies
```

### Backend Structure
```
service2/
├── fastapi/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── models/    # Database models
│   │   ├── services/  # Business logic
│   │   ├── core/      # Core configuration
│   │   └── main.py    # Application entry point
├── evaluation/        # Testing framework
└── docker-compose.yml # Service orchestration
```

## 🎯 Core Components

### Frontend Components

#### App.tsx
- **Purpose**: Main application component with state management
- **Key Features**:
  - Message handling and display
  - Chart URL processing and conversion
  - Download functionality setup
  - Session management
- **Key Hooks**: `useState`, `useEffect`, `useCallback`

#### ChatInterface.tsx
- **Purpose**: Chat message display and input handling
- **Key Features**:
  - Message list with scrolling
  - Input form with validation
  - Quick action buttons
  - Typing indicators
- **State**: Local UI state, user input

#### SourcePanel.tsx
- **Purpose**: Display and manage data sources
- **Key Features**:
  - Source filtering and sorting
  - Copy to clipboard functionality
  - Responsive layout
  - Keyboard navigation
- **Props**: `sources`, `isOpen`, `onClose`

#### chartRenderer.tsx
- **Purpose**: Process and render chart URLs
- **Key Features**:
  - URL detection and normalization
  - JSON extraction from responses
  - Chart component generation
  - Error handling for invalid charts

### Backend Services

#### Chat Service
- **Purpose**: Handle chat message processing
- **Key Features**:
  - Message storage and retrieval
  - Session management
  - Integration with RAG system
- **API Endpoints**: `/api/v1/chat/message`, `/api/v1/chat/history`

#### RAG Service
- **Purpose**: Retrieval-augmented generation
- **Key Features**:
  - Vector database operations
  - OpenAI API integration
  - Response generation with sources
- **Dependencies**: Qdrant, OpenAI, population data

#### Data Service
- **Purpose**: Population data management
- **Key Features**:
  - Data preprocessing and validation
  - Vector embeddings generation
  - Search and filtering
- **Data Sources**: DOSM APIs, Parquet files

## 🔄 Development Workflow

### Local Development

1. **Start Backend Services**
   ```bash
   # Terminal 1: FastAPI backend
   cd service2/fastapi
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend Development**
   ```bash
   # Terminal 2: React frontend
   cd frontend
   npm run dev
   ```

3. **Start Vector Database** (if not using Docker)
   ```bash
   # Terminal 3: Qdrant
   docker run -p 6333:6333 qdrant/qdrant
   ```

### Testing Workflow

1. **Unit Tests**
   ```bash
   # Frontend tests
   cd frontend
   npm test

   # Backend tests
   cd service2
   pytest tests/
   ```

2. **Integration Tests**
   ```bash
   # Chat functionality
   python debug/test_chat_storage.py

   # Chart processing
   python debug/test_chart_fix.py

   # Database operations
   python debug/debug_db.py
   ```

3. **End-to-End Tests**
   ```bash
   # Full system test
   python debug/test_real_ai_example.py
   ```

### Code Quality Checks

1. **Linting**
   ```bash
   # Frontend
   cd frontend
   npm run lint

   # Backend
   cd service2
   flake8 app/
   black app/
   mypy app/
   ```

2. **Type Checking**
   ```bash
   # Frontend
   cd frontend
   npx tsc --noEmit

   # Backend
   mypy app/
   ```

## 🎨 Styling and UI Guidelines

### Design System

#### Colors
- **Primary**: Blue (`#3B82F6`)
- **Secondary**: Gray (`#6B7280`)
- **Success**: Green (`#10B981`)
- **Error**: Red (`#EF4444`)
- **Warning**: Yellow (`#F59E0B`)

#### Typography
- **Font Family**: Inter, system-ui, sans-serif
- **Font Sizes**: 12px (small), 14px (base), 16px (large), 20px (xl)
- **Font Weights**: 400 (normal), 500 (medium), 600 (semibold)

#### Spacing
- **Unit**: 0.25rem (4px)
- **Scale**: 1, 2, 3, 4, 6, 8 units
- **Usage**: Consistent padding/margin with Tailwind classes

### Component Patterns

#### Buttons
```tsx
<button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
  Button Text
</button>
```

#### Input Fields
```tsx
<input
  type="text"
  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
  placeholder="Enter text..."
/>
```

#### Cards
```tsx
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
  <h3 className="text-lg font-medium text-gray-900 mb-2">Card Title</h3>
  <p className="text-gray-600">Card content goes here.</p>
</div>
```

## 🔧 Configuration Management

### Environment Variables

#### Required Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Database Configuration
DATABASE_URL=sqlite:///./rag_app.db
QDRANT_URL=http://localhost:6333

# Service Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

#### Optional Variables
```bash
# Development Flags
NODE_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# External Services
DOSM_API_URL=https://api.dosm.gov.my
QUICKCHART_URL=https://quickchart.io
```

### Configuration Files

#### Frontend Configuration
- `vite.config.ts`: Build and development configuration
- `tailwind.config.ts`: Tailwind CSS configuration
- `tsconfig.json`: TypeScript configuration

#### Backend Configuration
- `app/core/config.py`: Application configuration
- `docker-compose.yml`: Service orchestration
- `requirements.txt`: Python dependencies

## 🚀 Performance Optimization

### Frontend Optimization

#### Code Splitting
```tsx
// Lazy load components
const SourcePanel = React.lazy(() => import('./components/SourcePanel'));
const ChartRenderer = React.lazy(() => import('./utils/chartRenderer'));
```

#### Image Optimization
```tsx
// Optimize chart images
<img
  src={chartUrl}
  alt={title}
  loading="lazy"
  className="max-w-full h-auto"
/>
```

#### Caching Strategy
```tsx
// Memoize expensive operations
const processedMessages = useMemo(() => {
  return messages.map(processMessage);
}, [messages]);
```

### Backend Optimization

#### Database Optimization
```python
# Use connection pooling
DATABASE_URL = "sqlite+aiosqlite:///./rag_app.db?pool_size=5&max_overflow=10"

# Optimize queries with indexes
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
```

#### API Optimization
```python
# Implement response caching
from fastapi_cache import FastAPICache, Coder

@cached(expire=60)
async def get_chat_history(session_id: str):
    return await get_messages_by_session(session_id)
```

## 🐛 Debugging and Troubleshooting

### Common Development Issues

#### Frontend Issues
- **Hot reload not working**: Check Vite configuration and file watcher limits
- **CSS not updating**: Clear browser cache and restart dev server
- **TypeScript errors**: Update type definitions and check imports

#### Backend Issues
- **Database connection errors**: Verify database file permissions and URL
- **API timeout**: Increase timeout settings or optimize database queries
- **Import errors**: Check Python path and virtual environment activation

### Debug Tools

#### Frontend Debugging
```bash
# React Developer Tools
# Browser console for errors
# Network tab for API calls
```

#### Backend Debugging
```bash
# Python debugger
import pdb; pdb.set_trace()

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Profile performance
import cProfile
cProfile.run('function_to_profile()')
```

### Performance Profiling

#### Frontend Profiling
```tsx
// React Profiler
<React.Profiler id="ChatInterface" onRender={(id, phase, actualTime) => {
  console.log(`${id} ${phase} took ${actualTime} ms`);
}}>
  <ChatInterface />
</React.Profiler>
```

#### Backend Profiling
```python
# Time function execution
import time
from functools import wraps

def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper
```

## 📝 Documentation Standards

### Code Documentation

#### Python Docstrings
```python
def process_chat_message(message: str, session_id: str) -> dict:
    """
    Process a chat message and generate response with sources.

    Args:
        message: User message text
        session_id: Chat session identifier

    Returns:
        Dictionary containing response and sources

    Raises:
        ValueError: If message is empty or invalid
    """
    pass
```

#### TypeScript Comments
```tsx
/**
 * Chat interface component for displaying and sending messages
 * @param {Object} props - Component props
 * @param {Message[]} props.messages - Array of chat messages
 * @param {Function} props.onSendMessage - Callback for sending messages
 */
interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
}
```

### README Standards

#### Component README
Each major component should have:
- Purpose and functionality description
- Props/interface documentation
- Usage examples
- Testing instructions
- Performance considerations

## 🔄 Testing Guidelines

### Frontend Testing

#### Unit Testing with React Testing Library
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from './ChatInterface';

test('sends message when form is submitted', () => {
  const mockSendMessage = jest.fn();
  render(<ChatInterface onSendMessage={mockSendMessage} />);

  fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
    target: { value: 'Hello' }
  });
  fireEvent.click(screen.getByText('Send'));

  expect(mockSendMessage).toHaveBeenCalledWith('Hello');
});
```

#### Integration Testing
```tsx
test('full chat flow works correctly', async () => {
  render(<App />);

  // Send message
  fireEvent.change(screen.getByPlaceholderText('Type your message...'), {
    target: { value: 'What is Malaysia population?' }
  });
  fireEvent.click(screen.getByText('Send'));

  // Wait for response
  await waitFor(() => {
    expect(screen.getByText(/Malaysia/)).toBeInTheDocument();
  });
});
```

### Backend Testing

#### Unit Testing with Pytest
```python
import pytest
from app.services.chat_service import ChatService

@pytest.fixture
def chat_service():
    return ChatService()

def test_process_message(chat_service):
    result = chat_service.process_message("Hello")
    assert isinstance(result, dict)
    assert "response" in result
    assert "sources" in result
```

#### Integration Testing
```python
def test_full_chat_flow(client):
    # Send message
    response = client.post("/api/v1/chat/message", json={
        "message": "What is Malaysia population?"
    })
    assert response.status_code == 200

    # Get history
    session_id = response.json()["session_id"]
    history_response = client.get(f"/api/v1/chat/history/{session_id}")
    assert len(history_response.json()["messages"]) == 2
```

## 🚀 Deployment Guidelines

### Build Process

#### Frontend Build
```bash
cd frontend
npm run build
# Creates dist/ folder with optimized production build
```

#### Backend Build
```bash
cd service2
docker build -t rag-backend .
# Creates optimized Docker image
```

### Environment-Specific Configurations

#### Development
- Hot reload enabled
- Debug logging
- Local databases
- Source maps included

#### Production
- Optimized builds
- Structured logging
- Production databases
- Error monitoring
- Security headers

### Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static assets built and optimized
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Monitoring and logging configured
- [ ] Backup and recovery procedures tested

---

This development guide provides comprehensive information for contributing to the RAG Assignment project. For additional questions or clarification, please refer to the project documentation or create an issue in the repository.