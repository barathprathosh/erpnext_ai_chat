from frappe import _

def get_data():
    return [
        {
            "module_name": "ERPNext AI Chat",
            "color": "#2490ef",
            "icon": "octicon octicon-comment-discussion",
            "type": "module",
            "label": _("AI Chat"),
            "description": _("AI-powered chat assistant for ERPNext")
        }
    ]
