import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF, XSD, RDF, RDFS, SKOS, DCTERMS, OWL, DC
import os, logging
from pathlib import Path

ZIG = Namespace('http://joyhong.tistory.com/zigzag/')
CPT = Namespace('http://joyhong.tistory.com/concept/')
ONT = Namespace('http://joyhong.tistory.com/ontology/')


def init_graph():
    # 그래프 생성
    g = Graph()

    # namespace 바인딩
    g.bind("zig", ZIG)
    g.bind("ont", ONT)
    g.bind("owl", OWL)
    g.bind("cpt", CPT)
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
        subject = URIRef(CPT + row[0])
        g.add((subject, RDF.type, URIRef(SKOS + 'Concept')))
        g.add((subject, RDFS.label, Literal(row[1])))
        g.add((subject, SKOS.prefLabel, Literal(row[0].replace("_", " "))))
        if row[2] != "":
            g.add((URIRef(CPT + row[2]), SKOS.narrower, subject))
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


def add_triple(g, subject:URIRef, predicate:URIRef, object_prefix, object_suffix, object_type):
    if object_suffix != "":
        if object_type == URIRef:
            g.add((subject, predicate, URIRef(object_prefix + object_suffix)))
        else:
            g.add((subject, predicate, Literal(object_suffix)))


def make_ontology():
    df = pd.read_excel("../data/headache.xlsx", sheet_name="model")
    df.fillna("", inplace=True)
    g = init_graph()
    g.add((URIRef(ZIG), RDF.type, OWL.Ontology))
    g.add((URIRef(ZIG), OWL.imports, URIRef('http://www.w3.org/2004/02/skos/core')))
    g.add((URIRef(ZIG), OWL.versionInfo, Literal('1.0')))
    g.add((URIRef(ZIG), DC.creator, Literal('Joyhong(su4620@gmail.com)')))
    g.add((URIRef(ZIG), RDFS.comment, Literal('지그재그 토이프로젝트를 위해 두통 도메인에 대한 온톨로지를 구성')))

    for row in df.values:
        subject = URIRef(ONT + row[1])
        add_triple(g, subject, RDFS.label, "", row[2], Literal)
        add_triple(g, subject, RDFS.comment, "", row[3], Literal)
        if row[0] == 'class':
            add_triple(g, subject, RDF.type, OWL, 'Class', URIRef)
            add_triple(g, subject, RDFS.subClassOf, OWL, 'Thing', URIRef)
        elif row[0] == "objectproperty":
            add_triple(g, subject, RDF.type, OWL, 'ObjectProperty', URIRef)
        elif row[0] == "datatypeproperty":
            add_triple(g, subject, RDF.type, OWL, 'DatatypeProperty', URIRef)

        add_triple(g, subject, RDFS.domain, ONT, row[4], URIRef)
        add_triple(g, subject, RDFS.range, ONT, row[5], URIRef)
    serialize(g, "headache_ontology.ttl", format='turtle')


def make_basic():
    df = pd.read_excel("../data/headache.xlsx", sheet_name="DC")
    df.fillna("", inplace=True)
    g = init_graph()
    for row in df.values:
        subject = URIRef(ZIG + row[0])
        add_triple(g, subject, RDF.type, ONT, 'DiagnosisCriteria', URIRef)
        add_triple(g, subject, RDFS.label, "", row[0], Literal)
        add_triple(g, subject, RDFS.comment, "", row[1], Literal)
        if row[2] != "":
            sym = row[2].split("|")
            for sy in sym:
                add_triple(g, subject, URIRef(ONT + 'contain'), ZIG, sy, URIRef)
        if row[3] != "":
            disease = row[3].split("|")
            for ds in disease:
                add_triple(g, URIRef(ZIG + ds.strip()), URIRef(ONT + 'determinedBy'), ZIG, row[0], URIRef)
                add_triple(g, URIRef(ZIG + ds.strip()), DCTERMS.subject, CPT, ds, URIRef)

    df = pd.read_excel("../data/headache.xlsx", sheet_name="SY")
    df.fillna("", inplace=True)
    for row in df.values:
        subject = URIRef(ZIG + row[0])
        add_triple(g, subject, RDF.type, ONT, 'Symptoms', URIRef)
        add_triple(g, subject, RDFS.label, "", row[0], Literal)
        add_triple(g, subject, RDFS.comment, "", row[1], Literal)

    serialize(g, "headache_basic.ttl", format='turtle')


make_concept()
make_concept_scheme()
make_ontology()
make_basic()