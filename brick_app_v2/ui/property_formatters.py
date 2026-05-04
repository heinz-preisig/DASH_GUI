"""
Property formatting utilities for displaying property information.
Separates formatting logic from the main GUI for better maintainability.
"""

from typing import Dict, Any, List, Optional


# Constants
MAX_CONSTRAINTS_IN_SUMMARY = 10  # Maximum constraints shown in property list preview


def format_property_display(prop_name: str, prop_data: Any) -> str:
    """Format property information as rich HTML for better readability"""
    if isinstance(prop_data, dict):
        # Check if this is a property brick reference
        if prop_data.get('is_property_brick'):
            return format_property_brick_display(prop_name, prop_data)
        else:
            return format_regular_property_display(prop_name, prop_data)
    elif isinstance(prop_data, str):
        # Handle string prop_data (likely a simple property path)
        return f"""
        <div style="margin: 2px 0;">
            <div style="font-weight: bold; color: #2c3e50;">{prop_name}</div>
            <div style="font-size: 11px; color: #7f8c8d; margin-left: 10px;">📁 {prop_data}</div>
        </div>
        """
    else:
        # Handle other types
        return f"""
        <div style="margin: 2px 0;">
            <div style="font-weight: bold; color: #2c3e50;">{prop_name}</div>
            <div style="font-size: 11px; color: #7f8c8d; margin-left: 10px;">📄 {str(prop_data)}</div>
        </div>
        """


def format_property_brick_display(prop_name: str, prop_data: Dict[str, Any]) -> str:
    """Format property brick reference with enhanced display"""
    property_path = prop_data.get('property_path', '')
    description = prop_data.get('description', '')
    constraints = prop_data.get('constraints', [])
    
    constraint_info = ""
    if constraints:
        constraint_count = len(constraints)
        constraint_info = f'<div style="font-size: 10px; color: #e74c3c; margin-left: 10px;">🔒 {constraint_count} constraint{"s" if constraint_count != 1 else ""}</div>'
    
    description_info = ""
    if description:
        # Truncate long descriptions
        desc_text = description[:50] + "..." if len(description) > 50 else description
        description_info = f'<div style="font-size: 10px; color: #27ae60; margin-left: 10px;">📝 {desc_text}</div>'
    
    return f"""
    <div style="margin: 3px 0; padding: 2px;">
        <div style="font-weight: bold; color: #2980b9;">🧱 {prop_name}</div>
        <div style="font-size: 11px; color: #34495e; margin-left: 10px;">📁 {property_path}</div>
        {description_info}
        {constraint_info}
    </div>
    """


def format_regular_property_display(prop_name: str, prop_data: Dict[str, Any]) -> str:
    """Format regular property with enhanced display"""
    property_path = prop_data.get('path', '')
    datatype = prop_data.get('datatype', '')
    constraints = prop_data.get('constraints', [])
    
    # Build detail lines
    details = []
    
    if property_path:
        details.append(f'<div style="font-size: 11px; color: #7f8c8d; margin-left: 10px;">📁 {property_path}</div>')
    
    if datatype:
        # Show datatype with icon
        datatype_icon = get_datatype_icon(datatype)
        details.append(f'<div style="font-size: 11px; color: #8e44ad; margin-left: 10px;">{datatype_icon} {datatype}</div>')
    
    # Show constraints with better formatting
    if constraints:
        constraint_count = len(constraints)
        constraint_summary = format_constraint_summary(constraints)
        details.append(f'<div style="font-size: 10px; color: #e74c3c; margin-left: 10px;">🔒 {constraint_count} constraint{"s" if constraint_count != 1 else ""}: {constraint_summary}</div>')
    
    details_html = "".join(details)
    
    return f"""
    <div style="margin: 2px 0; padding: 2px;">
        <div style="font-weight: bold; color: #2c3e50;">📋 {prop_name}</div>
        {details_html}
    </div>
    """


def get_datatype_icon(datatype: Any) -> str:
    """Get appropriate icon for datatype"""
    # Handle dict datatype
    if isinstance(datatype, dict):
        datatype_str = datatype.get('value', str(datatype))
    else:
        datatype_str = str(datatype)
    
    datatype_lower = datatype_str.lower()
    if 'string' in datatype_lower:
        return '📝'
    elif 'int' in datatype_lower or 'decimal' in datatype_lower:
        return '🔢'
    elif 'bool' in datatype_lower:
        return '☑️'
    elif 'date' in datatype_lower or 'time' in datatype_lower:
        return '📅'
    elif 'uri' in datatype_lower:
        return '🔗'
    else:
        return '📄'


