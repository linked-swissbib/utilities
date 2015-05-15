#!/bin/bash
#
#Guenter Hipler 15.5.2015


export PATH=/home/swissbib/environment/tools/python3/env/bin:$PATH

DOCS_BASEDIR=/swissbib_index/linkedProcessing
DOCS_BASEDIR_INPUT=${DOCS_BASEDIR}/linkedRDFOutput
DOCS_BASEDIR_OUTPUT=${DOCS_BASEDIR}/json.es.bulk
LOG_DIR=${DOCS_BASEDIR}/log
LOGFILE=${LOG_DIR}/ES_UPLOAD.log
TRANSFORMATION_SCRIPT=/home/swissbib/environment/code/linkedSwissbib/utilities/python/rdfxml2es.py
ES_INDEX_FILE=/home/swissbib/environment/code/linkedSwissbib/utilities/examples/04/indctrl.json
JSONLD_FRAME_FILE=/home/swissbib/environment/code/linkedSwissbib/utilities/examples/04/frame.jsonld


CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`




function usage()
{
 printf "usage: $0 "
}

function setTimestamp()
{
    CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`
}


function preChecks()
{
    echo "not used so far"
}


function process2JSONLD ()
{


   for subdir in `ls ${DOCS_BASEDIR_INPUT}`
    do

       setTimestamp
       printf "start uploading to ES in <%s>\n" ${dir} >> ${LOGFILE}

       printf "unzip the files with Search documents" >> ${LOGFILE}
       #gunzip ${POSTDIRBASE}/$dir/*.gz

       for rdfxmlFile in `ls ${DOCS_BASEDIR_INPUT}/${subdir}`
       do
            python ${TRANSFORMATION_SCRIPT} --indctrl=${ES_INDEX_FILE} \
                                        --filemode \
                                        --oneline \
                                        --outsubDir=${DOCS_BASEDIR_OUTPUT} \
                                        ${DOCS_BASEDIR_INPUT}/${subdir}/${rdfxmlFile} \
                                        ${JSONLD_FRAME_FILE}
       done


    done


}

setTimestamp
process2JSONLD

