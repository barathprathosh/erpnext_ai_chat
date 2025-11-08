import frappe

def get_context(context):
    """Context for AI Chat page"""
    context.no_cache = 1
    
    if frappe.session.user == 'Guest':
        frappe.throw("Please login to use AI Chat", frappe.PermissionError)
    
    context.title = "AI Assistant"
    context.show_sidebar = False
    
    return context
