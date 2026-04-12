import tkinter as tk
from rdflib import Graph, Namespace, SH, RDF

# Define Namespaces
EX = Namespace("http://example.org")
DASH = Namespace("http://datashapes.org")

# 1. Sample SHACL Scheme (Turtle format)
shacl_data = """
@prefix sh: <http://w3.org> .
@prefix xsd: <http://w3.org> .
@prefix ex: <http://example.org> .
@prefix dash: <http://datashapes.org> .

ex:PersonShape
    a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property [
        sh:path ex:firstName ;
        sh:name "First Name" ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        dash:singleLine true ;
    ] ;
    sh:property [
        sh:path ex:age ;
        sh:name "Age" ;
        sh:datatype xsd:integer ;
    ] .
"""


class SHACLForm(tk.Tk):
    def __init__(self, ttl_schema):
        super().__init__()
        self.title("SHACL Generated Form")
        self.g = Graph().parse(data=ttl_schema, format="turtle")
        self.create_widgets()

    def create_widgets(self):
        # Use RDF.type from rdflib, not tk.RDF
        for shape in self.g.subjects(RDF.type, SH.NodeShape):
            # Sort properties by sh:order if available for a better UI layout
            for prop in self.g.objects(shape, SH.property):
                name = self.g.value(prop, SH.name)

                if name:  # Ensure we only create inputs for named properties
                    frame = tk.Frame(self)
                    frame.pack(padx=10, pady=5, fill='x')

                    label = tk.Label(frame, text=f"{name}:", width=15, anchor='w')
                    label.pack(side='left')

                    entry = tk.Entry(frame)
                    entry.pack(side='right', expand=True, fill='x')

                label = tk.Label(frame, text=f"{name}:", width=15, anchor='w')
                label.pack(side='left')

                # Logic: Choose widget based on SHACL/DASH hints
                entry = tk.Entry(frame)
                entry.pack(side='right', expand=True, fill='x')

        btn = tk.Button(self, text="Submit", command=self.submit)
        btn.pack(pady=10)

    def submit(self):
        print("Data submitted (validation logic would go here)")


if __name__ == "__main__":
    app = SHACLForm(shacl_data)
    app.mainloop()
