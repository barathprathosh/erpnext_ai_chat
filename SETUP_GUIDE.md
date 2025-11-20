# ERPNext AI Chat - Complete Setup Guide

## Overview

This is an **Agentic AI Chat System** integrated with Frappe ERPNext that uses:
- **LangChain** for agent orchestration
- **OpenAI GPT-4** as the LLM
- **RAG (Retrieval Augmented Generation)** for context-aware responses
- **Custom tools** to query ERPNext data (Customers, Items, Sales Orders, etc.)

## Features

✅ **Natural Language Queries**
- "Show me pending sales orders"
- "Search for customer ABC Corp"
- "What's the stock balance for item XYZ?"
- "Get details for customer John Doe"

✅ **Multi-turn Conversations** with memory
✅ **Permission-based data access** (respects ERPNext user permissions)
✅ **Real-time chat UI** integrated into ERPNext
✅ **Session management** (create, clear, delete sessions)

## Architecture

```
User Query → Chat UI → API Endpoint → AI Agent → LangChain Tools → ERPNext Data
                                       ↓
                                   OpenAI GPT-4
                                       ↓
                                   Response → UI
```

### Components:

1. **AI Agent** (`ai_agent/agent.py`)
   - Orchestrates conversation flow
   - Manages tools and memory
   - Handles LLM interactions

2. **Tools** (`ai_agent/tools.py`)
   - `search_customers` - Search customers by name
   - `get_customer_details` - Get detailed customer info
   - `search_items` - Search items/products
   - `get_sales_orders` - Fetch sales orders
   - `get_purchase_orders` - Fetch purchase orders
   - `get_stock_balance` - Check stock levels
   - `search_doctype` - Generic doctype search

3. **Memory Manager** (`ai_agent/memory.py`)
   - Stores conversation history in ERPNext
   - Maintains session context

4. **API Endpoints** (`api/chat.py`)
   - `/api/method/erpnext_ai_chat.api.chat.send_message`
   - `/api/method/erpnext_ai_chat.api.chat.get_chat_history`
   - `/api/method/erpnext_ai_chat.api.chat.get_sessions`
   - `/api/method/erpnext_ai_chat.api.chat.create_new_session`
   - `/api/method/erpnext_ai_chat.api.chat.clear_chat_history`

5. **Frontend UI** (`public/js/erpnext_ai_chat.js`)
   - Chat interface with typing indicators
   - Session management
   - Message history

## Installation

### Prerequisites

- ERPNext bench setup
- Python 3.10+
- OpenAI API key

### Steps

1. **The app is already installed!** ✅

2. **Configure OpenAI API Key**

   Option A: Via ERPNext UI (Recommended)
   ```
   1. Go to: Setup → AI Chat Settings
   2. Enter your OpenAI API Key
   3. Save
   ```

   Option B: Environment Variable
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Restart bench**
   ```bash
   cd /home/barath/erpnext/develop-bench
   bench restart
   ```

4. **Access the AI Chat**
   - Open ERPNext in your browser
   - Look for "AI Assistant" button in the navbar
   - Or go to: ERPNext AI Chat module

## Usage

### Basic Chat Queries

**Customer Queries:**
```
- "Search for customer named ABC Corp"
- "Show me details for customer CUST-00001"
- "Find customers in New York"
```

**Item/Product Queries:**
```
- "Search for items containing 'laptop'"
- "Show me all products in Electronics category"
- "What items do we have in stock?"
```

**Sales Order Queries:**
```
- "Show pending sales orders"
- "Get sales orders for customer ABC Corp"
- "Show completed orders from last month"
```

**Stock Queries:**
```
- "Check stock balance for ITEM-001"
- "What's the available quantity for item XYZ?"
- "Show stock in Main Store warehouse"
```

**Generic Queries:**
```
- "Search for suppliers named Tech"
- "Show me recent invoices"
- "Find all draft quotations"
```

### API Usage

**Send a message:**
```python
import frappe

response = frappe.call(
    "erpnext_ai_chat.api.chat.send_message",
    message="Show me pending sales orders",
    session_id=None  # Optional
)

print(response["message"])
```

**Get chat history:**
```python
history = frappe.call(
    "erpnext_ai_chat.api.chat.get_chat_history",
    session_id="AICS-0001"
)

for msg in history:
    print(f"{msg.message_type}: {msg.content}")
```

## DocTypes

### AI Chat Settings
- SingleDocType for configuration
- OpenAI API key
- Model selection (gpt-4o-mini, gpt-4o, etc.)
- Temperature and max tokens

