import rdflib
from rdflib.namespace import RDF
from rdflib.graph import Graph, URIRef
from SPARQLWrapper import SPARQLWrapper, XML

# Configuring the end-point and constructing query.
# Notice the various SPARQL constructs we are making use of:
#
#   * PREFIX to bind prefixes in our query
#   * CONSTRUCT to build new individuals from our query
#   * OPTIONAL to indicate that some fields may not exist and that's OK
#   * FILTER to constrain our query in some way
#

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
construct_query="""PREFIX ma: <http://www.semanticweb.org/dibah/ontologies/2024/3/untitled-ontology-11#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>        
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    PREFIX dbpprop: <http://dbpedia.org/property/>
    PREFIX dbp: <http://dbpedia.org/property/>

    CONSTRUCT {
    ?book rdf:type ma:Book .
    ?book rdfs:label ?name .
    ?book ma:title ?name .
    ?book ma:written_by ?author .
    ?author rdf:type ma:Author .
    ?author rdfs:label ?Nauthor .
    ?book ma:published_by ?publisher .
    ?publisher rdf:type ma:publisher .
    ?book ma:has_genre ?genre .
    ?genre rdf:type ma:literaryGenre .
    ?book ma:cover_designed_by ?coverArtist .
    ?coverArtist rdf:type ma:coverArtist .
    ?coverArtist rdfs:label ?NcoverArtist .
    ?book ma:numberOfPages ?numberOfPages .
    ?book ma:isbn ?isbn .
    ?book ma:releaseDate ?releaseDate .
    ?book ma:has_publish_country ?country .
    ?country rdf:type ma:Country .
    ?book ma:has_language ?lang .
    ?lang rdf:type ma:Language .
    ?book ma:has_character ?Character .
    ?Character rdf:type ma:Character .        
    
    }
    WHERE{
        ?book rdf:type dbpedia-owl:Book .

        ?book dbp:name ?name .
        FILTER(!REGEX(?name, "Book", "i"))
        ?book dbpedia-owl:author ?author .
        ?author dbp:birthName ?Nauthor .
        OPTIONAL {?book dbpedia-owl:genre ?genre}
        OPTIONAL {?book dbpedia-owl:publisher ?publisher}
        OPTIONAL {?book dbpedia-owl:coverArtist ?coverArtist .
        ?coverArtist dbp:name ?NcoverArtist}
        OPTIONAL {?book dbpedia-owl:numberOfPages ?numberOfPages}
        ?book dbpedia-owl:isbn ?isbn .
        FILTER(?isbn != "") . # Ensure ISBN is not an empty string
        ?book dbp:releaseDate ?releaseDate .
        OPTIONAL {?book dbpedia-owl:country ?country}
        OPTIONAL {?book dbpedia-owl:language ?lang}
        OPTIONAL {?book dbpedia-owl:Character ?Character}

        FILTER(?country != ?lang) # Ensure country and language are different
        FILTER(LANG(?name)='en')
        }
    LIMIT 1000
    """

sparql.setQuery(construct_query)
sparql.setReturnFormat(XML)

# Creating the RDF store and graph
# We've seen something similar in the lab sheets before, Week 3. We're telling
# the rdflib library to create a new graph and store it in memory (so, temporarily).

graph_id = URIRef("http://www.semanticweb.org/store/book")
g = Graph(identifier = graph_id)

# SPARQL queries can take some time to run, especially if the query is particularly
# large and you're grabbing very many items. 
#
# While experimenting you may want to use the LIMIT construct in SPARQL to take
# only a couple of items, this way you can experiment with things without waiting
# ages for a query to complete.
print("  I might take some time, bear with  me...")

# merging results and saving the store
# The Week 4 lab showed us this, so we know that running the query will return a
# valid RDFlib graph.
g = sparql.query().convert()

# We also saw in Week 3 that we can parse files as valid RDFlib graphs too. When
# we do both of these things, they will be merged together.
g.parse("book.owl")

author_uris = set()
for subject, predicate, obj in g.triples((None, RDF.type, None)):
    for s, p, o in g.triples((subject, None, None)):
        if str(p).endswith("written_by"):
            author_uris.add(o)

sparql_bonus = SPARQLWrapper("https://query.wikidata.org/sparql")
for author in author_uris:
    author_uri = author
    author = str(author_uri)
    author_name = author.split('/')[-1].replace('_',' ')
    query_bonus = """
PREFIX ma: <http://www.semanticweb.org/dibah/ontologies/2024/3/untitled-ontology-11#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>

CONSTRUCT {
    ?author ma:AuthorBirthDate ?birthDate .
    ?author ma:WasBorn ?birthPlace .
    ?birthPlace rdf:type ma:BirthPlace .   
    ?author ma:NumberOfChildren ?numChild
}
WHERE {
    ?author wdt:P31 wd:Q5 .
    ?author rdfs:label "%s"@en .
    ?author wdt:P569 ?birthDate .
    ?author wdt:P19 ?birthPlace .
    ?author wdt:P1971 ?numChild
}
""" % (author_name)

    sparql_bonus.setQuery(query_bonus)
    sparql_bonus.setReturnFormat(XML)
    graph_id_bonus = URIRef("http://www.semanticweb.org/store/author")
    g_bonus = Graph(identifier=graph_id_bonus)
    g_bonus = sparql_bonus.query().convert()
    
    for s, p, o in g_bonus:
        g.add((author_uri,p,o))
    g.serialize("book_bonus.owl", format="xml")
print("All Done!")