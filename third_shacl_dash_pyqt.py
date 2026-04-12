import sys
import tkinter as tk  # Only for internal RDFLib reference if needed
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QTextEdit, QCheckBox, QVBoxLayout,
                             QFormLayout, QPushButton, QMessageBox)
from rdflib import Graph, Namespace, RDF, SH, XSD

# 1. Define Namespaces
# Note: Manually defining SH ensures matching with the Turtle string
SH_NS = Namespace("http://w3.org")
DASH = Namespace("http://datashapes.org")
EX = Namespace("http://example.org")

# 2. Sample SHACL Schema (Turtle format)
shacl_data = """
@prefix sh: <http://w3.org> .
@prefix xsd: <http://w3.org> .
@prefix ex: <http://example.org> .
@prefix dash: <http://datashapes.org> .

ex:PersonShape
    a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property [
        sh:path ex:fullName ;
        sh:name "Full Name" ;
        dash:editor dash:TextFieldEditor ;
    ] ;
    sh:property [
        sh:path ex:biography ;
        sh:name "Biography" ;
        dash:editor dash:TextAreaEditor ;
    ] ;
    sh:property [
        sh:path ex:isProgrammer ;
        sh:name "Is Programmer?" ;
        sh:datatype xsd:boolean ;
        dash:editor dash:BooleanFieldEditor ;
    ] .
"""


class SHACLPyQtForm(QWidget):
    def __init__(self, ttl_schema):
        super().__init__()
        self.setWindowTitle("SHACL & DASH Form Generator")
        self.setMinimumWidth(500)

        # Parse the SHACL Graph
        self.g = Graph()
        self.g.parse(data=ttl_schema, format="turtle")

        self.widgets = {}  # Dictionary to store widgets for data retrieval
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        # Set spacing for better visibility
        self.form_layout.setSpacing(15)

        # Find all NodeShapes in the graph
        node_shapes = list(self.g.subjects(RDF.type, SH_NS.NodeShape))

        if not node_shapes:
            error_label = QLabel("Error: No sh:NodeShape found in the schema!")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            main_layout.addWidget(error_label)
        else:
            for shape in node_shapes:
                # Iterate through all properties of the shape
                for prop in self.g.objects(shape, SH_NS.property):
                    self.create_field(prop)

        # Submit Button
        submit_btn = QPushButton("Submit Data")
        submit_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        submit_btn.clicked.connect(self.handle_submit)

        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(submit_btn)
        self.setLayout(main_layout)

    def create_field(self, prop_node):
        # Extract UI hints from SHACL/DASH
        name = self.g.value(prop_node, SH_NS.name)
        editor = self.g.value(prop_node, DASH.editor)
        datatype = self.g.value(prop_node, SH_NS.datatype)

        if not name:
            return

        # Determine which widget to create based on DASH editor or SH datatype
        if editor == DASH.TextAreaEditor:
            widget = QTextEdit()
            widget.setMaximumHeight(100)
        elif editor == DASH.BooleanFieldEditor or datatype == XSD.boolean:
            widget = QCheckBox()
        else:
            # Default to a standard text field
            widget = QLineEdit()

        self.form_layout.addRow(str(name) + ":", widget)
        self.widgets[str(name)] = widget

    def handle_submit(self):
        # Extract values from the generated widgets
        results = []
        for name, widget in self.widgets.items():
            if isinstance(widget, QTextEdit):
                val = widget.toPlainText().strip()
            elif isinstance(widget, QCheckBox):
                val = str(widget.isChecked())
            else:
                val = widget.text().strip()
            results.append(f"<b>{name}:</b> {val}")

        # Display the results in a popup
        msg = QMessageBox(self)
        msg.setWindowTitle("Form Data Collected")
        msg.setText("<br>".join(results))
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Modern styling
    app.setStyle("Fusion")

    form_window = SHACLPyQtForm(shacl_data)
    form_window.show()
    sys.exit(app.exec())
