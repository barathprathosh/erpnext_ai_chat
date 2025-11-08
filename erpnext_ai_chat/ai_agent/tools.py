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
def get_sales_orders(customer: Optional[str] = None, status: Optional[str] = None, limit: int = 10, summary: str = "no") -> str:
    """
    Get sales orders with optional filters. Returns data in table format.
    
    Args:
        customer: Filter by customer name (optional)
        status: Filter by order status like 'Draft', 'To Deliver', 'Completed' (optional)
        limit: Maximum number of results to return (default: 10)
        summary: Set to "by_status" to get summary grouped by status with totals (default: "no")
    
    Returns:
        List of sales orders in table format, or summary table grouped by status if summary="by_status"
    """
    try:
        # If summary by status requested
        if summary == "by_status":
            query = """
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(grand_total) as total_amount
                FROM `tabSales Order`
                WHERE docstatus < 2
                {filters}
                GROUP BY status
                ORDER BY count DESC
            """
            
            filter_conditions = []
            if status:
                filter_conditions.append(f"AND status = '{frappe.db.escape(status)}'")
            if customer:
                filter_conditions.append(f"AND customer LIKE '%{frappe.db.escape(customer)}%'")
            
            filter_str = " ".join(filter_conditions) if filter_conditions else ""
            query = query.format(filters=filter_str)
            
            results = frappe.db.sql(query, as_dict=True)
            
            if not results:
                return "No sales orders found"
            
            # Format as table
            result = "Sales Orders by Status:\n\n"
            result += "Status           | Count | Total Amount\n"
            result += "-----------------|-------|------------------\n"
            
            total_count = 0
            total_amount = 0
            
            for row in results:
                status_name = (row.status or "None")[:16].ljust(16)
                count = str(row.count).rjust(5)
                amount = frappe.utils.fmt_money(row.total_amount or 0, currency="USD").rjust(16)
                result += f"{status_name} | {count} | {amount}\n"
                total_count += row.count
                total_amount += (row.total_amount or 0)
            
            result += "-----------------|-------|------------------\n"
            result += f"{'Total'.ljust(16)} | {str(total_count).rjust(5)} | {frappe.utils.fmt_money(total_amount, currency='USD').rjust(16)}\n"
            
            return result
        
        # Otherwise return individual records
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
        
        # Calculate total
        total_amount = sum(order.grand_total for order in orders)
        
        result = f"Sales Orders ({len(orders)} records):\n\n"
        result += "Order ID         | Customer              | Date       | Status        | Amount\n"
        result += "-----------------|----------------------|------------|---------------|------------------\n"
        
        for order in orders:
            order_id = (order.name or "")[:16].ljust(16)
            cust = (order.customer or "")[:20].ljust(20)
            date = str(order.transaction_date or "")[:10].ljust(10)
            stat = (order.status or "")[:13].ljust(13)
            amt = frappe.utils.fmt_money(order.grand_total, currency="USD").rjust(16)
            result += f"{order_id} | {cust} | {date} | {stat} | {amt}\n"
        
        result += "-----------------|----------------------|------------|---------------|------------------\n"
        result += f"{'Total:'.ljust(70)} | {frappe.utils.fmt_money(total_amount, currency='USD').rjust(16)}\n"
        
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


@tool
def get_all_modules() -> str:
    """
    Get list of all available modules in ERPNext/Frappe.
    
    Returns:
        List of all modules with their doctypes
    """
    try:
        modules = frappe.get_all("Module Def", 
                                fields=["name", "module_name", "app_name"],
                                order_by="app_name, module_name")
        
        if not modules:
            return "No modules found"
        
        result = "Available Modules:\n\n"
        current_app = None
        
        for module in modules:
            if current_app != module.app_name:
                current_app = module.app_name
                result += f"\n📦 {current_app.upper()}\n"
                result += "=" * 50 + "\n"
            
            result += f"  • {module.module_name}\n"
        
        result += f"\nTotal: {len(modules)} modules\n"
        return result
    except Exception as e:
        return f"Error fetching modules: {str(e)}"


@tool
def get_doctypes_in_module(module_name: str) -> str:
    """
    Get all doctypes in a specific module.
    
    Args:
        module_name: Name of the module
    
    Returns:
        List of doctypes in the module
    """
    try:
        doctypes = frappe.get_all("DocType",
                                 filters={"module": module_name, "istable": 0},
                                 fields=["name", "is_submittable", "is_tree"],
                                 order_by="name")
        
        if not doctypes:
            return f"No doctypes found in module '{module_name}'"
        
        result = f"DocTypes in '{module_name}' module:\n\n"
        
        for dt in doctypes:
            flags = []
            if dt.is_submittable:
                flags.append("Submittable")
            if dt.is_tree:
                flags.append("Tree")
            
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            result += f"  • {dt.name}{flag_str}\n"
        
        result += f"\nTotal: {len(doctypes)} doctypes\n"
        return result
    except Exception as e:
        return f"Error fetching doctypes: {str(e)}"


