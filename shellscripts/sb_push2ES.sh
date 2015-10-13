#!/bin/bash
#
#Guenter Hipler 15.5.2015


export PATH=/home/swissbib/environment/tools/python3/env/bin:$PATH

DOCS_BASEDIR=/swissbib_index/linkedProcessing
#DOCS_BASEDIR_OUTPUT=${DOCS_BASEDIR}/json.es.bulk
#LOG_DIR=${DOCS_BASEDIR}/log


CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`




function usage()
{
 printf "usage: $0 -o[BASEDIR json files] -u[url index server] -l[base dir log]"
 echo ""

 printf "Example on localhost: ./sb_push2ES.sh -o/swissbib_index/linkedProcessing/linkedTestOutput -ulocalhost:8080/_bulk -l/swissbib_index/linkedProcessing/log"
 echo ""

}

function setTimestamp()
{
    CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`
}


function preChecks()
{
    echo "options are going to be checked"


    if [ ! -n "${DOCS_BASEDIR_OUTPUT}" ]
    then
            echo "option -o [DOCS_BASEDIR_OUTPUT] not set"  && usage && exit 9
    fi

    if [ ! -d ${DOCS_BASEDIR_OUTPUT} ]
    then
            echo "ERROR : base directory -->>${DOCS_BASEDIR_OUTPUT}<<-- for files to be posted does not exist!\n"  && usage && exit 9
    fi


    if [ ! -n "${LOG_DIR}" ]
    then
            echo "option -l [LOG_DIR] not set"  && usage && exit 9
    fi

    if [ ! -d ${LOG_DIR} ]
    then
            echo "ERROR : base directory -->>${LOG_DIR}<<-- for logging files does not exist!\n"  && usage && exit 9
    fi



    #-z: the length of string is zero
    [ -z  ${URLINDEXSERVER} ] && echo " option -u [URL index serevr] not set" && usage && exit 9

    #-n: True if the length of "STRING" is non-zero.
    [ ! -n ${URLINDEXSERVER} ] && echo "index server  is not set"  && usage && exit 9

    echo "pre checks successful"
}


function push2ES ()
{


   for subdir in `ls ${DOCS_BASEDIR_OUTPUT}`
    do

       setTimestamp
       printf "start uploading json files to ES in <%s>\n" ${DOCS_BASEDIR_OUTPUT}/${subdir} >> ${LOGFILE}

       gunzip ${DOCS_BASEDIR_OUTPUT}/$subdir/*.gz

       for jsonFile in `ls ${DOCS_BASEDIR_OUTPUT}/${subdir}`
       do

            printf "starting to push file <%s> to ES \n\n" ${DOCS_BASEDIR_OUTPUT}/${subdir}/${jsonFile} >> ${LOGFILE}

            printf "starting to push file <%s> to ES \n\n" ${DOCS_BASEDIR_OUTPUT}/${subdir}/${jsonFile} >> ${LOGFILE_CURL}

            curl -XPOST ${URLINDEXSERVER} --data-binary @${DOCS_BASEDIR_OUTPUT}/${subdir}/${jsonFile} >> ${LOGFILE_CURL} 2>&1

            echo "\n\n" >> ${LOGFILE_CURL}

       done

       gzip ${DOCS_BASEDIR_OUTPUT}/$subdir/*


    done


}

while getopts ho:u:l: OPTION
do
  case $OPTION in
    h) usage
	exit 9
	;;
	o) DOCS_BASEDIR_OUTPUT=$OPTARG      #outputbasedir
	;;
    u) URLINDEXSERVER=$OPTARG		# URL ES server
    ;;
    l) LOG_DIR=$OPTARG              #Logdirectory
    ;;
    *) printf "unknown option -%c\n" $OPTION; usage; exit;;
  esac
done

preChecks

#DOCS_BASEDIR_OUTPUT=${DOCS_BASEDIR}/json.es.bulk
LOGFILE_CURL=${LOG_DIR}/ES_Push2JsonCurl.log
LOGFILE=${LOG_DIR}/ES_Push2Json.log



setTimestamp
push2ES

