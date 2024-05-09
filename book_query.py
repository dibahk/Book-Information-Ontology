import rdflib

# This simple query grabs all movies with a title and a figure for how much the
# movie grossed at the box office.
query = """
PREFIX ma: <http://www.semanticweb.org/dibah/ontologies/2024/3/untitled-ontology-11#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>  
SELECT DISTINCT ?name ?author
WHERE { ?book rdf:type ma:Book .
        ?book ma:title ?name .
        ?book ma:Author ?author
      }"""


# Create an empty RDF graph and then parse our generated ontology into it.
g = rdflib.Graph()
g.parse("book_advanced.owl", "xml")

print("graph has %s statements.\n" % len(g))

# Don't bbe put off by the weird strings, they're formatting strings that we can
# use in Python to nicely format a table, for example. You can print things 
# however you want.
print ('{0:45s} {1:15s}'.format("Title","Author"))
for x,y in g.query(query):
    print ('{0:45s} {1:15s}'.format(x,y))
