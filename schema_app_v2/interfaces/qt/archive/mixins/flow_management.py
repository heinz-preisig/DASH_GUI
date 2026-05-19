"""Flow management mixin: flow type, edit flow dialog, flow steps refresh."""
from PyQt6.QtWidgets import QMessageBox, QDialog


class FlowManagementMixin:
    """Handles flow configuration within a schema."""

    def on_flow_type_changed(self, flow_type):
        """Handle flow type combo change"""
        if self.current_schema and flow_type:
            try:
                from schema_app_v2.core.flow_engine import FlowType
                flow_enum = FlowType(flow_type)
                self.current_schema.flow_config = self.flow_engine.create_flow(
                    f"Flow for {self.current_schema.name}", flow_enum
                )
                self.current_schema.update_timestamp()
                self.qt_session._emit_event('flow_updated', self.current_schema.flow_config.to_dict())
                self.state_manager.mark_schema_modified()
                self.refresh_flow_steps()
            except ValueError:
                pass

    def edit_flow(self):
        """Open the flow editor dialog"""
        if not self.current_schema:
            QMessageBox.warning(self, "No Schema", "Please create or select a schema first")
            return
        from schema_app_v2.interfaces.qt.flow_editor_dialog import FlowEditorDialog
        dialog = FlowEditorDialog(
            self.flow_engine, self.brick_integration,
            self.current_schema.flow_config, self, self.current_schema
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_schema.flow_config = dialog.current_flow
            self.current_schema.update_timestamp()
            self.qt_session._emit_event('flow_updated', self.current_schema.flow_config.to_dict())
            self.refresh_flow_steps()
            self.update_preview()
            self.ui.statusbar.showMessage("Flow updated successfully")

    def on_flow_step_selection_changed(self):
        """Handle flow step list selection change"""
        pass

    def refresh_flow_steps(self):
        """Rebuild the flow steps list widget"""
        self.ui.flowStepsListWidget.clear()
        if self.current_schema and self.current_schema.flow_config:
            for step in self.current_schema.flow_config.steps:
                self.ui.flowStepsListWidget.addItem(
                    f"{step.name} ({len(step.brick_ids)} bricks)"
                )
