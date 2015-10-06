#!/bin/sh

#######################################################################
# Title: 	noBulkHeader
# Description:  Removes header lines from Elasticsearch Bulk-API
#               compliant files
# Usage: 	noBulkHeader.sh
# Created: 	2015-10-06
# Version: 	1.0
# Author: 	Sebastian Schüpbach (sebastian.schuepbach@unibas.ch)
#######################################################################

cd $1
for f in `ls *.jsonld.gz`
do
	gunzip -c $f | sed -e '1d;n;d' > ${f%.gz}
	gzip -f ${f%.gz}
done
