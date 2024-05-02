from SPARQLWrapper import SPARQLWrapper, XML
from rdflib import Graph, URIRef, RDF, RDFS, Literal

# Initialize SPARQLWrapper
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# SPARQL query to construct author data
author_query = """
SELECT DISTINCT ?author ?birthdate ?birthplace ?gender WHERE {
    ?author wdt:P31 wd:Q5 .
    ?author wdt:P569 ?birthdate .
    OPTIONAL { ?author wdt:P19 ?birthplace . }
    OPTIONAL { ?author wdt:P21 ?gender . }
}
"""

# Set SPARQL query and return format
sparql.setQuery(author_query)
sparql.setReturnFormat(XML)

# Execute SPARQL query and convert results to RDF graph
author_data = sparql.query().convert()

# Parse existing ontology file (assuming it's in OWL format)
g = Graph()
g.parse("book_ipynb.owl")

# Namespace declaration for data properties
ma = URIRef("http://www.semanticweb.org/ontologies/ECS735/movie.owl#")

# Iterate through the results and add data properties to the ontology
for result in author_data.bindings:
    author_uri = result["author"].value
    birthdate = result.get("birthdate")
    birthplace = result.get("birthplace")
    gender = result.get("gender")

    if birthdate:
        g.add((URIRef(author_uri), ma.AuthorBirthDate, Literal(birthdate.value)))
    if birthplace:
        g.add((URIRef(author_uri), ma.AuthorBirthPlace, URIRef(birthplace.value)))
    if gender:
        g.add((URIRef(author_uri), ma.AuthorGender, URIRef(gender.value)))

# Serialize the modified graph to OWL format
g.serialize("book_bonus.owl", format="xml")

print("...All done!")
