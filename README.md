# Book Information Ontology

The goal of this project is to gather information from multiple data sources and integrating them in a seamless manner using protégé to better visualize the connections between data. 

This project is consisted of three main sections.

## Basic part

In the basic part of this project the layout of the ontology is constructed in the protégé, then the book data is queried inside this ontology from dbpedia which is the first data source used in this project by book_dbpedia.py file.

## Bonus part

In this section additional information about the author of the books are queried inside this ontology from wikidata.

## Advanced part

In the advanced part Description Logics are added to the ontology in the book_bonus.owl file which resulted in book_advanced

## File description

book_dbpedia.py is a file which is used to query data in to the Book_Ontology.owl ontology and creates book_dboedia.owl

bonus.py is a file which is used to query author data to the book_dbpedia.owl file and creates book_bonus.owl.

main.py does all the three part together in the same file and creates book.owl file.
