# ERPNext AI Chat 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ERPNext](https://img.shields.io/badge/ERPNext-15.x-orange.svg)](https://erpnext.com/)

An intelligent AI-powered chat assistant for ERPNext that uses **LangChain** and **OpenAI GPT-4** to help users query and interact with their ERP data using natural language.

## ✨ Features

- 🗣️ **Natural Language Queries** - Ask questions in plain English
- 🔧 **7 Specialized Tools** - Query customers, items, sales orders, purchase orders, stock, and more
- 🧠 **Context-Aware** - Remembers conversation history for multi-turn dialogues
- 🔐 **Permission-Based** - Respects ERPNext user permissions
- 💬 **Real-Time Chat UI** - Integrated directly into ERPNext navbar
- 📊 **Session Management** - Create, save, and manage chat sessions
- 🎯 **Agentic AI** - Automatically selects and executes the right tools

## 🚀 Quick Start

### Prerequisites

- ERPNext 15.x or later
- Python 3.10+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Get the app:**
   ```bash
   cd /path/to/your/bench
   bench get-app https://github.com/barathprathosh/erpnext_ai_chat.git
   ```

2. **Install on your site:**
   ```bash
   bench --site your-site install-app erpnext_ai_chat
   ```

3. **Install dependencies:**
   ```bash
   bench pip install langchain langchain-openai langchain-community chromadb openai tiktoken
   ```

4. **Configure API Key:**
   - Go to: **Setup → AI Chat Settings**
   - Enter your OpenAI API key
   - Click **Save**

5. **Restart bench:**
   ```bash
   bench restart
   ```

6. **Start chatting!**
   - Click the **"AI Assistant"** button in the navbar
   - Ask: "Show me pending sales orders"

## 💡 Example Queries

### Sales & Orders
```
"Show me pending sales orders"
"Get sales orders for customer ABC Corp"
"Find completed orders from last week"
```

### Customer Management
```
"Search for customer Tech Solutions"
"Get details for customer CUST-00001"
"Find all customers in California"
```

### Inventory
```
"Check stock balance for ITEM-001"
"What's the available quantity in Main Warehouse?"
"Show me items with low stock"
```

### Purchases
```
"Show pending purchase orders"
"Get POs from supplier XYZ"
"Find recent purchase orders"
```

## 🛠️ Architecture

```
User Query → Chat UI → API → AI Agent → LangChain → Tools → ERPNext Data
                                  ↓
                            OpenAI GPT-4
                                  ↓
                         Natural Language Response
```

### Components

- **AI Agent** - Orchestrates conversation flow using LangChain
- **7 Specialized Tools** - Query different ERPNext doctypes
- **Memory Manager** - Maintains conversation context
- **REST API** - 6 endpoints for chat operations
- **Chat UI** - Modern interface integrated into ERPNext

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Setup Guide](SETUP_GUIDE.md) - Detailed installation and configuration
- [Project Structure](PROJECT_STRUCTURE.md) - Technical architecture and code organization

## 🔧 Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `search_customers` | Find customers by name | "Search for customer ABC" |
| `get_customer_details` | Get detailed customer info | "Show details for CUST-001" |
| `search_items` | Find products/items | "Search for laptop items" |
| `get_sales_orders` | Fetch sales orders | "Show pending sales orders" |
| `get_purchase_orders` | Fetch purchase orders | "Show purchase orders from supplier X" |
| `get_stock_balance` | Check inventory levels | "Check stock for ITEM-001" |
| `search_doctype` | Generic doctype search | "Find all draft quotations" |

## 🔌 API Endpoints

```python
# Send a message
POST /api/method/erpnext_ai_chat.api.chat.send_message
{
    "message": "Show me pending sales orders",
    "session_id": "optional-session-id"
}

# Get chat history
GET /api/method/erpnext_ai_chat.api.chat.get_chat_history?session_id=AICS-0001

# Get all sessions
GET /api/method/erpnext_ai_chat.api.chat.get_sessions

# Create new session
POST /api/method/erpnext_ai_chat.api.chat.create_new_session

# Clear history
POST /api/method/erpnext_ai_chat.api.chat.clear_chat_history

# Delete session
POST /api/method/erpnext_ai_chat.api.chat.delete_session
```

## 💰 Cost

Uses OpenAI's API with affordable pricing:

| Model | Cost per Query | Recommended For |
|-------|---------------|-----------------|
| gpt-4o-mini (default) | ~$0.0001 | Daily use (very cheap!) |
| gpt-4o | ~$0.01 | Complex queries |

**Example:** 100 queries/day with gpt-4o-mini = ~$3/month

## 🔒 Security

- ✅ Respects ERPNext permissions
- ✅ API key stored encrypted
- ✅ All queries logged
- ✅ No direct database access
- ✅ User-based session isolation

## 🎯 Use Cases

- **Customer Service** - Quickly find customer information
- **Sales Operations** - Monitor orders and pipelines
- **Inventory Management** - Check stock levels instantly
- **Procurement** - Track purchase orders
- **General Queries** - Ask anything about your ERP data

## 🛠️ Extending

### Add a Custom Tool

```python
# In erpnext_ai_chat/ai_agent/tools.py

from langchain.tools import tool
import frappe

@tool
def get_invoices(status: str = None, limit: int = 10) -> str:
    """Get sales invoices with optional status filter"""
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={"status": status} if status else {},
        fields=["name", "customer", "grand_total"],
        limit=limit
    )
    
    result = f"Found {len(invoices)} invoice(s):\n"
    for inv in invoices:
        result += f"- {inv.name}: {inv.customer} (${inv.grand_total})\n"
    
    return result

# Add to get_erpnext_tools() function
def get_erpnext_tools(user=None):
    return [
        # ... existing tools ...
        get_invoices  # Your new tool
    ]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [OpenAI GPT-4](https://openai.com/)
- For [Frappe ERPNext](https://erpnext.com/)

## 📞 Support

- 📖 [Documentation](SETUP_GUIDE.md)
- 🐛 [Issue Tracker](https://github.com/barathprathosh/erpnext_ai_chat/issues)
- 💬 [Discussions](https://github.com/barathprathosh/erpnext_ai_chat/discussions)

## ⭐ Show Your Support

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ for the ERPNext community**
