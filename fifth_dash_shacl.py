< !DOCTYPE
html >
< html >
< head >
< title > SHACL
Browser
Form < / title >
< !-- Using
the
stable
version
of
PyScript -->
< link
rel = "stylesheet"
href = "https://pyscript.net" / >
< script
defer
src = "https://pyscript.net" > < / script >
< py - config >
packages = ["rdflib"]
< / py - config >
< / head >
< body
style = "font-family: sans-serif; padding: 20px; background-color: #f4f4f9;" >

< h2 > SHACL
Browser
Form(DASH
Enhanced) < / h2 >
< div
id = "form-container"
style = "background: white; padding: 20px; border-radius: 8px; max-width: 500px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); min-height: 100px;" >
< p
id = "loading-msg" > Initializing
Python & Downloading
RDFLib... < / p >
< / div >
< button
id = "submit-btn"
style = "margin-top: 20px; padding: 10px 20px; cursor: pointer; display: none;" > Submit
Data < / button >

< py - script >
import js
from pyodide.ffi import create_proxy
from rdflib import Graph, Namespace, RDF, SH

# 1. SHACL Schema
shacl_data = """
        @prefix sh: <http://w3.org> .
        @prefix ex: <http://example.org> .
        @prefix dash: <http://datashapes.org> .
        ex:PersonShape a sh:NodeShape ;
            sh:property [ sh:path ex:fullName ; sh:name "Full Name" ] ;
            sh:property [ sh:path ex:bio ; sh:name "Biography" ; dash:editor dash:TextAreaEditor ] .
        """

# 2. Setup
SH_NS = Namespace("http://w3.org")
DASH = Namespace("http://datashapes.org")
g = Graph().parse(data=shacl_data, format="turtle")

container = js.document.getElementById("form-container")
container.innerHTML = ""
fields = {}

# 3. Build UI
for shape in g.subjects(RDF.type, SH_NS.NodeShape):
    for prop in g.objects(shape, SH_NS.property):
        name = str(g.value(prop, SH_NS.name))
        editor = g.value(prop, DASH.editor)

        lbl = js.document.createElement("label")
        lbl.innerText = f"{name}:"
        lbl.style.display = "block"
        lbl.style.marginTop = "10px"
        container.appendChild(lbl)

        if editor == DASH.TextAreaEditor:
            el = js.document.createElement("textarea")
        else:
            el = js.document.createElement("input")

        el.style.width = "95%"
        container.appendChild(el)
        fields[name] = el

# Show button once ready
btn = js.document.getElementById("submit-btn")
btn.style.display = "block"


def handle_click(event):
    out = "Submitted Data:\\n"
    for n, e in fields.items():
        out += f"{n}: {e.value}\\n"
    js.alert(out)


btn.onclick = create_proxy(handle_click)
< / py - script >
< / body >
< / html >
