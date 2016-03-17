#!/bin/bash

#######################################################################
# Title: 	update_indexname
# Description:  Updates the index name in gzipped Elasticsearch Bulk-API
#               compliant files
# Usage: 	update_indexname.sh <path to dir> <old index name> <new index name>
# Created: 	2015-12-10
# Author: 	Sebastian Schüpbach (sebastian.schuepbach@unibas.ch)
#######################################################################

cd $1
for f in $(find -type f -name "*.jsonld.gz")
do
	gunzip $f
	# sed -in 's/"_index":"$2"/"_index":"$3"/g' ${f:0:-3}
	sed -i "s/\"_index\":\"$2\"/\"_index\":\"$3\"/g" ${f:0:-3}
	gzip ${f:0:-3}
done
