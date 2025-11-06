import frappe
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
import json


class ConversationMemoryManager:
    """Manages conversation memory for AI chat sessions"""
    
    def __init__(self, user, session_id=None):
        self.user = user
        self.session_id = session_id or self._get_or_create_session()
        
    def _get_or_create_session(self):
        """Get existing active session or create new one"""
        existing_session = frappe.get_all(
            "AI Chat Session",
            filters={
                "user": self.user,
                "is_active": 1
            },
            order_by="modified desc",
            limit=1
        )
        
        if existing_session:
            return existing_session[0].name
        
        session = frappe.get_doc({
            "doctype": "AI Chat Session",
            "user": self.user,
            "session_name": f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "is_active": 1
        })
        session.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return session.name
    
    def add_message(self, message_type, content):
        """Add a message to the conversation history"""
        message = frappe.get_doc({
            "doctype": "AI Chat Message",
            "session": self.session_id,
            "message_type": message_type.capitalize(),
            "content": content,
            "user": self.user
        })
        message.insert(ignore_permissions=True)
        frappe.db.commit()
    
    def get_messages(self, limit=20):
        """Retrieve conversation history"""
        messages = frappe.get_all(
            "AI Chat Message",
            filters={"session": self.session_id},
            fields=["message_type", "content"],
            order_by="creation asc",
            limit=limit
        )
        
        langchain_messages = []
        for msg in messages:
            if msg.message_type == "Human":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.message_type == "Ai":
                langchain_messages.append(AIMessage(content=msg.content))
        
        return langchain_messages
    
    def clear(self):
        """Clear conversation history"""
        frappe.db.delete("AI Chat Message", {"session": self.session_id})
        frappe.db.commit()
    
    def get_session_history(self):
        """Get all sessions for the user"""
        sessions = frappe.get_all(
            "AI Chat Session",
            filters={"user": self.user},
            fields=["name", "session_name", "creation", "modified", "is_active"],
            order_by="modified desc"
        )
        return sessions
