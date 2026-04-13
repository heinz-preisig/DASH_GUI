import tkinter as tk
from rdflib import Graph, Namespace, RDF

# Explicitly define namespaces to ensure they match the data EXACTLY
SH = Namespace("http://w3.org")
DASH = Namespace("http://datashapes.org")
EX = Namespace("http://example.org")

shacl_data = """
@prefix sh: <http://w3.org> .
@prefix dash: <http://datashapes.org> .
@prefix ex: <http://example.org> .

ex:PersonShape
    a sh:NodeShape ;
    sh:property [
        sh:path ex:fullName ;
        sh:name "Full Name" ;
        dash:editor dash:TextFieldEditor ;
    ] ;
    sh:property [
        sh:path ex:bio ;
        sh:name "Biography" ;
        dash:editor dash:TextAreaEditor ;
    ] .
"""


class SHACLForm(tk.Tk):
    def __init__(self, ttl_schema):
        super().__init__()
        self.title("SHACL Data Entry")
        self.geometry("500x400")

        # Parse the graph
        self.g = Graph()
        self.g.parse(data=ttl_schema, format="turtle")

        self.widgets = {}
        self.create_ui()

    def create_ui(self):
        container = tk.Frame(self, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        row = 0
        # Look for NodeShapes using the explicit SH namespace
        node_shapes = list(self.g.subjects(RDF.type, SH.NodeShape))

        if not node_shapes:
            tk.Label(container, text="Error: No sh:NodeShape found in data!", fg="red").pack()
            return

        for shape in node_shapes:
            for prop in self.g.objects(shape, SH.property):
                name = self.g.value(prop, SH.name)
                editor = self.g.value(prop, DASH.editor)

                if name:
                    tk.Label(container, text=f"{name}:").grid(row=row, column=0, sticky="w", pady=5)

                    if editor == DASH.TextAreaEditor:
                        widget = tk.Text(container, height=4, width=30, borderwidth=1, relief="solid")
                    else:
                        widget = tk.Entry(container, width=30, borderwidth=1, relief="solid")

                    widget.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
                    self.widgets[str(name)] = widget
                    row += 1

        tk.Button(container, text="Submit", command=self.print_data).grid(row=row, column=1, pady=20)

    def print_data(self):
        for name, widget in self.widgets.items():
            content = widget.get("1.0", tk.END) if isinstance(widget, tk.Text) else widget.get()
            print(f"{name}: {content.strip()}")


if __name__ == "__main__":
    app = SHACLForm(shacl_data)
    app.mainloop()
