import re
from os import listdir, remove
from os.path import isfile, join
from sys import argv

from elasticsearch import Elasticsearch

__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2016, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '1.0'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

"""
Reads name of every file in a specified directory (assuming it has a special pattern timestamp_action_id.xml)
and adds its resId to a list of to be removed documents in the Elasticsearch index.
"""

es = Elasticsearch(['http://localhost:9200'])
index = 'testsb_160616'

# Filenames need to have the format YYYYmmddHHMMSSffffff_ACTION_id
p = re.compile('^([0-9]{20})_([A-Z]{6})_([a-zA-Z0-9]{9})\.xml')

with open(argv[2], 'a') as tf:
    files = [f for f in listdir(argv[1]) if isfile(join(argv[1], f))]
    codes = []
    for f in files:
        resId = p.match(f).group(3)
        tf.write('{ "delete" : { "_index" : "%s", "_type" : "bibliographicResource", "_id" : "%s" } }\n'
                 % (index, resId))
        tf.write('{ "delete" : { "_index" : "%s", "_type" : "document", "_id" : "%s" } }\n'
                 % (index, resId))
        items = es.search(index=index, doc_type='item',
                          body='{"query": {"term": {"bf:holdingFor": "http://data.swissbib.ch/resource/%s"}}}' %
                               resId,
                          filter_path=['hits.hits._id'])
        for i in items['hits']['hits']:
            tf.write('{ "delete" : { "_index" : "%s", "_type" : "item", "_id" : "%s" } }\n' % (index, i['_id']))
        remove(join(argv[1], f))
