# ERPNext AI Chat - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the API key (starts with `sk-...`)

### Step 2: Configure in ERPNext

1. Open ERPNext in your browser
2. Go to: **Setup → AI Chat Settings**
3. Paste your OpenAI API Key
4. Click **Save**

### Step 3: Restart Bench

```bash
cd /home/barath/erpnext/develop-bench
bench restart
```

### Step 4: Start Chatting!

1. Look for **"AI Assistant"** button in the navbar
2. Click it to open the chat dialog
3. Type a question like:
   - "Show me pending sales orders"
   - "Search for customer ABC"
   - "What's the stock balance?"

## Example Conversations

### 💼 Customer Management
```
You: Search for customer named Tech Solutions
AI: Found 2 customer(s):
    1. Tech Solutions Inc (ID: CUST-00123)
       Type: Company, Group: Commercial
    2. Tech Solutions Ltd (ID: CUST-00456)
       Type: Company, Group: Corporate
```

### 📦 Inventory Check
```
You: Check stock for ITEM-001
AI: Stock balance for ITEM-001:

    Warehouse: Main Store
      Actual Qty: 150
      Reserved Qty: 25
      Available Qty: 125
    
    Warehouse: Branch Store
      Actual Qty: 50
      Reserved Qty: 10
      Available Qty: 40
```

### 📊 Sales Orders
```
You: Show me sales orders for customer ABC Corp
AI: Found 3 sales order(s):

    1. SO: SO-2024-00123
       Customer: ABC Corp
       Date: 2024-11-01
       Amount: $15,450.00
       Status: To Deliver
    
    2. SO: SO-2024-00145
       Customer: ABC Corp
       Date: 2024-10-28
       Amount: $8,200.00
       Status: Completed
```

## Chat Features

### 🗨️ Multi-turn Conversations
The AI remembers your conversation context:
```
You: Search for customer John
AI: [Shows results for John Doe]

You: Get more details about the first one
AI: [Shows detailed info for John Doe]

You: What are their pending orders?
AI: [Shows John Doe's pending orders]
```

### 📝 Session Management

- **New Chat**: Start fresh conversation
- **Clear History**: Clear current chat
- **Sessions**: View all past conversations

### 🔒 Permission-based Access

The AI only shows data you have permission to view based on your ERPNext role.

## Available Tools

The AI can help with:

| Tool | What it does | Example Query |
|------|-------------|---------------|
| **search_customers** | Find customers by name | "Search for customer ABC" |
| **get_customer_details** | Get detailed customer info | "Show details for CUST-001" |
| **search_items** | Find products/items | "Search for laptop items" |
| **get_sales_orders** | Fetch sales orders | "Show pending sales orders" |
| **get_purchase_orders** | Fetch purchase orders | "Show purchase orders from supplier XYZ" |
| **get_stock_balance** | Check inventory | "What's the stock for ITEM-001?" |
| **search_doctype** | Search any doctype | "Find all draft quotations" |

## Tips for Better Results

✅ **Be specific**: "Show sales orders for customer ABC in last week"
✅ **Use natural language**: "What's in stock?" instead of just "stock"
✅ **Ask follow-up questions**: The AI remembers context
✅ **Mention IDs if known**: "Get details for CUST-00123"

❌ **Avoid very broad queries**: "Show everything" (use limits)
❌ **Don't ask for data you can't access**: Respects permissions

## Troubleshooting

### Chat button not visible?
```bash
bench clear-cache
bench restart
```
Then refresh your browser.

### API Key error?
Make sure you saved the key in **AI Chat Settings** (Setup menu).

### No results returned?
Check that you have permissions to view the data you're asking about.

## Cost Information

The AI uses OpenAI's API which has costs:

- **gpt-4o-mini** (default): ~$0.0001 per message (very cheap!)
- **gpt-4o**: ~$0.01 per message

For typical usage (100 queries/day):
- **gpt-4o-mini**: ~$3/month
- **gpt-4o**: ~$300/month

💡 Tip: Start with gpt-4o-mini, it's perfect for most queries!

## Next Steps

1. ✅ Try the example queries above
2. ✅ Explore your own data with natural language
3. ✅ Check the full [SETUP_GUIDE.md](SETUP_GUIDE.md) for advanced features
4. ✅ Add custom tools for your specific needs

## Need Help?

- 📖 Read the full guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 🔍 Check logs: `bench logs`
- 🐛 Report issues: Check error logs in ERPNext

---

**Enjoy your AI-powered ERPNext! 🎉**
