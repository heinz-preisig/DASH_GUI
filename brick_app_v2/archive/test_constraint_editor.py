#!/usr/bin/env python3
"""
Test the enhanced constraint editor
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui_components import ConstraintEditorDialog

def test_constraint_editor():
    """Test the constraint editor dialog"""
    app = QApplication(sys.argv)
    
    try:
        # Create constraint editor dialog
        dialog = ConstraintEditorDialog()
        
        print("Constraint Editor Dialog created successfully!")
        print("Testing UI components...")
        
        # Check if UI components exist
        assert hasattr(dialog, 'constraintTypeCombo'), "constraintTypeCombo not found"
        assert hasattr(dialog, 'numericValueWidget'), "numericValueWidget not found"
        assert hasattr(dialog, 'patternValueWidget'), "patternValueWidget not found"
        assert hasattr(dialog, 'datatypeValueWidget'), "datatypeValueWidget not found"
        assert hasattr(dialog, 'listValueWidget'), "listValueWidget not found"
        assert hasattr(dialog, 'helpTextLabel'), 'helpTextLabel not found'
        
        print("All UI components found!")
        
        # Test type switching
        dialog.constraintTypeCombo.setCurrentText("minCount")
        dialog.on_type_changed("minCount")
        assert dialog.numericValueWidget.isVisible(), "numericValueWidget should be visible"
        assert not dialog.patternValueWidget.isVisible(), "patternValueWidget should be hidden"
        
        dialog.constraintTypeCombo.setCurrentText("pattern")
        dialog.on_type_changed("pattern")
        assert dialog.patternValueWidget.isVisible(), "patternValueWidget should be visible"
        assert not dialog.numericValueWidget.isVisible(), "numericValueWidget should be hidden"
        
        print("Type switching works correctly!")
        
        # Show dialog for manual testing
        dialog.show()
        print("Dialog shown for manual testing. Close the dialog to exit.")
        
        return app.exec()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_constraint_editor())
