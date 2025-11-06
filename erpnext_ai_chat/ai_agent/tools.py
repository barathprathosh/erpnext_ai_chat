import frappe
from langchain.tools import tool
from typing import List, Dict, Any, Optional


@tool
def search_customers(query: str, limit: int = 10) -> str:
    """
    Search for customers by name or other fields.
    
    Args:
        query: Search term for customer name
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of customers matching the search criteria
    """
    try:
        customers = frappe.get_all(
            "Customer",
            filters=[["customer_name", "like", f"%{query}%"]],
            fields=["name", "customer_name", "customer_type", "customer_group", "territory"],
            limit=limit
        )
        
        if not customers:
            return f"No customers found matching '{query}'"
        
        result = f"Found {len(customers)} customer(s):\n\n"
        for idx, customer in enumerate(customers, 1):
            result += f"{idx}. {customer.customer_name} (ID: {customer.name})\n"
            result += f"   Type: {customer.customer_type}, Group: {customer.customer_group}\n"
        
        return result
    except Exception as e:
        return f"Error searching customers: {str(e)}"


@tool
def get_customer_details(customer_id: str) -> str:
    """
    Get detailed information about a specific customer.
    
    Args:
        customer_id: The customer ID or name
    
    Returns:
        Detailed customer information
    """
    try:
        customer = frappe.get_doc("Customer", customer_id)
        
        result = f"Customer Details for: {customer.customer_name}\n\n"
        result += f"ID: {customer.name}\n"
        result += f"Type: {customer.customer_type}\n"
        result += f"Group: {customer.customer_group}\n"
        result += f"Territory: {customer.territory}\n"
        
        if customer.mobile_no:
            result += f"Mobile: {customer.mobile_no}\n"
        if customer.email_id:
            result += f"Email: {customer.email_id}\n"
        
        outstanding = frappe.get_value(
            "Customer",
            customer_id,
            "outstanding_amount"
        ) or 0
        result += f"\nOutstanding Amount: {frappe.utils.fmt_money(outstanding, currency='USD')}\n"
        
        return result
    except Exception as e:
        return f"Error fetching customer details: {str(e)}"


@tool
def search_items(query: str, limit: int = 10) -> str:
    """
    Search for items/products by name or item code.
    
    Args:
        query: Search term for item name or code
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of items matching the search criteria
    """
    try:
        items = frappe.get_all(
            "Item",
            filters=[
                ["item_name", "like", f"%{query}%"]
            ],
            fields=["name", "item_name", "item_code", "item_group", "stock_uom", "standard_rate"],
            limit=limit,
            or_filters=[
                ["item_code", "like", f"%{query}%"]
            ]
        )
        
        if not items:
            return f"No items found matching '{query}'"
        
        result = f"Found {len(items)} item(s):\n\n"
        for idx, item in enumerate(items, 1):
            result += f"{idx}. {item.item_name} (Code: {item.item_code})\n"
            result += f"   Group: {item.item_group}, UOM: {item.stock_uom}\n"
            if item.standard_rate:
                result += f"   Rate: {frappe.utils.fmt_money(item.standard_rate, currency='USD')}\n"
        
        return result
    except Exception as e:
        return f"Error searching items: {str(e)}"


@tool
def get_sales_orders(customer: Optional[str] = None, status: Optional[str] = None, limit: int = 10) -> str:
    """
    Get sales orders with optional filters.
    
    Args:
        customer: Filter by customer name (optional)
        status: Filter by order status like 'Draft', 'To Deliver', 'Completed' (optional)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of sales orders
    """
    try:
        filters = {}
        if customer:
            filters["customer"] = ["like", f"%{customer}%"]
        if status:
            filters["status"] = status
        
        orders = frappe.get_all(
            "Sales Order",
            filters=filters,
            fields=["name", "customer", "transaction_date", "grand_total", "status", "delivery_status"],
            order_by="transaction_date desc",
            limit=limit
        )
        
        if not orders:
            return "No sales orders found matching the criteria"
        
        result = f"Found {len(orders)} sales order(s):\n\n"
        for idx, order in enumerate(orders, 1):
            result += f"{idx}. SO: {order.name}\n"
            result += f"   Customer: {order.customer}\n"
            result += f"   Date: {order.transaction_date}\n"
            result += f"   Amount: {frappe.utils.fmt_money(order.grand_total, currency='USD')}\n"
            result += f"   Status: {order.status}\n\n"
        
        return result
    except Exception as e:
        return f"Error fetching sales orders: {str(e)}"


