# Constraint Editor Documentation

## Overview

The Constraint Editor is a comprehensive UI component for managing SHACL constraints in the SHACL Brick Editor application. It provides a professional interface for creating, viewing, editing, and deleting constraints on properties within SHACL bricks.

## Architecture

### Component Structure

```
Constraint Editor System
    |
    |-- ConstraintEditorStateController
    |   |-- Manages UI visibility based on constraint type
    |   |-- Handles dynamic label updates
    |   |-- Provides context-sensitive help text
    |
    |-- ConstraintEditorDialog
    |   |-- Loads Qt Designer UI file
    |   -- Uses state controller for UI management
    |   -- Handles constraint CRUD operations
    |
    |-- Constraint Manager (in stateful_gui.py)
    |   -- Property double-click handler
    |   -- Constraint management dialog
    |   -- Integration with brick core for persistence
```

### Files

- **`ui/constraint_editor.ui`** - Qt Designer UI file
- **`gui_components.py`** - State controller and dialog implementation
- **`stateful_gui.py`** - Main GUI integration and constraint management

## Features

### Supported Constraint Types

| Type | Input Widget | Description | Example |
|------|--------------|-------------|---------|
| **minCount** | SpinBox | Minimum number of values required | `1` |
| **maxCount** | SpinBox | Maximum number of values allowed | `5` |
| **minLength** | SpinBox | Minimum string length | `3` |
| **maxLength** | SpinBox | Maximum string length | `50` |
| **pattern** | TextEdit | Regular expression pattern | `^[A-Za-z0-9]+$` |
| **datatype** | ComboBox | Required datatype | `xsd:string` |
| **in** | ListWidget | Allowed values | `["red", "green", "blue"]` |
| **notIn** | ListWidget | Forbidden values | `["admin", "root"]` |

### UI Components

#### Constraint Editor Dialog
- **Type Selection**: Dropdown with 8 constraint types
- **Dynamic Fields**: Context-dependent input widgets
- **Help Text**: Type-specific guidance and examples
- **Action Buttons**: Cancel/OK for confirmation

#### Constraint Manager Dialog
- **Property Info**: Shows property name and path
- **Constraint List**: Displays all constraints with type:value format
- **CRUD Operations**: Add, Edit, Delete buttons
- **Button State Management**: Edit/Delete enabled only when constraint selected

## User Workflows

### Viewing Constraints

1. **Property List Display**: Properties show constraint count (e.g., "2 constraints")
2. **Double-Click Access**: Double-click any property to open constraint manager
3. **Constraint Details**: See all constraints with format "type: value"

### Adding Constraints

#### Method 1: Toolbar Button
1. Select property in property list
2. Click "add constraint" button
3. Configure constraint in editor
4. Click OK to save

#### Method 2: Constraint Manager
1. Double-click property to open manager
2. Click "Add Constraint" button
3. Configure constraint in editor
4. Click OK to save
5. Constraint appears immediately in manager

### Editing Constraints

1. Double-click property to open constraint manager
2. Select constraint in the list
3. Click "Edit Constraint" button
4. Modify constraint in pre-filled editor
5. Click OK to save
6. Updated constraint appears immediately

### Deleting Constraints

1. Double-click property to open constraint manager
2. Select constraint in the list
3. Click "Delete Constraint" button
4. Confirm deletion in dialog
5. Constraint removed immediately

## Technical Implementation

### State Management Pattern

The constraint editor follows the same state management pattern as the main GUI:

```python
class ConstraintEditorStateController:
    def __init__(self, ui_components):
        self.ui = ui_components
        self.current_constraint_type = ""
    
    def set_constraint_type(self, constraint_type):
        self.current_constraint_type = constraint_type
        self.update_visibility()
    
    def update_visibility(self):
        # Hide all widgets first
        # Show appropriate widget based on type
        # Update labels and help text
```

### Data Persistence

All constraint operations persist data through the brick core:

```python
# After any constraint modification
prop_name = prop_data.get('name')
if prop_name:
    self.brick_core.add_property(prop_name, prop_data)
```

