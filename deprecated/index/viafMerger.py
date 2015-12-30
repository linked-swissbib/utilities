from elasticsearch import Elasticsearch
import argparse


p = argparse.ArgumentParser(description="Merges documents in type viaf which are referenced by a document in type "
                                        "person either by simply appending the fields of the former to the fields of "
                                        "the latter or by nesting the fields of the former into the document of type"
                                        "person.")
p.add_argument('--index', metavar='<str>', dest='index', type=str, required=True, help='Name of index')
p.add_argument('--node', metavar='<str>', dest='node', type=str, required=True, help='Url and port of node')
args = p.parse_args()

es = Elasticsearch([args.node])
same_as = es.search(index=args.index,
                    doc_type='person',
                    _source=['owl:sameAs'],
                    body='{"query":{"exists":{"field":"owl:sameAs"}}}',
                    size=1000)['hits']['hits']
ref_viaf = dict()
for e in same_as:
    if es.exists(index=args.index, doc_type='person', id=e['_id']):
        print('Retrieving document ' + e['_source']['owl:sameAs'] + ' in order to add it to document ' + e['_id'] + '.')
        query_body = '{"query":{"ids":{"values":["' + e['_source']['owl:sameAs'][21:] + '"]}}}'
        viaf_entry = es.search(index=args.index,
                           doc_type='viaf',
                           _source=True,
                           body=query_body)['hits']['hits'][0]['_source']
        inner_viaf = es.get(index=args.index,
                              doc_type='person',
                              id=e['_id'],
                              _source = True)['_source']
        embedded_viaf = es.get(index=args.index,
                              doc_type='person',
                              id=e['_id'],
                              _source = True)['_source']
        print('Updating document ' + e['_id'] + '.')
        inner_viaf['viaf'] = viaf_entry
        inner_viaf = str(inner_viaf).replace("'", "\"")
        embedded_viaf.update(viaf_entry)
        embedded_viaf = str(embedded_viaf).replace("'", "\"")
        print("INNER VIAF")
        print(inner_viaf)
        es.index(index=args.index, doc_type='inner_viaf', id=e['_id'], body=inner_viaf)
        print("EMBEDDED VIAF")
        print(embedded_viaf)
        es.index(index=args.index, doc_type='embedded_viaf', id=e['_id'], body=embedded_viaf)
    else:
        print('Document with id ' + e['_id'] + ' does not exist!')
