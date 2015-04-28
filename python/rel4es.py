__author__ = 'Sebastian Schüpbach'
__copyright__ = 'Copyright 2015, swissbib project, UB Basel'
__license__ = 'http://opensource.org/licenses/gpl-2.0.php'
__version__ = '0.1'
__maintainer__ = 'Sebastian Schüpbach'
__email__ = 'sebastian.schuepbach@unibas.ch'
__status__ = 'development'

"""
This file provides a wrapper for indexing and querying related data records in Elasticsearch
"""

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

client = Elasticsearch([{'host': 'localhost', 'port': 9200}])

s = Search(using=client, index="itest35")