@tool
def query_doctype(doctype_name: str, filters: Optional[str] = None, fields: Optional[str] = None, limit: int = 10) -> str:
    """
    Query any doctype with filters and field selection.
    
    Args:
        doctype_name: Name of the doctype to query
        filters: Optional filter string in format: "field=value,field2=value2"
        fields: Optional comma-separated fields to return
        limit: Maximum number of results (default: 10)
    
    Returns:
        Query results from the doctype
    """
    try:
        # Check permission
        if not frappe.has_permission(doctype_name, "read"):
            return f"You don't have permission to access {doctype_name}"
        
        # Parse filters
        filter_dict = {}
        if filters:
            for f in filters.split(","):
                if "=" in f:
                    key, val = f.strip().split("=", 1)
                    filter_dict[key.strip()] = val.strip()
        
        # Parse fields
        field_list = ["name"]
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
            if "name" not in field_list:
                field_list.insert(0, "name")
        else:
            # Get default fields from meta
            meta = frappe.get_meta(doctype_name)
            if meta.title_field and meta.title_field not in field_list:
                field_list.append(meta.title_field)
            
            # Add first 5 fields that are not in table
            for df in meta.fields[:10]:
                if df.fieldtype not in ["Table", "Table MultiSelect", "HTML", "Text Editor", "Code"] and \
                   df.fieldname not in field_list and len(field_list) < 6:
                    field_list.append(df.fieldname)
        
        # Execute query
        docs = frappe.get_all(doctype_name,
                             filters=filter_dict if filter_dict else None,
                             fields=field_list,
                             limit=limit,
                             order_by="modified desc")
        
        if not docs:
            filter_str = f" with filters {filter_dict}" if filter_dict else ""
            return f"No records found in {doctype_name}{filter_str}"
        
        result = f"Found {len(docs)} record(s) in {doctype_name}:\n\n"
        
        for idx, doc in enumerate(docs, 1):
            result += f"{idx}. {doc.name}\n"
            for field in field_list[1:]:  # Skip 'name' as it's already shown
                if field in doc and doc[field]:
                    value = doc[field]
                    # Format value
                    if isinstance(value, (int, float)):
                        if field in ["grand_total", "total", "amount", "outstanding_amount"]:
                            value = frappe.utils.fmt_money(value, currency="USD")
                    result += f"   {field}: {value}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error querying {doctype_name}: {str(e)}"


@tool
def get_reports_list(module_name: Optional[str] = None) -> str:
    """
    Get list of available reports, optionally filtered by module.
    
    Args:
        module_name: Optional module name to filter reports
    
    Returns:
        List of available reports
    """
    try:
        filters = {}
        if module_name:
            filters["module"] = module_name
        
        reports = frappe.get_all("Report",
                                filters=filters,
                                fields=["name", "ref_doctype", "report_type", "module"],
                                order_by="module, name")
        
        if not reports:
            filter_str = f" in module '{module_name}'" if module_name else ""
            return f"No reports found{filter_str}"
        
        result = "Available Reports:\n\n"
        current_module = None
        
        for report in reports:
            if current_module != report.module:
                current_module = report.module
                result += f"\n📊 {current_module}\n"
                result += "-" * 50 + "\n"
            
            result += f"  • {report.name}"
            if report.ref_doctype:
                result += f" (Based on: {report.ref_doctype})"
            result += f" [{report.report_type}]\n"
        
        result += f"\nTotal: {len(reports)} reports\n"
        return result
    except Exception as e:
        return f"Error fetching reports: {str(e)}"


@tool
def get_doctype_structure(doctype_name: str) -> str:
    """
    Get the structure/schema of a doctype including all fields.
    
    Args:
        doctype_name: Name of the doctype
    
    Returns:
        Structure information including fields, links, and properties
    """
    try:
        if not frappe.db.exists("DocType", doctype_name):
            return f"DocType '{doctype_name}' does not exist"
        
        meta = frappe.get_meta(doctype_name)
        
        result = f"DocType Structure: {doctype_name}\n"
        result += "=" * 60 + "\n\n"
        
        result += f"Module: {meta.module}\n"
        result += f"Is Submittable: {'Yes' if meta.is_submittable else 'No'}\n"
        result += f"Is Tree: {'Yes' if meta.is_tree else 'No'}\n"
        result += f"Track Changes: {'Yes' if meta.track_changes else 'No'}\n"
        result += f"Allow Rename: {'Yes' if meta.allow_rename else 'No'}\n\n"
        
        # Fields
        result += "FIELDS:\n"
        result += "-" * 60 + "\n"
        
        for field in meta.fields:
            if field.fieldtype not in ["Section Break", "Column Break", "HTML"]:
                mandatory = " *" if field.reqd else ""
                unique = " [Unique]" if field.unique else ""
                result += f"  • {field.label or field.fieldname}{mandatory}{unique}\n"
                result += f"    Type: {field.fieldtype}"
                if field.options:
                    result += f", Options: {field.options}"
                result += "\n"
        
        result += f"\nTotal Fields: {len([f for f in meta.fields if f.fieldtype not in ['Section Break', 'Column Break', 'HTML']])}\n"
        
        return result
    except Exception as e:
        return f"Error fetching doctype structure: {str(e)}"


