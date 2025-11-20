# ERPNext AI Chat - Project Structure

## Directory Layout

```
erpnext_ai_chat/
├── erpnext_ai_chat/              # Main app module
│   ├── __init__.py               # Version info
│   ├── hooks.py                  # Frappe hooks configuration
│   │
│   ├── ai_agent/                 # AI Agent Core
│   │   ├── __init__.py
│   │   ├── agent.py              # Main ERPNextAgent class
│   │   ├── tools.py              # LangChain tools for ERPNext
│   │   └── memory.py             # Conversation memory manager
│   │
│   ├── api/                      # REST API endpoints
│   │   ├── __init__.py
│   │   └── chat.py               # Chat API methods
│   │
│   ├── config/                   # App configuration
│   │   ├── __init__.py
│   │   └── desktop.py            # Desktop module config
│   │
│   ├── erpnext_ai_chat/          # Module folder
│   │   ├── __init__.py
│   │   └── doctype/              # DocTypes
│   │       ├── ai_chat_settings/     # Settings DocType
│   │       │   ├── __init__.py
│   │       │   ├── ai_chat_settings.json
│   │       │   └── ai_chat_settings.py
│   │       ├── ai_chat_session/      # Session DocType
│   │       │   ├── __init__.py
│   │       │   ├── ai_chat_session.json
│   │       │   └── ai_chat_session.py
│   │       └── ai_chat_message/      # Message DocType
│   │           ├── __init__.py
│   │           ├── ai_chat_message.json
│   │           └── ai_chat_message.py
│   │
│   ├── public/                   # Frontend assets
│   │   ├── js/
│   │   │   └── erpnext_ai_chat.js   # Chat UI and logic
│   │   └── css/
│   │       └── erpnext_ai_chat.css  # Styles
│   │
│   └── templates/                # HTML templates (if needed)
│
├── setup.py                      # Package setup
├── pyproject.toml                # Build configuration
├── requirements.txt              # Python dependencies
├── MANIFEST.in                   # Package manifest
├── README.md                     # Project README
├── SETUP_GUIDE.md                # Detailed setup guide
├── QUICKSTART.md                 # Quick start guide
└── PROJECT_STRUCTURE.md          # This file
```

## Key Files Explained

### 🤖 AI Agent Module

#### `ai_agent/agent.py`
**Purpose:** Core AI agent that orchestrates the conversation flow

**Key Classes:**
- `ERPNextAgent`: Main agent class
  - `__init__()`: Initialize LLM, tools, memory
  - `chat()`: Process user message and return response
  - `_create_agent()`: Set up LangChain agent with tools
  - `_initialize_llm()`: Configure OpenAI model

**Flow:**
```
User Message → chat() → Agent Executor → Tools → LLM → Response
                         ↓
                    Memory Manager
```

#### `ai_agent/tools.py`
**Purpose:** LangChain tools that query ERPNext data

**Available Tools:**
| Tool | Function | Returns |
|------|----------|---------|
| `search_customers()` | Search customers by name | List of customers |
| `get_customer_details()` | Get customer info | Detailed customer data |
| `search_items()` | Search products | List of items |
| `get_sales_orders()` | Fetch sales orders | Sales order list |
| `get_purchase_orders()` | Fetch purchase orders | Purchase order list |
| `get_stock_balance()` | Check inventory | Stock quantities |
| `search_doctype()` | Generic doctype search | Document list |

**Adding a New Tool:**
```python
@tool
def your_new_tool(param: str) -> str:
    """Tool description for the AI"""
    # Your logic here
    return result_string
```

#### `ai_agent/memory.py`
**Purpose:** Manage conversation history and sessions

**Key Classes:**
- `ConversationMemoryManager`: Manages chat memory
  - `add_message()`: Save message to database
  - `get_messages()`: Retrieve chat history
  - `clear()`: Clear conversation
  - `get_session_history()`: Get all user sessions

### 🌐 API Layer

#### `api/chat.py`
**Purpose:** Whitelisted API endpoints for chat functionality

**Endpoints:**

1. **send_message** 
   - Method: `POST`
   - URL: `/api/method/erpnext_ai_chat.api.chat.send_message`
   - Params: `message`, `session_id` (optional)
   - Returns: AI response

2. **get_chat_history**
   - Method: `GET`
   - URL: `/api/method/erpnext_ai_chat.api.chat.get_chat_history`
   - Params: `session_id`, `limit`
   - Returns: List of messages

3. **get_sessions**
   - Method: `GET`
   - URL: `/api/method/erpnext_ai_chat.api.chat.get_sessions`
   - Returns: User's chat sessions

4. **create_new_session**
   - Method: `POST`
   - URL: `/api/method/erpnext_ai_chat.api.chat.create_new_session`
   - Params: `session_name` (optional)
   - Returns: New session ID

5. **clear_chat_history**
   - Method: `POST`
   - URL: `/api/method/erpnext_ai_chat.api.chat.clear_chat_history`
   - Params: `session_id`
   - Returns: Success status

6. **delete_session**
   - Method: `POST`
   - URL: `/api/method/erpnext_ai_chat.api.chat.delete_session`
   - Params: `session_id`
   - Returns: Success status

### 🎨 Frontend

#### `public/js/erpnext_ai_chat.js`
**Purpose:** Chat UI and client-side logic

