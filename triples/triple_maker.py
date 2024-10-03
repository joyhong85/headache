import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF, XSD, RDF, RDFS, SKOS, DCTERMS, OWL
import os, logging
from pathlib import Path

ZIG = Namespace('http://joyhong.tistory.com/zigzag/')
ONT = Namespace('http://joyhong.tistory.com/ontology/')


def init_graph():
    # 그래프 생성
    g = Graph()

    # namespace 바인딩
    # SCHEMA = Namespace("http://schema.org/")
    g.bind("zig", ZIG)
    g.bind("ont", ONT)
    g.bind("owl", OWL)
    # g.bind("schema", SCHEMA)
    g.bind("foaf", FOAF)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    return g


def create_directory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        logging.error("Error: Failed to create the directory.")


def serialize(g, file_name:str, format='turtle'):
    ROOT = str(Path(__file__).parent.parent)
    directory = ROOT+'/rdf/'
    create_directory(directory)
    g.serialize(destination=directory+file_name, format=format)
    logging.info("Finished..")


def make_concept():
    df = pd.read_excel("../data/headache.xlsx", sheet_name="concept")
    df.fillna("", inplace=True)
    g = init_graph()
    for row in df.values:
        subject = URIRef(ZIG + row[0])
        g.add((subject, RDF.type, URIRef(SKOS + 'Concept')))
        g.add((subject, RDFS.label, Literal(row[1])))
        g.add((subject, SKOS.prefLabel, Literal(row[0].replace("_", " "))))
        if row[2] != "":
            g.add((URIRef(ZIG + row[2]), SKOS.narrower, subject))
        if row[3] != "":
            schemes = row[3].split(",")
            for sc in schemes:
                sc = sc.strip()
                g.add((subject, SKOS.inScheme, URIRef(ZIG + sc)))
                g.add((URIRef(ZIG + sc), RDF.type, URIRef(SKOS + 'ConceptScheme')))
        if row[4] != "":
            altlabels = row[4].split(",")
            for al in altlabels:
                g.add((subject, SKOS.altLabel, Literal(al.strip())))
        if row[5] != "":
            g.add((subject, SKOS.definition, Literal(row[5])))

    serialize(g, "headache_concept.ttl", format='turtle')


def make_concept_scheme():
    df = pd.read_excel("../data/headache.xlsx", sheet_name="ConceptScheme")
    df.fillna("", inplace=True)
    g = init_graph()
    for row in df.values:
        subject = URIRef(ZIG + row[0])
        g.add((subject, RDF.type, URIRef(SKOS + 'ConceptScheme')))
        g.add((subject, RDFS.label, Literal(row[1])))
        g.add((subject, SKOS.prefLabel, Literal(row[0].replace("_", " "))))
        if row[2] != "":
            altlabels = row[2].split(",")
            for al in altlabels:
                g.add((subject, SKOS.altLabel, Literal(al.strip())))

    serialize(g, "headache_scheme.ttl", format='turtle')


make_concept()
make_concept_scheme()