#!/bin/bash
#
#Guenter Hipler 15.5.2015


#export PATH=/home/swissbib/environment/tools/python3/env/bin:$PATH



CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`




function usage()
{
    #on sb-s2 / sb-s6 / sb-s7
     #cd $WORKFLOWS
    #./utilities/shellscripts/sb_createJSON-LD.sh -o${DATA_BASE}/jsonld.bulk.files -l${DATA_BASE}/log -i${DATA_BASE}/linkedRDFOutput -f${WORKFLOWS}/utilities/examples/04/frame.jsonld -e${WORKFLOWS}/utilities/examples/04/indctrl.json -b42000 -slocalhost -p8080 > process.jsonld.log 2>&1 &

     printf "usage: $0 -o[BASEDIR for writing the created json-ld files] -i[basic input directory for RDF/XML files to be transformed in Json-LD] -l[base dir log] -b[bulksize - optional default 21000] -e [Indexfile to create ES INdex] -f[Framing file for JSON-ld] -s[server: default - localhost] -p[ES server port - default 9200]"
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

    if [ ! -n "${SERVER}" ]
    then
            SERVER=localhost
            echo "ES server was set to localhost"
    fi

    if [ ! -n "${PORT}" ]
    then
            PORT=9200
            echo "Port was set to 9200"
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
                                        --host=${SERVER}        \
                                        --port=${PORT}          \
                                        ${DOCS_BASEDIR_INPUT}/${subdir}/${BASEFILENAME} \
                                        ${FRAMING}   >>   ${LOGFILE_PYTHON} 2>&1

            gzip ${DOCS_BASEDIR_INPUT}/${subdir}/${BASEFILENAME}

       done


    done


}

while getopts hi:e:o:l:b:f:s:p: OPTION
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
    s) SERVER=$OPTARG
    ;;
    p) PORT=$OPTARG
    ;;
    *) printf "unknown option -%c\n" $OPTION; usage; exit;;
  esac
done

preChecks

LOGFILE=${LOG_DIR}/ES_CREATE_JSON_PROCESS.log
LOGFILE_PYTHON=${LOG_DIR}/ES_CREATE_JSON.log

setTimestamp

process2JSONLD


