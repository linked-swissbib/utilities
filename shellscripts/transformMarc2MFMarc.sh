#!/bin/bash

#ulimit -v unlimited

CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`

function usage()
{
 printf "usage: $0 -i[Inputdir with Marc files not MF compatible - should be zipped] -o[Output dir for MF compatible Marc Files] -l[base dir log]"
 echo ""

}

function setTimestamp()
{
    CURRENT_TIMESTAMP=`date +%Y%m%d%H%M%S`
}


function preChecks()
{
    echo "options are going to be checked"


    if [ ! -n "${INPUT_DIR}" ]
    then
            echo "option -i [INPUT_DIR] not set"  && usage && exit 9
    fi

    if [ ! -d ${INPUT_DIR} ]
    then
            echo "ERROR : input  directory -->>${INPUT_DIR}<<-- for files to be transformed in compatible MF Marc not exist!\n"  && usage && exit 9
    fi


    if [ ! -n "${LOG_DIR}" ]
    then
            echo "option -l [LOG_DIR] not set"  && usage && exit 9
    fi

    if [ ! -d ${LOG_DIR} ]
    then
            echo "ERROR : base directory -->>${LOG_DIR}<<-- for logging files does not exist!\n"  && usage && exit 9
    fi


    if [ ! -n "${OUTPUT_DIR}" ]
    then
            echo "option -o [OUTPUT_DIR] not set"  && usage && exit 9
    fi

    if [ ! -d ${OUTPUT_DIR} ]
    then
            echo "ERROR : output  directory -->>${OUTPUT_DIR}<<-- for files with compatible MF Marc not exist!\n"  && usage && exit 9
    fi


    echo "pre checks successful"
}




function transformMarc ()
{

    SHELLPATH=`dirname $BASH_SOURCE`
    for datei in ${INPUT_DIR}/*.gz
    do
        #actually the name convention I assume is only possible for initial loading

        echo "unzip $datei" >> ${logscriptflow}
        gunzip ${datei}

        echo "transform file $datei"  >> ${logscriptflow}


        setTimestamp

        BASEFILENAME=`basename ${datei} .gz`
        #echo $BASEFILENAME
        #FILENAME=${BASEFILENAME}.mf.xml
        python ${SHELLPATH}/../python/transFormMarc2MFMarc.py -i${INPUT_DIR}/${BASEFILENAME} -o${OUTPUT_DIR}/$BASEFILENAME

        gzip ${INPUT_DIR}/${BASEFILENAME}
        gzip ${OUTPUT_DIR}/$BASEFILENAME




    done

}


while getopts hi:o:l: OPTION
do
  case $OPTION in
    h) usage
	exit 9
	;;
	i) INPUT_DIR=$OPTARG      #inputdir
	;;
    o) OUTPUT_DIR=$OPTARG		# outputdir
    ;;
    l) LOG_DIR=$OPTARG              #Logdirectory
    ;;
    *) printf "unknown option -%c\n" $OPTION; usage; exit;;
  esac
done



preChecks

logscriptflow=${LOG_DIR}/transformMarc.log
setTimestamp
echo "start transforming marc data into MF format: "${CURRENT_TIMESTAMP}"\n" >> ${logscriptflow}

transformMarc
setTimestamp
echo "end transforming marc data into MF format: "${CURRENT_TIMESTAMP}"\n" >> ${logscriptflow}