@tool
def search_across_doctypes(search_term: str, doctype_list: Optional[str] = None, limit: int = 5) -> str:
    """
    Search for a term across multiple doctypes.
    
    Args:
        search_term: The term to search for
        doctype_list: Optional comma-separated list of doctypes to search in
        limit: Maximum results per doctype (default: 5)
    
    Returns:
        Search results from multiple doctypes
    """
    try:
        # Default doctypes to search
        default_doctypes = [
            "Customer", "Supplier", "Item", "Sales Order", "Purchase Order",
            "Sales Invoice", "Purchase Invoice", "Quotation", "Lead",
            "Opportunity", "Project", "Task", "Issue", "Employee"
        ]
        
        if doctype_list:
            doctypes_to_search = [dt.strip() for dt in doctype_list.split(",")]
        else:
            doctypes_to_search = default_doctypes
        
        result = f"Searching for '{search_term}' across doctypes:\n\n"
        total_results = 0
        
        for doctype in doctypes_to_search:
            try:
                if not frappe.has_permission(doctype, "read"):
                    continue
                
                meta = frappe.get_meta(doctype)
                
                # Build search filters
                search_fields = []
                if meta.search_fields:
                    search_fields = [f.strip() for f in meta.search_fields.split(",")]
                if meta.title_field and meta.title_field not in search_fields:
                    search_fields.append(meta.title_field)
                if not search_fields:
                    search_fields = ["name"]
                
                # Search
                or_filters = []
                for field in search_fields[:3]:  # Limit to first 3 search fields
                    or_filters.append([field, "like", f"%{search_term}%"])
                
                if or_filters:
                    docs = frappe.get_all(doctype,
                                         or_filters=or_filters,
                                         fields=["name"] + search_fields[:2],
                                         limit=limit)
                    
                    if docs:
                        result += f"📄 {doctype} ({len(docs)} found):\n"
                        for doc in docs:
                            result += f"   • {doc.name}\n"
                            for field in search_fields[:2]:
                                if field in doc and field != "name" and doc[field]:
                                    result += f"     {field}: {doc[field]}\n"
                        result += "\n"
                        total_results += len(docs)
            
            except Exception as e:
                continue
        
        if total_results == 0:
            result += f"No results found for '{search_term}'\n"
        else:
            result += f"Total results: {total_results}\n"
        
        return result
    except Exception as e:
        return f"Error searching: {str(e)}"


@tool
def get_doctype_count(doctype_name: str, filters: Optional[str] = None) -> str:
    """
    Get count of documents in a doctype with optional filters.
    
    Args:
        doctype_name: Name of the doctype
        filters: Optional filter string in format: "field=value,field2=value2"
    
    Returns:
        Count of documents
    """
    try:
        if not frappe.has_permission(doctype_name, "read"):
            return f"You don't have permission to access {doctype_name}"
        
        # Parse filters
        filter_dict = {}
        if filters:
            for f in filters.split(","):
                if "=" in f:
                    key, val = f.strip().split("=", 1)
                    filter_dict[key.strip()] = val.strip()
        
        count = frappe.db.count(doctype_name, filters=filter_dict if filter_dict else None)
        
        filter_str = f" with filters {filter_dict}" if filter_dict else ""
        result = f"Count of {doctype_name}{filter_str}: {count:,} record(s)\n"
        
        # Get some stats if possible
        if not filters:
            try:
                # Try to get status breakdown if status field exists
                meta = frappe.get_meta(doctype_name)
                if any(f.fieldname == "status" for f in meta.fields):
                    status_counts = frappe.get_all(doctype_name,
                                                   fields=["status", "count(*) as count"],
                                                   group_by="status",
                                                   order_by="count desc")
                    if status_counts:
                        result += "\nBreakdown by Status:\n"
                        for stat in status_counts:
                            result += f"  • {stat.status or 'None'}: {stat.count:,}\n"
            except:
                pass
        
        return result
    except Exception as e:
        return f"Error counting {doctype_name}: {str(e)}"


def get_erpnext_tools(user=None):
    """
    Get all available tools for the ERPNext agent.
    
    Args:
        user: Current user (for permission checks)
    
    Returns:
        List of LangChain tools
    """
    return [
        # Original tools
        search_customers,
        get_customer_details,
        search_items,
        get_sales_orders,
        get_purchase_orders,
        get_stock_balance,
        search_doctype,
        
        # New comprehensive tools
        get_all_modules,
        get_doctypes_in_module,
        query_doctype,
        get_reports_list,
        get_doctype_structure,
        search_across_doctypes,
        get_doctype_count
    ]
