__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '1'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

import argparse

from elasticsearch import Elasticsearch
from elasticsearch import exceptions
from jsmin import jsmin

p = argparse.ArgumentParser(description="Creates the mapping for Elasticsearch")
p.add_argument('ifile', metavar='<file>', type=argparse.FileType('r'), help='Input file')
p.add_argument('--index', metavar='<str>', dest='index', type=str, required=True, help='Name of index')
p.add_argument('--node', metavar='<str>', dest='node', type=str, required=True, help='Url and port of node')
args = p.parse_args()

body = jsmin(args.ifile.read())

try:
    es = Elasticsearch([args.node])
    es.indices.create(index=args.index, body=body)
except exceptions.ConnectionError as ce:
    print("Could not connect to server")
