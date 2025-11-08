import frappe
from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .tools import get_erpnext_tools
from .memory import ConversationMemoryManager


class ERPNextAgent:
    def __init__(self, user=None, session_id=None):
        self.user = user or frappe.session.user
        self.session_id = session_id
        self.memory_manager = ConversationMemoryManager(self.user, self.session_id)
        self.llm = self._initialize_llm()
        self.tools = get_erpnext_tools(self.user)
        
    def _initialize_llm(self):
        """Initialize the LLM with API key from settings or environment"""
        api_key = self._get_api_key()
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=api_key
        )

    def _get_api_key(self):
        """Get OpenAI API key from settings or environment"""
        try:
            settings = frappe.get_single("AI Chat Settings")
            if settings.openai_api_key:
                return settings.openai_api_key
        except:
            pass
        
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            frappe.throw("OpenAI API key not configured. Please set it in AI Chat Settings or OPENAI_API_KEY environment variable.")
        return api_key

    def _get_tools_description(self):
        """Get description of available tools"""
        tools_desc = []
        for tool in self.tools:
            tools_desc.append(f"- {tool.name}: {tool.description}")
        return "\n".join(tools_desc)

    def _execute_tool(self, tool_name, tool_input):
        """Execute a specific tool"""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    return tool.run(tool_input)
                except Exception as e:
                    return f"Error executing tool: {str(e)}"
        return f"Tool {tool_name} not found"
    
    def _execute_tool_with_dict(self, tool_name, tool_input_dict):
        """Execute a tool with dictionary input"""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    # Get the function and call it with unpacked dict
                    return tool.func(**tool_input_dict)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    # Fallback: try as string
                    try:
                        return tool.run(str(tool_input_dict))
                    except:
                        return f"Error executing tool: {str(e)}"
        return f"Tool {tool_name} not found"

    def chat(self, message):
        """Process a chat message and return response"""
        try:
            # Get chat history for context
            chat_history = self.memory_manager.get_messages(limit=10)
            
            # Build system message with tools
            system_msg = f"""You are an intelligent AI assistant for ERPNext, helping user "{self.user}" with their business operations.

You have access to the following tools to query ERPNext data:
{self._get_tools_description()}

IMPORTANT RULES FOR RESPONSES:
1. DO NOT explain your thinking process or what you're about to do
2. DO NOT say "Let me fetch..." or "I will retrieve..." or "To get the data..."
3. DIRECTLY request tools and show results without preamble
4. Present final data in clean, organized formats (tables, lists, or structured text)
5. Be concise and direct - users want data, not explanations of how you'll get it

When you need data:
- Format: TOOL: <tool_name> INPUT: <tool_input>
- I will execute and give you the result
- Then present the final answer in a structured format

DATA FORMATTING GUIDELINES:
- Multiple records: Use tables with columns separated by |
- Single detailed record: Use vertical key-value list
- Summaries: Use bullet points
- Always include totals, counts, and groupings where relevant
- Group by status/category when it makes sense

GOOD response example:
"Sales Orders by Status:

Status      | Count | Total Amount
------------|-------|-------------
Draft       | 5     | $25,000
To Deliver  | 12    | $150,000
Completed   | 8     | $95,000

Total: 25 orders, $270,000"

BAD response example:
"To get the sales orders based on status, I will retrieve them and calculate totals..." ❌

Always respect user permissions and provide accurate information."""

            # Build messages list
            messages = [SystemMessage(content=system_msg)]
            
            # Add recent conversation history
            for msg in chat_history[-5:]:
                messages.append(msg)
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # First LLM call - determine if tools are needed
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Check if LLM wants to use a tool
            if "TOOL:" in response_text and "INPUT:" in response_text:
                # Parse tool request
                import json
                import re
                
                tool_name = None
                tool_input = None
                
                # Extract tool name
                tool_match = re.search(r'TOOL:\s*(\w+)', response_text)
                if tool_match:
                    tool_name = tool_match.group(1).strip()
                
                # Extract input (could be JSON or plain text)
                input_match = re.search(r'INPUT:\s*(.+?)(?:\n|$)', response_text, re.DOTALL)
                if input_match:
                    input_str = input_match.group(1).strip()
                    
                    # Try to parse as JSON if it looks like JSON
                    if input_str.startswith('{') or input_str.startswith('['):
                        try:
                            tool_input = json.loads(input_str)
                        except:
                            tool_input = input_str
                    else:
                        tool_input = input_str
                
                if tool_name and tool_input:
                    # Execute the tool
                    # If tool_input is dict, convert to string arguments for the tool
                    if isinstance(tool_input, dict):
                        # Build argument string from dict
                        # For get_sales_orders, extract relevant params
                        tool_result = self._execute_tool_with_dict(tool_name, tool_input)
                    else:
                        tool_result = self._execute_tool(tool_name, tool_input)
                    
                    # Second LLM call with tool results
                    messages.append(AIMessage(content=response_text))
                    messages.append(HumanMessage(content=f"Tool result:\n{tool_result}\n\nPlease provide your final answer based on this data."))
                    
                    final_response = self.llm.invoke(messages)
                    answer = final_response.content
                else:
                    answer = response_text
            else:
                answer = response_text
            
            # Save to memory
            self.memory_manager.add_message("human", message)
            self.memory_manager.add_message("ai", answer)
            
            return {
                "success": True,
                "message": answer,
                "intermediate_steps": []
            }
            
        except Exception as e:
            frappe.log_error(f"AI Agent Error: {str(e)}", "ERPNext AI Chat")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"I encountered an error: {str(e)}",
                "error": str(e)
            }

    def clear_history(self):
        """Clear conversation history"""
        self.memory_manager.clear()
