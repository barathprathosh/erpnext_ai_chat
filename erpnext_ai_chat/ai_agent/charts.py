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


def parse_table_to_chart(
    table_text: str,
    chart_type: str = "bar",
    title: str = "Data Chart"
) -> Optional[Dict[str, Any]]:
    """
    Parse a text table and convert to chart data.
    
    Args:
        table_text: Table formatted text with | separators
        chart_type: Type of chart to generate
        title: Chart title
    
    Returns:
        Chart data dictionary or None if parsing fails
    """
    try:
        lines = table_text.strip().split('\n')
        
        # Find header row (contains |)
        header_row = None
        data_rows = []
        
        for line in lines:
            if '|' in line and not line.strip().startswith('-'):
                if header_row is None:
                    header_row = line
                elif not line.lower().startswith('total'):
                    data_rows.append(line)
        
        if not header_row or not data_rows:
            return None
        
        # Parse header
        headers = [h.strip() for h in header_row.split('|')]
        
        # Parse data rows
        labels = []
        datasets = {}
        
        for row in data_rows:
            values = [v.strip() for v in row.split('|')]
            
            if len(values) != len(headers):
                continue
            
            # First column is typically the label
            label = values[0]
            labels.append(label)
            
            # Rest are data values
            for i, header in enumerate(headers[1:], 1):
                if header not in datasets:
                    datasets[header] = {"name": header, "values": []}
                
                # Try to parse numeric value
                try:
                    value_str = values[i].replace('$', '').replace(',', '').strip()
                    value = float(value_str)
                    datasets[header]["values"].append(value)
                except:
                    # If parsing fails, skip this cell
                    datasets[header]["values"].append(0)
        
        # Convert datasets dict to list
        dataset_list = list(datasets.values())
        
        return generate_chart_data(
            chart_type=chart_type,
            title=title,
            labels=labels,
            datasets=dataset_list
        )
        
    except Exception as e:
        frappe.log_error(f"Error parsing table to chart: {str(e)}", "AI Chat Chart")
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