### AI Chat Session
- Stores conversation sessions
- Links to User
- Tracks active sessions

### AI Chat Message
- Individual messages in a session
- Message type (Human/AI)
- Content and timestamp

## Extending the System

### Adding New Tools

Create a new tool in `erpnext_ai_chat/ai_agent/tools.py`:

```python
from langchain.tools import tool

@tool
def get_invoices(status: str = None, limit: int = 10) -> str:
    """
    Get sales invoices with optional status filter.
    
    Args:
        status: Invoice status (e.g., 'Paid', 'Unpaid')
        limit: Maximum results to return
    
    Returns:
        List of invoices
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name", "customer", "grand_total", "status"],
            limit=limit
        )
        
        # Format and return results
        result = f"Found {len(invoices)} invoice(s):\n\n"
        for inv in invoices:
            result += f"- {inv.name}: {inv.customer} - ${inv.grand_total}\n"
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

Then add it to `get_erpnext_tools()` function:

```python
def get_erpnext_tools(user=None):
    return [
        search_customers,
        get_customer_details,
        search_items,
        get_sales_orders,
        get_purchase_orders,
        get_stock_balance,
        search_doctype,
        get_invoices  # Your new tool
    ]
```

### Customizing the Agent Prompt

Edit the system message in `erpnext_ai_chat/ai_agent/agent.py`:

```python
system_message = f"""You are an intelligent AI assistant for ERPNext...

Your capabilities:
- Query ERPNext data
- Provide insights
- Answer questions
- YOUR CUSTOM INSTRUCTIONS HERE

Guidelines:
- YOUR CUSTOM GUIDELINES HERE
"""
```

### Using Different LLMs

To use a different model, update `_initialize_llm()` in `agent.py`:

```python
# Use GPT-4 instead of GPT-4-mini
return ChatOpenAI(
    model="gpt-4o",  # or "gpt-4-turbo"
    temperature=0.7,
    api_key=api_key
)

# Or use Anthropic Claude:
from langchain_anthropic import ChatAnthropic
return ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    anthropic_api_key=api_key
)
```

## RAG Implementation (Future Enhancement)

To add vector embeddings for better context:

1. Install additional packages:
```bash
source env/bin/activate
pip install sentence-transformers faiss-cpu
```

2. Create embeddings of ERPNext data:
```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Embed customer data
customers = frappe.get_all("Customer", fields=["name", "customer_name", "territory"])
texts = [f"{c.customer_name} in {c.territory}" for c in customers]

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(texts, embeddings)

# Use in agent
retriever = vectorstore.as_retriever()
```

## Troubleshooting

### Issue: "OpenAI API key not configured"
**Solution:** Set the API key in AI Chat Settings or via environment variable

### Issue: "No module named langchain"
**Solution:** Reinstall packages:
```bash
cd /home/barath/erpnext/develop-bench
source env/bin/activate
pip install langchain langchain-openai langchain-community chromadb openai tiktoken
```

### Issue: Chat UI not appearing
**Solution:** 
```bash
bench clear-cache
bench restart
```

### Issue: Permission errors when querying data
**Solution:** The agent respects ERPNext permissions. Make sure the user has proper roles and permissions.

## Performance Tips

1. **Limit results** in tools (use `limit` parameter)
2. **Use specific queries** instead of broad searches
3. **Cache frequently accessed data**
4. **Monitor OpenAI API usage** to control costs

## Security Considerations

⚠️ **Important:**
- The agent only accesses data the user has permissions to view
- All queries are logged in AI Chat Session/Message doctypes
- API keys are stored securely in password fields
- Never share your OpenAI API key

## Cost Management

OpenAI API costs depend on:
- Model used (gpt-4o-mini is cheapest)
- Number of messages
- Message length

**Estimated costs:**
- gpt-4o-mini: ~$0.0001 per message
- gpt-4o: ~$0.01 per message

Set limits in OpenAI dashboard to prevent overspending.

## Next Steps

1. ✅ Configure your OpenAI API key
2. ✅ Test basic queries in the chat UI
3. ✅ Add custom tools for your use cases
4. ✅ Train team members on natural language queries
5. ✅ Monitor usage and costs

## Support

For issues or questions:
- Check logs: `bench logs`
- Review error logs in ERPNext: Error Log doctype
- Examine agent behavior with `verbose=True` in agent.py

## License

MIT License - Feel free to modify and extend!

---

**Happy chatting with your ERPNext data! 🚀**