def format_constraint_summary(constraints: List[Dict[str, Any]]) -> str:
    """Create a concise summary of constraints"""
    if not constraints:
        return ""
    
    constraint_types = []
    for constraint in constraints[:MAX_CONSTRAINTS_IN_SUMMARY]:  # Show max constraints in summary
        constraint_type = constraint.get('constraint_type', 'unknown')
        constraint_value = constraint.get('value', '')
        
        # Format constraint type nicely
        type_mapping = {
            'minLength': 'min len',
            'maxLength': 'max len',
            'minInclusive': 'min',
            'maxInclusive': 'max',
            'minExclusive': 'min excl',
            'maxExclusive': 'max excl',
            'pattern': 'pattern',
            'datatype': 'type'
        }
        
        nice_type = type_mapping.get(constraint_type, constraint_type)
        constraint_types.append(f"{nice_type}={constraint_value}")
    
    if len(constraints) > MAX_CONSTRAINTS_IN_SUMMARY:
        constraint_types.append(f"... ({len(constraints) - MAX_CONSTRAINTS_IN_SUMMARY} more)")
    
    return ", ".join(constraint_types)


def html_to_formatted_text(html_text: str) -> str:
    """Convert HTML to formatted plain text for QListWidget display"""
    import re
    
    # Remove div tags and replace with newlines
    text = re.sub(r'<div[^>]*>', '', html_text)
    text = re.sub(r'</div>', '\n', text)
    
    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up extra whitespace and newlines
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Add indentation for sub-items
            if line.startswith('📁') or line.startswith('📝') or line.startswith('🔒') or line.startswith('🔢'):
                formatted_lines.append('  ' + line)
            else:
                formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def format_property_enhanced_text(prop_name: str, prop_data: Any) -> str:
    """Format property information as enhanced plain text for QListWidget"""
    if isinstance(prop_data, dict):
        # Check if this is a property brick reference
        if prop_data.get('is_property_brick'):
            return format_property_brick_text(prop_name, prop_data)
        else:
            return format_regular_property_text(prop_name, prop_data)
    elif isinstance(prop_data, str):
        # Handle string prop_data (likely a simple property path)
        return f"{prop_name}\n  📁 {prop_data}"
    else:
        # Handle other types
        return f"{prop_name}\n  📄 {str(prop_data)}"


def format_property_brick_text(prop_name: str, prop_data: Dict[str, Any]) -> str:
    """Format property brick reference with enhanced text display"""
    property_path = prop_data.get('property_path', '')
    description = prop_data.get('description', '')
    constraints = prop_data.get('constraints', [])
    
    lines = [f"🧱 {prop_name}"]
    
    if property_path:
        lines.append(f"  📁 {property_path}")
    
    if description:
        # Truncate long descriptions
        desc_text = description[:50] + "..." if len(description) > 50 else description
        lines.append(f"  📝 {desc_text}")
    
    if constraints:
        constraint_count = len(constraints)
        constraint_summary = format_constraint_summary(constraints)
        lines.append(f"  🔒 {constraint_count} constraint{'s' if constraint_count != 1 else ''}: {constraint_summary}")
    
    return "\n".join(lines)


def format_regular_property_text(prop_name: str, prop_data: Dict[str, Any]) -> str:
    """Format regular property with enhanced text display"""
    property_path = prop_data.get('path', '')
    datatype = prop_data.get('datatype', '')
    constraints = prop_data.get('constraints', [])
    
    lines = [f"📋 {prop_name}"]
    
    if property_path:
        lines.append(f"  📁 {property_path}")
    
    if datatype:
        # Show datatype with icon
        # Handle dict datatype
        if isinstance(datatype, dict):
            datatype_str = datatype.get('value', str(datatype))
        else:
            datatype_str = str(datatype)
        datatype_icon = get_datatype_icon(datatype)
        lines.append(f"  {datatype_icon} {datatype_str}")
    
    # Show constraints with better formatting
    if constraints:
        constraint_count = len(constraints)
        constraint_summary = format_constraint_summary(constraints)
        lines.append(f"  🔒 {constraint_count} constraint{'s' if constraint_count != 1 else ''}: {constraint_summary}")
    
    return "\n".join(lines)
