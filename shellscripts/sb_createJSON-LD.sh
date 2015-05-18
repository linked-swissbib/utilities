#!/bin/bash
#
#Guenter Hipler 15.5.2015


export PATH=/home/swissbib/environment/tools/python3/env/bin:$PATH



CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`




function usage()
{
    #./sb_createJSON-LD.sh -o/swissbib_index/linkedProcessing/jsonld.bulk.files -l/swissbib_index/linkedProcessing/log -i/swissbib_index/linkedProcessing/linkedRDFOutput -f/home/swissbib/environment/code/linkedSwissbib/utilities/examples/04/frame.jsonld -e/home/swissbib/environment/code/linkedSwissbib/utilities/examples/04/indctrl.json
     printf "usage: $0 -o[BASEDIR for writing the created json-ld files] -i[basic input directory for RDF/XML files to be transformed in Json-LD] -l[base dir log] -b[bulksize - optional default 21000] -e [Indexfile to create ES INdex] -f[Framing file for JSON-ld] "
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
            echo "ERROR : base directory -->>${DOCS_BASEDIR_OUTPUT}<<-- for JSON-LD files does not exist!\n"  && usage && exit 9
    fi


    if [ ! -n "${LOG_DIR}" ]
    then
            echo "option -l [LOG_DIR] not set"  && usage && exit 9
    fi

    if [ ! -d ${LOG_DIR} ]
    then
            echo "ERROR : base directory -->>${LOG_DIR}<<-- for logging files does not exist!\n"  && usage && exit 9
    fi

    if [ ! -n "${DOCS_BASEDIR_INPUT}" ]
    then
            echo "option -i [DOCS_BASEDIR_INPUT] not set"  && usage && exit 9
    fi

    if [ ! -d ${DOCS_BASEDIR_INPUT} ]
    then
            echo "ERROR : base directory -->>${DOCS_BASEDIR_INPUT}<<-- for files to be transformed into Json-ld does not exist!\n"  && usage && exit 9
    fi


    if [ ! -n "${FRAMING}" ]
    then
            echo "option -f [framing file] not set"  && usage && exit 9
    fi

    if [ ! -f ${FRAMING} ]
    then
            echo "framing file -->>${FRAMING}<<--  does not exist!\n"  && usage && exit 9
    fi



    if [ ! -n "${ES_INDEX_FILE}" ]
    then
            echo "option -e [index file] not set"  && usage && exit 9
    fi

    if [ ! -f ${ES_INDEX_FILE} ]
    then
            echo "index file -->>${ES_INDEX_FILE}<<--  does not exist!\n"  && usage && exit 9
    fi

    if [ ! -n "${BULKSIZE}" ]
    then
            BULKSIZE=22000
            echo "BULKSIZE was set to 22000"
    fi




    echo "pre checks successful"
}


function process2JSONLD ()
{

    SHELLPATH=`dirname $BASH_SOURCE`


   for subdir in `ls ${DOCS_BASEDIR_INPUT}`
    do

       setTimestamp
       printf "transformation to JSON-LD started for subdir <%s>\n" ${DOCS_BASEDIR_INPUT}/${subdir} >> ${LOGFILE}

       for rdfxmlFile in `ls ${DOCS_BASEDIR_INPUT}/${subdir}`
       do

           setTimestamp

            BASEFILENAME=`basename ${rdfxmlFile} .gz`
            gunzip ${DOCS_BASEDIR_INPUT}/${subdir}/${rdfxmlFile}

            printf "processing file <%s>\n" ${DOCS_BASEDIR_INPUT}/${subdir}/${BASEFILENAME} >> ${LOGFILE}
            python ${SHELLPATH}/../python/rdfxml2es.py   \
                                        --indctrl=${ES_INDEX_FILE} \
                                        --filemode \
                                        --oneline \
                                        --bulksize=${BULKSIZE} \
                                        --outsubDir=${DOCS_BASEDIR_OUTPUT} \
                                        ${DOCS_BASEDIR_INPUT}/${subdir}/${BASEFILENAME} \
                                        ${FRAMING}   >>   ${LOGFILE_PYTHON} 2>&1

            gzip ${DOCS_BASEDIR_INPUT}/${subdir}/${BASEFILENAME}

       done


    done


}

while getopts hi:e:o:l:b:f: OPTION
do
  case $OPTION in
    h) usage
	exit 9
	;;
	i) DOCS_BASEDIR_INPUT=$OPTARG   #basic input directory
	;;
	e) ES_INDEX_FILE=$OPTARG
	;;
	o) DOCS_BASEDIR_OUTPUT=$OPTARG      #basic output directory outputbasedir
	;;
    l) LOG_DIR=$OPTARG              #Logdirectory
    ;;
    b) BULKSIZE=$OPTARG
    ;;
    f) FRAMING=$OPTARG
    ;;
    *) printf "unknown option -%c\n" $OPTION; usage; exit;;
  esac
done

preChecks

LOGFILE=${LOG_DIR}/ES_CREATE_JSON_PROCESS.log
LOGFILE_PYTHON=${LOG_DIR}/ES_CREATE_JSON.log

setTimestamp

process2JSONLD


