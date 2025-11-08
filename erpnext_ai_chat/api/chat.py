import frappe
from frappe import _
from erpnext_ai_chat.ai_agent import ERPNextAgent


@frappe.whitelist()
def send_message(message, session_id=None):
    """
    Send a message to the AI agent and get a response.
    
    Args:
        message: User's message
        session_id: Optional session ID to continue a conversation
    
    Returns:
        dict: Response with AI message, session info, and optional chart data
    """
    try:
        if not message:
            frappe.throw(_("Message cannot be empty"))
        
        user = frappe.session.user
        agent = ERPNextAgent(user=user, session_id=session_id)
        
        response = agent.chat(message)
        
        # Check if user requested a chart visualization
        chart_data = None
        if response["success"] and any(keyword in message.lower() for keyword in ['chart', 'graph', 'visualize', 'plot', 'show chart']):
            from erpnext_ai_chat.ai_agent.charts import parse_table_to_chart
            
            response_text = response["message"]
            
            # Determine chart type from message
            chart_type = "bar"  # default
            if "pie" in message.lower():
                chart_type = "pie"
            elif "donut" in message.lower():
                chart_type = "donut"
            elif "line" in message.lower():
                chart_type = "line"
            elif "percentage" in message.lower():
                chart_type = "percentage"
            
            # Extract title from message context
            title = "Data Visualization"
            if "sales" in message.lower():
                title = "Sales Data"
            elif "purchase" in message.lower():
                title = "Purchase Data"
            elif "customer" in message.lower():
                title = "Customer Data"
            elif "employee" in message.lower():
                title = "Employee Data"
            elif "status" in message.lower():
                title = "Status Summary"
            
            chart_data = parse_table_to_chart(response_text, chart_type, title)
        
        return {
            "success": response["success"],
            "response": response["message"],
            "message": response["message"],
            "session_id": agent.session_id,
            "user": user,
            "chart_data": chart_data
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Chat API Error")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "response": f"Error: {str(e)}"
        }


@frappe.whitelist()
def get_chat_history(session_id=None, limit=50):
    """
    Get chat history for a session.
    
    Args:
        session_id: Session ID (optional, uses latest active session if not provided)
        limit: Maximum number of messages to retrieve
    
    Returns:
        list: Chat messages
    """
    try:
        user = frappe.session.user
        
        if not session_id:
            latest_session = frappe.get_all(
                "AI Chat Session",
                filters={"user": user, "is_active": 1},
                order_by="modified desc",
                limit=1
            )
            if not latest_session:
                return []
            session_id = latest_session[0].name
        
        messages = frappe.get_all(
            "AI Chat Message",
            filters={"session": session_id},
            fields=["message_type", "content", "creation"],
            order_by="creation asc",
            limit=limit
        )
        
        return messages
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Chat History Error")
        return []


@frappe.whitelist()
def get_sessions():
    """
    Get all chat sessions for the current user.
    
    Returns:
        list: User's chat sessions
    """
    try:
        user = frappe.session.user
        
        sessions = frappe.get_all(
            "AI Chat Session",
            filters={"user": user},
            fields=["name", "session_name", "creation", "modified", "is_active"],
            order_by="modified desc"
        )
        
        for session in sessions:
            message_count = frappe.db.count(
                "AI Chat Message",
                {"session": session.name}
            )
            session["message_count"] = message_count
        
        return sessions
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Sessions Error")
        return []


@frappe.whitelist()
def create_new_session(session_name=None):
    """
    Create a new chat session.
    
    Args:
        session_name: Optional name for the session
    
    Returns:
        dict: New session details
    """
    try:
        user = frappe.session.user
        
        from datetime import datetime
        if not session_name:
            session_name = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        frappe.db.set_value(
            "AI Chat Session",
            {"user": user, "is_active": 1},
            "is_active",
            0
        )
        
        session = frappe.get_doc({
            "doctype": "AI Chat Session",
            "user": user,
            "session_name": session_name,
            "is_active": 1
        })
        session.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "session_id": session.name,
            "session_name": session.session_name
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Session Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def clear_chat_history(session_id):
    """
    Clear chat history for a session.
    
    Args:
        session_id: Session ID to clear
    
    Returns:
        dict: Success status
    """
    try:
        user = frappe.session.user
        
        session = frappe.get_doc("AI Chat Session", session_id)
        if session.user != user and not frappe.has_permission("AI Chat Session", "write"):
            frappe.throw(_("You don't have permission to clear this session"))
        
        frappe.db.delete("AI Chat Message", {"session": session_id})
        frappe.db.commit()
        
        return {"success": True, "message": "Chat history cleared"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Clear History Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def delete_session(session_id):
    """
    Delete a chat session and all its messages.
    
    Args:
        session_id: Session ID to delete
    
    Returns:
        dict: Success status
    """
    try:
        user = frappe.session.user
        
        session = frappe.get_doc("AI Chat Session", session_id)
        if session.user != user and not frappe.has_permission("AI Chat Session", "delete"):
            frappe.throw(_("You don't have permission to delete this session"))
        
        frappe.db.delete("AI Chat Message", {"session": session_id})
        frappe.delete_doc("AI Chat Session", session_id, ignore_permissions=True)
        frappe.db.commit()
        
        return {"success": True, "message": "Session deleted"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Session Error")
        return {"success": False, "message": str(e)}