### UI Loading

The constraint editor uses Qt Designer UI files:

```python
# Load UI from file
ui_path = Path(__file__).parent / "ui" / "constraint_editor.ui"
from PyQt6.uic import loadUi
loadUi(str(ui_path), self)
```

## Implementation Details

### Dynamic Field Visibility

The state controller manages which input fields are visible based on constraint type:

```python
if constraint_type in ["minCount", "maxCount", "minLength", "maxLength"]:
    self.ui.numericValueWidget.setVisible(True)
    # Update label based on type
elif constraint_type == "pattern":
    self.ui.patternValueWidget.setVisible(True)
# ... etc
```

### List Management

For 'in'/'notIn' constraints:

```python
def add_value_to_list(self):
    value = self.newValueEdit.text().strip()
    if value:
        # Check for duplicates
        for i in range(self.valueListWidget.count()):
            item = self.valueListWidget.item(i)
            if item.text() == value:
                return
        # Add new value
        self.valueListWidget.addItem(value)
```

### Constraint Data Structure

Constraints are stored as dictionaries:

```python
constraint_data = {
    'type': 'minCount',
    'value': '1'
}

# For list constraints
constraint_data = {
    'type': 'in',
    'value': ['red', 'green', 'blue']
}
```

## Integration Points

### Main GUI Integration

The constraint editor integrates with the main GUI through:

1. **Property List**: Shows constraint count in property display
2. **Double-Click Handler**: Opens constraint manager
3. **Toolbar Button**: "add constraint" button functionality
4. **Data Persistence**: Integration with brick core

### Brick Core Integration

All constraint modifications go through the brick core:

```python
self.brick_core.add_property(prop_name, prop_data)
```

This ensures:
- **Data Persistence**: Changes saved to brick's property dictionary
- **JSON Storage**: Constraints saved to and loaded from JSON files
- **Real-time Updates**: Changes reflected immediately in UI

## Testing and Validation

### Test Cases

1. **Add Constraint**: Verify constraint appears in manager and persists
2. **Edit Constraint**: Verify constraint updates correctly
3. **Delete Constraint**: Verify constraint removal with confirmation
4. **Type Switching**: Verify correct fields appear for each type
5. **Data Persistence**: Verify constraints survive save/reload
6. **List Management**: Verify add/remove functionality for list constraints

### Validation

- **Input Validation**: SpinBox ranges, regex patterns, datatype selection
- **Duplicate Prevention**: List constraints prevent duplicate values
- **Confirmation Dialogs**: Delete operations require confirmation
- **Button States**: Edit/Delete buttons enabled only when appropriate

## Future Enhancements

### Potential Improvements

1. **Advanced Validation**: More sophisticated input validation
2. **Constraint Templates**: Pre-defined constraint templates
3. **Import/Export**: Import constraints from external sources
4. **Constraint Preview**: Visual preview of constraint effects
5. **Batch Operations**: Apply constraints to multiple properties

### Extensibility

The architecture supports easy addition of new constraint types:

1. **Add to UI**: Add widget to constraint_editor.ui
2. **Update State Controller**: Add visibility logic
3. **Add Help Text**: Update help text dictionary
4. **Update Data Handling**: Add get/set logic for new type

## Troubleshooting

### Common Issues

1. **Constraints Not Persisting**: Ensure brick core integration is working
2. **Fields Not Visible**: Check state controller visibility logic
3. **UI Not Updating**: Verify signal connections and UI refresh calls
4. **Data Loss**: Ensure proper save/load cycle in brick core

### Debug Points

- **State Controller**: Verify constraint type is set correctly
- **UI Loading**: Verify Qt Designer UI file loads successfully
- **Data Flow**: Verify prop_data updates flow to brick core
- **Signals**: Verify signal connections are working

## Conclusion

The constraint editor provides a comprehensive, user-friendly interface for managing SHACL constraints with robust data persistence and a consistent state management pattern. The architecture supports easy maintenance and future enhancements while following established patterns from the main GUI implementation.