@tool
def get_purchase_orders(supplier: Optional[str] = None, status: Optional[str] = None, limit: int = 10) -> str:
    """
    Get purchase orders with optional filters.
    
    Args:
        supplier: Filter by supplier name (optional)
        status: Filter by order status (optional)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of purchase orders
    """
    try:
        filters = {}
        if supplier:
            filters["supplier"] = ["like", f"%{supplier}%"]
        if status:
            filters["status"] = status
        
        orders = frappe.get_all(
            "Purchase Order",
            filters=filters,
            fields=["name", "supplier", "transaction_date", "grand_total", "status"],
            order_by="transaction_date desc",
            limit=limit
        )
        
        if not orders:
            return "No purchase orders found matching the criteria"
        
        result = f"Found {len(orders)} purchase order(s):\n\n"
        for idx, order in enumerate(orders, 1):
            result += f"{idx}. PO: {order.name}\n"
            result += f"   Supplier: {order.supplier}\n"
            result += f"   Date: {order.transaction_date}\n"
            result += f"   Amount: {frappe.utils.fmt_money(order.grand_total, currency='USD')}\n"
            result += f"   Status: {order.status}\n\n"
        
        return result
    except Exception as e:
        return f"Error fetching purchase orders: {str(e)}"


@tool
def get_stock_balance(item_code: str, warehouse: Optional[str] = None) -> str:
    """
    Get stock balance for an item.
    
    Args:
        item_code: Item code to check stock for
        warehouse: Specific warehouse to check (optional, shows all warehouses if not specified)
    
    Returns:
        Stock balance information
    """
    try:
        from erpnext.stock.utils import get_stock_balance
        
        if warehouse:
            balance = get_stock_balance(item_code, warehouse)
            return f"Stock balance for {item_code} in {warehouse}: {balance}"
        else:
            bins = frappe.get_all(
                "Bin",
                filters={"item_code": item_code},
                fields=["warehouse", "actual_qty", "reserved_qty", "projected_qty"]
            )
            
            if not bins:
                return f"No stock found for item: {item_code}"
            
            result = f"Stock balance for {item_code}:\n\n"
            for bin_data in bins:
                result += f"Warehouse: {bin_data.warehouse}\n"
                result += f"  Actual Qty: {bin_data.actual_qty}\n"
                result += f"  Reserved Qty: {bin_data.reserved_qty}\n"
                result += f"  Available Qty: {bin_data.projected_qty}\n\n"
            
            return result
    except Exception as e:
        return f"Error fetching stock balance: {str(e)}"


@tool
def search_doctype(doctype: str, query: str, limit: int = 10) -> str:
    """
    Search for documents in any ERPNext doctype.
    
    Args:
        doctype: The doctype name to search in (e.g., 'Customer', 'Item', 'Sales Order')
        query: Search term
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of matching documents
    """
    try:
        if not frappe.has_permission(doctype, "read"):
            return f"You don't have permission to access {doctype}"
        
        meta = frappe.get_meta(doctype)
        search_field = meta.search_fields.split(",")[0].strip() if meta.search_fields else "name"
        
        filters = [[search_field, "like", f"%{query}%"]]
        
        fields = ["name"]
        if meta.title_field:
            fields.append(meta.title_field)
        if search_field not in fields:
            fields.append(search_field)
        
        docs = frappe.get_all(
            doctype,
            filters=filters,
            fields=fields,
            limit=limit
        )
        
        if not docs:
            return f"No {doctype} documents found matching '{query}'"
        
        result = f"Found {len(docs)} {doctype} document(s):\n\n"
        for idx, doc in enumerate(docs, 1):
            result += f"{idx}. {doc.name}\n"
            for field in fields:
                if field != "name" and doc.get(field):
                    result += f"   {field}: {doc.get(field)}\n"
        
        return result
    except Exception as e:
        return f"Error searching {doctype}: {str(e)}"


def get_erpnext_tools(user=None):
    """
    Get all available tools for the ERPNext agent.
    
    Args:
        user: Current user (for permission checks)
    
    Returns:
        List of LangChain tools
    """
    return [
        search_customers,
        get_customer_details,
        search_items,
        get_sales_orders,
        get_purchase_orders,
        get_stock_balance,
        search_doctype
    ]
