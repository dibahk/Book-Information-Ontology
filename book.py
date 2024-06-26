
import rdflib
from rdflib.graph import Graph, URIRef
from SPARQLWrapper import SPARQLWrapper, XML

# Configuring the end-point and constructing query.

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
    ?country rdfs:label ?Ncountry .
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
        OPTIONAL {?book dbpedia-owl:genre ?genre .}
        OPTIONAL {?book dbpedia-owl:publisher ?publisher}
        OPTIONAL {?book dbpedia-owl:coverArtist ?coverArtist .
        ?coverArtist dbp:name ?NcoverArtist}
        OPTIONAL {?book dbpedia-owl:numberOfPages ?numberOfPages}
        ?book dbpedia-owl:isbn ?isbn .
        FILTER(?isbn != "") . # Ensure ISBN is not an empty string
        ?book dbp:releaseDate ?releaseDate .
        OPTIONAL {?book dbpedia-owl:country ?country .
        ?country dbp:conventionalLongName ?Ncountry}
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

graph_id = URIRef("http://www.semanticweb.org/store/book")
g = Graph(identifier = graph_id)

print("  I might take some time, bear with  me...")

# merging results and saving the store

g = sparql.query().convert()

# Parsing the original ontology for merging.
g.parse("Book_Ontology.owl")

g.serialize("book_dbpedia.owl", "xml")

print("  ...All done!")
print("")
