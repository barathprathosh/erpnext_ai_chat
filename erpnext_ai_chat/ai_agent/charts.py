"""
Chart generation utilities for AI Chat.
Supports multiple chart types: line, bar, pie, donut, percentage, axis-mixed
"""

import frappe
from typing import Dict, List, Any, Optional


def generate_chart_data(
    chart_type: str,
    title: str,
    labels: List[str],
    datasets: List[Dict[str, Any]],
    colors: Optional[List[str]] = None,
    height: int = 300,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate chart data structure for Frappe Charts.
    
    Args:
        chart_type: Type of chart (line, bar, pie, donut, percentage, axis-mixed)
        title: Chart title
        labels: X-axis labels
        datasets: List of dataset dictionaries with 'name' and 'values' keys
        colors: Optional custom colors
        height: Chart height in pixels
        **kwargs: Additional chart-specific options
    
    Returns:
        Dictionary with chart configuration
    """
    chart_data = {
        "type": chart_type,
        "title": title,
        "labels": labels,
        "datasets": datasets,
        "height": height
    }
    
    if colors:
        chart_data["colors"] = colors
    
    # Add chart-specific options
    if "axisOptions" in kwargs:
        chart_data["axisOptions"] = kwargs["axisOptions"]
    if "barOptions" in kwargs:
        chart_data["barOptions"] = kwargs["barOptions"]
    if "lineOptions" in kwargs:
        chart_data["lineOptions"] = kwargs["lineOptions"]
    
    return chart_data


def parse_html_table_to_chart(
    html_text: str,
    chart_type: str = "bar",
    title: str = "Data Chart"
) -> Optional[Dict[str, Any]]:
    """
    Parse an HTML table and convert to chart data.
    
    Args:
        html_text: HTML text containing table
        chart_type: Type of chart to generate
        title: Chart title
    
    Returns:
        Chart data dictionary or None if parsing fails
    """
    try:
        import re
        from html.parser import HTMLParser
        
        # Simple HTML table parser
        class TableParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_table = False
                self.in_thead = False
                self.in_tbody = False
                self.in_tr = False
                self.in_th = False
                self.in_td = False
                self.headers = []
                self.current_row = []
                self.data_rows = []
                self.current_text = ""
                
            def handle_starttag(self, tag, attrs):
                if tag == "table":
                    self.in_table = True
                elif tag == "thead":
                    self.in_thead = True
                elif tag == "tbody":
                    self.in_tbody = True
                elif tag == "tr":
                    self.in_tr = True
                    self.current_row = []
                elif tag == "th":
                    self.in_th = True
                    self.current_text = ""
                elif tag == "td":
                    self.in_td = True
                    self.current_text = ""
                    
            def handle_endtag(self, tag):
                if tag == "table":
                    self.in_table = False
                elif tag == "thead":
                    self.in_thead = False
                elif tag == "tbody":
                    self.in_tbody = False
                elif tag == "tr":
                    self.in_tr = False
                    if self.in_thead and self.current_row:
                        self.headers = self.current_row
                    elif self.in_tbody and self.current_row:
                        # Skip total/summary rows
                        if self.current_row and not str(self.current_row[0]).lower().startswith('total'):
                            self.data_rows.append(self.current_row)
                elif tag == "th":
                    self.in_th = False
                    if self.current_text:
                        self.current_row.append(self.current_text.strip())
                elif tag == "td":
                    self.in_td = False
                    if self.current_text:
                        self.current_row.append(self.current_text.strip())
                        
            def handle_data(self, data):
                if self.in_th or self.in_td:
                    self.current_text += data
        
        parser = TableParser()
        parser.feed(html_text)
        
        if not parser.headers or not parser.data_rows:
            return None
        
        # Build chart data from parsed table
        labels = []
        datasets = {}
        
        for row in parser.data_rows:
            if len(row) < 2:
                continue
                
            # First column is label
            label = row[0]
            labels.append(label)
            
            # Rest are numeric values
            for i in range(1, min(len(row), len(parser.headers))):
                header = parser.headers[i]
                
                if header not in datasets:
                    datasets[header] = {"name": header, "values": []}
                
                # Try to parse numeric value
                try:
                    value_str = row[i]
                    # Remove currency symbols, commas, and whitespace
                    value_str = re.sub(r'[^\d.-]', '', value_str)
                    
                    if value_str:
                        value = float(value_str)
                        datasets[header]["values"].append(value)
                    else:
                        datasets[header]["values"].append(0)
                except Exception:
                    datasets[header]["values"].append(0)
        
        if not labels or not datasets:
            return None
        
        # Convert datasets dict to list
        dataset_list = list(datasets.values())
        
        # For pie/donut charts, use only first dataset
        if chart_type in ["pie", "donut"] and dataset_list:
            dataset_list = [dataset_list[0]]
        
        return generate_chart_data(
            chart_type=chart_type,
            title=title,
            labels=labels,
            datasets=dataset_list
        )
        
    except Exception as e:
        frappe.log_error(f"Error parsing HTML table to chart: {str(e)}\n\nHTML:\n{html_text[:500]}", "AI Chat HTML Chart")
        return None


def parse_table_to_chart(
    table_text: str,
    chart_type: str = "bar",
    title: str = "Data Chart"
) -> Optional[Dict[str, Any]]:
    """
    Parse a text table and convert to chart data.
    Supports both markdown tables and plain text tables.
    
    Args:
        table_text: Table formatted text with | separators
        chart_type: Type of chart to generate
        title: Chart title
    
    Returns:
        Chart data dictionary or None if parsing fails
    """
    try:
        lines = table_text.strip().split('\n')
        
        # Find header row and data rows
        header_row = None
        data_rows = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip separator lines (all dashes and pipes)
            if all(c in '-|= \t' for c in line):
                continue
            
            # Skip lines that say "Total:" at the start
            if line.lower().startswith('total'):
                continue
            
            # Check if line contains pipes (table row)
            if '|' in line:
                # Remove leading/trailing pipes
                line = line.strip('|')
                
                if header_row is None:
                    header_row = line
                else:
                    data_rows.append(line)
        
        if not header_row or not data_rows:
            return None
        
        # Parse header - split by | and clean
        headers = [h.strip() for h in header_row.split('|') if h.strip()]
        
        if len(headers) < 2:
            return None
        
        # Parse data rows
        labels = []
        datasets = {}
        
        for row in data_rows:
            # Split by | and clean
            values = [v.strip() for v in row.split('|') if v.strip()]
            
            # Need at least 2 columns (label + 1 value)
            if len(values) < 2:
                continue
            
            # First column is the label (category)
            label = values[0]
            if label and label not in labels:
                labels.append(label)
            else:
                continue
            
            # Rest are numeric values
            for i in range(1, min(len(values), len(headers))):
                header = headers[i]
                
                if header not in datasets:
                    datasets[header] = {"name": header, "values": []}
                
                # Try to parse numeric value
                try:
                    value_str = values[i]
                    # Remove currency symbols, commas, and whitespace
                    value_str = value_str.replace('$', '').replace('₹', '').replace(',', '').replace(' ', '').strip()
                    
                    # Try to convert to float
                    if value_str:
                        value = float(value_str)
                        datasets[header]["values"].append(value)
                    else:
                        datasets[header]["values"].append(0)
                except Exception as e:
                    # If parsing fails, use 0
                    datasets[header]["values"].append(0)
        
        # Validate we have data
        if not labels or not datasets:
            return None
        
        # Convert datasets dict to list
        dataset_list = list(datasets.values())
        
        # Ensure all datasets have same length as labels
        for dataset in dataset_list:
            while len(dataset["values"]) < len(labels):
                dataset["values"].append(0)
        
        return generate_chart_data(
            chart_type=chart_type,
            title=title,
            labels=labels,
            datasets=dataset_list
        )
        
    except Exception as e:
        frappe.log_error(f"Error parsing table to chart: {str(e)}\n\nTable text:\n{table_text}", "AI Chat Chart")
        return None


def create_sales_by_status_chart(data: List[Dict]) -> Dict[str, Any]:
    """
    Create a bar chart for sales orders grouped by status.
    
    Args:
        data: List of dictionaries with 'status', 'count', and 'total_amount'
    
    Returns:
        Chart data dictionary
    """
    labels = [row.get('status', 'Unknown') for row in data]
    counts = [row.get('count', 0) for row in data]
    amounts = [row.get('total_amount', 0) for row in data]
    
    return generate_chart_data(
        chart_type="bar",
        title="Sales Orders by Status",
        labels=labels,
        datasets=[
            {"name": "Count", "values": counts},
            {"name": "Total Amount", "values": amounts}
        ],
        colors=['#5e64ff', '#ffa00a']
    )


def create_pie_chart(labels: List[str], values: List[float], title: str = "Distribution") -> Dict[str, Any]:
    """
    Create a pie chart.
    
    Args:
        labels: Category labels
        values: Numeric values
        title: Chart title
    
    Returns:
        Chart data dictionary
    """
    return generate_chart_data(
        chart_type="pie",
        title=title,
        labels=labels,
        datasets=[{"values": values}]
    )


def create_donut_chart(labels: List[str], values: List[float], title: str = "Distribution") -> Dict[str, Any]:
    """
    Create a donut chart.
    
    Args:
        labels: Category labels
        values: Numeric values
        title: Chart title
    
    Returns:
        Chart data dictionary
    """
    return generate_chart_data(
        chart_type="donut",
        title=title,
        labels=labels,
        datasets=[{"values": values}]
    )


def create_line_chart(
    labels: List[str],
    datasets: List[Dict[str, Any]],
    title: str = "Trend Over Time"
) -> Dict[str, Any]:
    """
    Create a line chart for trends.
    
    Args:
        labels: X-axis labels (typically dates)
        datasets: List of datasets with 'name' and 'values'
        title: Chart title
    
    Returns:
        Chart data dictionary
    """
    return generate_chart_data(
        chart_type="line",
        title=title,
        labels=labels,
        datasets=datasets,
        lineOptions={"regionFill": 1, "hideDots": 0}
    )


def create_percentage_chart(value: float, title: str = "Progress") -> Dict[str, Any]:
    """
    Create a percentage chart.
    
    Args:
        value: Percentage value (0-100)
        title: Chart title
    
    Returns:
        Chart data dictionary
    """
    return generate_chart_data(
        chart_type="percentage",
        title=title,
        labels=[],
        datasets=[{"values": [value]}]
    )


def create_axis_mixed_chart(
    labels: List[str],
    bar_data: Dict[str, List[float]],
    line_data: Dict[str, List[float]],
    title: str = "Combined Chart"
) -> Dict[str, Any]:
    """
    Create an axis-mixed chart (bar + line).
    
    Args:
        labels: X-axis labels
        bar_data: Dictionary with name and values for bar chart
        line_data: Dictionary with name and values for line chart
        title: Chart title
    
    Returns:
        Chart data dictionary
    """
    datasets = [
        {"name": bar_data["name"], "values": bar_data["values"], "chartType": "bar"},
        {"name": line_data["name"], "values": line_data["values"], "chartType": "line"}
    ]
    
    return generate_chart_data(
        chart_type="axis-mixed",
        title=title,
        labels=labels,
        datasets=datasets
    )
