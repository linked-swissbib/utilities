#!/bin/bash - 
#===============================================================================
#
#          FILE: indexWorkflows.sh
# 
#         USAGE: ./indexWorkflows.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Sebastian Schüpbach, sebastian.schuepbach@unibas.ch
#  ORGANIZATION: Project Swissbib
#       CREATED: 16.06.2016 16:22
#      REVISION: 29.06.2016
#===============================================================================

set -o nounset                              # Treat unset variables as an error

# Set default paths (don't change them unless you know what you are doing)
fileloc=$(readlink -f $0)
ROOTDIR=${fileloc%/*}
LOGDIR=$ROOTDIR/logs
LOGFILE=$LOGDIR/lsb.log
MF_HOME=$ROOTDIR/apps/mfWorkflows
BASELINE=$MF_HOME/src/main/resources/transformation/baseLine.flux
ENRICHEDLINE=$MF_HOME/src/main/resources/transformation/enrichedLine.flux
RESHAPER_SB=$ROOTDIR/apps/dummyLinkingWrapper
RESHAPER_DBP=$ROOTDIR/apps/dummyLinkingWrapper
RESHAPER_VIAF=$ROOTDIR/apps/dummyLinkingWrapper
LINKING=$ROOTDIR/apps/dummyLinkingWrapper
WORKLINE=$ROOTDIR/apps/workConceptGenerator.jar
GARBAGECOLLECTOR=$ROOTDIR/apps/garbageCollector.jar
DELETELINE=$ROOTDIR/apps/deletebulk.py
DELETEFOLDER=$ROOTDIR/data/deleteFolder
SPARK_HOME=$SPARK_HOME
SPARK_MASTER="local[*]"
ES_CLUSTERNAME=elasticsearch
ES_HTTP_HOST="localhost:9200"
ES_TCP_HOST="localhost:9300"
ES_INDEX=lsb


function log {
	echo $(date +"%Y-%m-%d %H:%M:%S") :: $1 | tee --append $LOGFILE
}


function checkvars {
	if [ -z $1 ]; then
		log "Variable $2 not set! Aborting."
		exit 1
	fi
	if [ ! -f $1 ] && [ ! -d $1 ]; then
		log "The file $1 doesn't exist! Aborting."
		exit 1
	fi
}


checkvars $ROOTDIR \$ROOTDIR
checkvars $LOGDIR \$LOGDIR
checkvars $DELETELINE \$DELETELINE
checkvars $DELETEFOLDER \$DELETEFOLDER
checkvars $MF_HOME \$MF_HOME
checkvars $BASELINE \$BASELINE
checkvars $ENRICHEDLINE \$ENRICHEDLINE
checkvars $RESHAPER_SB \$RESHAPER_SB
checkvars $RESHAPER_DBP \$RESHAPER_DBP
checkvars $RESHAPER_VIAF \$RESHAPER_VIAF
checkvars $LINKING \$LINKING
checkvars $WORKLINE \$WORKLINE
checkvars $GARBAGECOLLECTOR \$GARBAGECOLLECTOR


log "Transforming and creating concepts bibliographicResource, document, organisation and item"
cd $MF_HOME
bash flux.sh $BASELINE &>> $LOGFILE
log "Tranformation finished"

log "Starting reshaping workflows"
for RESHAPER in $RESHAPER_SB $RESHAPER_DBP $RESHAPER_VIAF
do
	$RESHAPER &>> $LOGFILE &
done
wait
log "Reshaping finished"

log "Starting linking process"
# $LINKING &>> $LOGFILE
log "Linking finished"


log  "Indexing enriched person documents"
$MF_HOME/flux.sh $ENRICHEDLINE &>> $LOGFILE


# wait $baselineid
python $DELETELINE $DELETEFOLDER $LOGDIR/deleteBulk.log


log "Creating work concept"
java -jar $WORKLINE --sparkMaster $SPARK_MASTER --sparkHome $SPARK_HOME --esHost $ES_HTTP_HOST --esCluster $ES_CLUSTERNAME &>> $LOGFILE
log "Creation of work concept finished"


log "Indexing of enriched person documents finished"
log "Garbage collecting index"
java -jar $GARBAGECOLLECTOR -clean -eshost $ES_TCP_HOST -esname $ES_CLUSTERNAME -esindex $ES_INDEX &>> $LOGFILE
log "All finished!"
