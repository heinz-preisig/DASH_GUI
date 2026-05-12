**2026-04-26**
no not now. I am thinking of making a more complex module, but we do that later. For now we should focus on functionality. We are now building a schema by adding nodes sequentially. It does not have a tree structure. We need to be able to build a tree for example we start with a product which has entries company, properties.
The company has a name, a logo, a address 
-- the address has a street, a house number, a zip code, a town, a coountry

The properties may be many and also grouped in a tree structure like looks, physical properties, or the like.

If you look into my OntoBuild_v1 you can see on how I build an RDF tree there using a similar brick scheme approach.

Let's discuss on how we can extend things to achieve the desired complexity and we do not need to forget that we want to  use DASH to construct an interface that we can consequently use in a browser to enter data using the constructed scheme.