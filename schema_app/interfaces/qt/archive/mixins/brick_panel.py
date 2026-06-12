"""Brick panel mixin: brick library, search, selection details."""


class BrickPanelMixin:
    """Handles the brick library panel (left/centre column)."""

    def on_brick_library_changed(self, library_name):
        """Handle brick library combo change"""
        self.refresh_brick_list()
        self.ui.statusbar.showMessage(f"Changed brick library: {library_name}")

    def on_brick_search_changed(self, text):
        """Handle brick search field change"""
        self.refresh_brick_list(search_term=text)

    def on_brick_selection_changed(self):
        """Show details for the selected brick"""
        current_item = self.ui.brickListWidget.currentItem()
        if not current_item:
            self.ui.brickDetailsTextEdit.clear()
            return

        brick_name = current_item.text()
        all_bricks = self.brick_integration.get_available_bricks()
        brick = next((b for b in all_bricks if b.name == brick_name), None)

        if brick:
            details = f"<b>Name:</b> {brick.name}<br>"
            details += f"<b>Type:</b> {brick.object_type}<br>"
            details += f"<b>ID:</b> {brick.brick_id}<br>"
            if hasattr(brick, 'description') and brick.description:
                details += f"<b>Description:</b> {brick.description}<br>"
            if hasattr(brick, 'target_class') and brick.target_class:
                details += f"<b>Target Class:</b> {brick.target_class}<br>"
            if hasattr(brick, 'properties') and brick.properties:
                details += f"<b>Properties ({len(brick.properties)}):</b><br>"
                for name, value in brick.properties.items():
                    details += f"  • {name}: {value}<br>"
            if hasattr(brick, 'constraints') and brick.constraints:
                details += f"<b>Constraints ({len(brick.constraints)}):</b><br>"
                for c in brick.constraints:
                    details += f"  • {c}<br>"
            self.ui.brickDetailsTextEdit.setText(details)
        else:
            self.ui.brickDetailsTextEdit.setText("Brick details not available")

    def refresh_brick_libraries(self):
        """Refresh brick library combo"""
        try:
            libraries = sorted(self.brick_integration.get_brick_libraries())
            self.ui.brickLibraryComboBox.clear()
            self.ui.brickLibraryComboBox.addItems(libraries)
            if libraries:
                self.ui.brickLibraryComboBox.setCurrentIndex(0)
        except Exception as e:
            print(f"Error loading brick libraries: {e}")

    def refresh_brick_list(self, search_term=""):
        """Refresh brick list, optionally filtered by search_term"""
        self.ui.brickListWidget.clear()
        all_bricks = self.brick_integration.get_available_bricks()
        if search_term:
            all_bricks = [b for b in all_bricks if search_term.lower() in b.name.lower()]
        all_bricks = sorted(all_bricks, key=lambda b: b.name.lower())
        for brick in all_bricks:
            self.ui.brickListWidget.addItem(brick.name)
