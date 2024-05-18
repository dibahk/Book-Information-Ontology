import rdflib
from rdflib.namespace import RDF
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
        OPTIONAL {?book dbpedia-owl:literaryGenre ?genre .}
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

g.parse("book.owl")

# extracting author names
author_uris = set()
for subject, predicate, obj in g.triples((None, RDF.type, None)):
    for s, p, o in g.triples((subject, None, None)):
        if str(p).endswith("written_by"):
            author_uris.add(o)

sparql_bonus = SPARQLWrapper("https://query.wikidata.org/sparql")
for author in author_uris:
    author_uri = author
    author = str(author_uri)
    author_name = author.rsplit('/',1)[-1].replace('_',' ')
    query_bonus = """
PREFIX ma: <http://www.semanticweb.org/dibah/ontologies/2024/3/untitled-ontology-11#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>

CONSTRUCT {
    ?author ma:AuthorBirthDate ?BirthDate .
    ?author ma:WasBornIn ?BirthPlace .
    ?BirthPlace rdf:type ma:BirthPlace .   
    ?BirthPlace rdfs:label ?birthPlaceName .
    ?author ma:NumberOfChildren ?numChild .
    ?author ma:Gender ?gender .
    ?gender rdfs:label ?gendern .
}
WHERE {
    ?author wdt:P31 wd:Q5 .
    ?author rdfs:label "%s"@en .
    OPTIONAL { ?author wdt:P569 ?BirthDate . 
        MINUS { 
            ?author wdt:P569 ?anotherBirthDate . 
            FILTER(?anotherBirthDate < ?BirthDate) 
        } 
        } 
    OPTIONAL { ?author wdt:P19 ?BirthPlace .     
    ?BirthPlace rdfs:label ?birthPlaceName . 
    FILTER NOT EXISTS { ?BirthPlace wdt:P31 wd:Q6256 }}
    OPTIONAL { ?author wdt:P1971 ?numChild . }
    OPTIONAL { ?author wdt:P21 ?gender .
    ?gender rdfs:label ?gendern .
    FILTER (lang(?gendern) = "en") .}
    
    FILTER (LANG(?birthPlaceName) = 'en') .
    }
    LIMIT 1
""" % (author_name)

    sparql_bonus.setQuery(query_bonus)
    sparql_bonus.setReturnFormat(XML)
    graph_id_bonus = URIRef("http://www.semanticweb.org/store/author")
    g_bonus = Graph(identifier=graph_id_bonus)
    g_bonus = sparql_bonus.query().convert()
    
    for s, p, o in g_bonus:
        if str(p) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" or str(p) == "http://www.w3.org/2000/01/rdf-schema#label":
            s = s
        else:
            s = author_uri
        
        g.add((s,p,o))
        
    g.serialize("book1.owl", format="xml")
print("All Done!")