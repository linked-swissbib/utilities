__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '0.1'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

from elasticsearch import Elasticsearch
from pprint import pprint

def rcr(index='itest01', type='ttest01', id='dtest01'):
    body = '{"alist": ["element1"]}'
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    es.index(index=index, doc_type=type, id=id, body=body)
    res = es.get(index=index, doc_type=type, id=id)
    print("\nOriginal Document\n-----------------")
    pprint(res)
    res['_source']['alist'].extend(['element2', 'element3'])
    es.index(index=index, doc_type=type, id=id, body=res)
    res = es.get(index=index, doc_type=type, id=id)
    print("\nUpdated Document\n-----------------")
    pprint(res)

def updateapi(index='itest01', type='ttest01', id='dtest01'):
    body = '{"alist": ["element1"]}'
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    es.index(index=index, doc_type=type, id=id, body=body)
    res = es.get(index=index, doc_type=type, id=id)
    print("\nOriginal Document\n-----------------")
    pprint(res)
    body = '''
    {"script": "ctx._source.alist+=new_element",
     "params": {
        "new_element": ["element2", "element3"]
     }
    }
    '''
    es.update(index=index, doc_type=type, id=id, body=body)
    res = es.get(index=index, doc_type=type, id=id)
    print("\nUpdated Document\n-----------------")
    pprint(res)