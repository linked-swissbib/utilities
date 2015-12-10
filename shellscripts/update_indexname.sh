#!/bin/sh

#######################################################################
# Title: 	update_indexname
# Description:  Updates the index name in gzipped Elasticsearch Bulk-API
#               compliant files
# Usage: 	update_indexname.sh <old index name> <new index name>
# Created: 	2015-12-10
# Author: 	Sebastian Schüpbach (sebastian.schuepbach@unibas.ch)
#######################################################################

for f in *.jsonld.gz
do
	gunzip $f
	# sed -in 's/"_index":"$1"/"_index":"$2"/g' ${f:0:-3}
	sed -i "s/\"_index\":\"$1\"/\"_index\":\"$2\"/g" ${f:0:-3}
	gzip ${f:0:-3}
done