**Key Functions:**
- `openChat()`: Open chat dialog
- `initChat()`: Initialize chat interface
- `sendMessage()`: Send user message to API
- `addMessage()`: Display message in chat
- `addTypingIndicator()`: Show "AI is typing..."
- `loadChatHistory()`: Load previous messages
- `createNewSession()`: Start new conversation
- `clearHistory()`: Clear chat

**Event Handlers:**
- Click "Send" button
- Press Enter in input
- New Chat button
- Clear History button

#### `public/css/erpnext_ai_chat.css`
**Purpose:** Styling for chat interface

- Message bubble styling
- Typing indicator animation
- Layout and positioning
- Responsive design

### 📊 DocTypes

#### `ai_chat_settings` (Single DocType)
**Fields:**
- `openai_api_key` (Password): OpenAI API key
- `model_name` (Select): GPT model to use
- `temperature` (Float): Randomness (0-1)
- `max_tokens` (Int): Response length limit
- `enable_logging` (Check): Log conversations
- `enable_embeddings` (Check): Enable RAG

#### `ai_chat_session` (Document)
**Fields:**
- `session_name` (Data): Session title
- `user` (Link): User reference
- `is_active` (Check): Active session flag

**Naming:** Auto (AICS-####)

#### `ai_chat_message` (Document)
**Fields:**
- `session` (Link): Parent session
- `message_type` (Select): Human/AI
- `content` (Long Text): Message content
- `user` (Link): User reference

**Naming:** Auto (AICM-#####)

### ⚙️ Configuration

#### `hooks.py`
**Purpose:** Register app with Frappe

**Key Configurations:**
- `app_include_js`: Include JS files
- `app_include_css`: Include CSS files
- `doc_events`: Document event hooks
- `scheduler_events`: Scheduled tasks
- `fixtures`: Initial data

#### `requirements.txt`
**Dependencies:**
```
frappe
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
chromadb>=0.4.22
openai>=1.12.0
tiktoken>=0.5.2
pydantic>=2.0.0
```

## Data Flow

### 1. User Sends Message

```
User Input (Frontend)
    ↓
erpnext_ai_chat.js: sendMessage()
    ↓
API: chat.send_message()
    ↓
ERPNextAgent.chat()
    ↓
LangChain Agent Executor
    ↓
[Tool Selection & Execution]
    ↓
OpenAI GPT-4
    ↓
Response Generation
    ↓
Save to AI Chat Message
    ↓
Return to Frontend
    ↓
Display in Chat UI
```

### 2. Memory Management

```
Message Sent
    ↓
ConversationMemoryManager.add_message()
    ↓
Create AI Chat Message doc
    ↓
Link to AI Chat Session
    ↓
Store in database
    ↓
Available for context in next message
```

### 3. Tool Execution

```
Agent decides to use tool
    ↓
Tool function called (e.g., search_customers)
    ↓
frappe.get_all() query
    ↓
Apply user permissions
    ↓
Format results
    ↓
Return to agent
    ↓
Agent uses in response
```

## Extension Points

### 1. Add New Tools
Location: `ai_agent/tools.py`
```python
@tool
def your_tool(param: str) -> str:
    """Description"""
    # Implementation
    return result
```

### 2. Customize Agent Behavior
Location: `ai_agent/agent.py`
- Modify `system_message` in `_create_agent()`
- Change LLM parameters in `_initialize_llm()`
- Add custom logic in `chat()`

### 3. Add API Endpoints
Location: `api/chat.py`
```python
@frappe.whitelist()
def your_endpoint(param):
    # Implementation
    return result
```

### 4. Extend Frontend
Location: `public/js/erpnext_ai_chat.js`
- Add new UI components
- Implement additional features
- Custom styling in CSS

### 5. Create New DocTypes
Location: `erpnext_ai_chat/doctype/`
- Create folder with JSON and PY files
- Register in hooks.py if needed

## Testing

### Manual Testing
1. Send test messages through UI
2. Check console logs
3. Verify database entries

### API Testing
```python
# In bench console
import frappe

response = frappe.call(
    "erpnext_ai_chat.api.chat.send_message",
    message="Test query"
)
print(response)
```

### Log Files
- Application logs: `develop-bench/logs/`
- Error logs: ERPNext → Error Log doctype

## Performance Considerations

### Optimization Tips
1. **Limit query results** in tools (use `limit` parameter)
2. **Cache frequently accessed data**
3. **Use efficient DocType queries**
4. **Monitor OpenAI API usage**
5. **Implement rate limiting** if needed

### Scalability
- Sessions and messages stored in MariaDB
- Can handle thousands of conversations
- OpenAI API has rate limits (check your tier)
- Consider using Redis for caching

## Security

### Data Access
- All queries respect ERPNext permissions
- Tools use `frappe.get_all()` which applies permission filters
- No direct database access exposed

### API Security
- All endpoints use `@frappe.whitelist()`
- Require active user session
- No authentication bypass

### API Key Storage
- Stored in Password field (encrypted)
- Not exposed in API responses
- Accessed only server-side

## Maintenance

### Regular Tasks
1. Monitor API usage and costs
2. Review chat logs periodically
3. Update dependencies
4. Clear old sessions if needed

### Upgrades
```bash
cd /home/barath/erpnext/develop-bench
git pull  # In app directory
bench migrate
bench restart
```

---

**For more details, see:**
- [QUICKSTART.md](QUICKSTART.md) - Get started quickly
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed guide
- [README.md](README.md) - Overview
