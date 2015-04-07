#!/bin/bash

#ulimit -v unlimited


function test ()
{

    for datei in ${INPUT_DIR}/*.gz
    do

        echo $datei

        BASEFILENAME=`basename ${datei} .gz`
        echo $BASEFILENAME


    done

}

function transformMarc ()
{
    nr=1
    for datei in ${INPUT_DIR}/*.gz
    do
        #actually the name convention I assume is only possible for initial loading

        echo "unzip $datei" >> ${logscriptflow}
        gunzip ${datei}

        echo "transform file $datei"  >> ${logscriptflow}

        TIMESTAMP=`date +%Y%m%d%H%M%S`	# seconds

        BASEFILENAME=`basename ${datei} .gz`
        #echo $BASEFILENAME
        #FILENAME=${BASEFILENAME}.mf.xml
        python ./transFormMarc2MFMarc.py -i${INPUT_DIR}/${BASEFILENAME} -o${OUTDIR_BASE}/$BASEFILENAME

        gzip ${INPUT_DIR}/${BASEFILENAME}


        nr=$(($nr+1))

    done

}

BASEDIR=$PWD
INPUT_DIR=/swissbib_index/solrDocumentProcessing/FrequentInitialPreProcessing/data/format_2

OUTDIR_BASE=${BASEDIR}/out2

logscriptflow=${BASEDIR}/log/transformMarc.log

TIMESTAMP=`date +%Y%m%d%H%M%S`	# seconds
echo "start transforming marc data into MF format: "${TIMESTAMP}"\n" >> ${logscriptflow}


transformMarc
#test

#gzip ${OUTDIR_BASE}/*.xml

TIMESTAMP=`date +%Y%m%d%H%M%S`	# seconds
echo "end transforming marc data into MF format: "${TIMESTAMP}"\n" >> ${logscriptflow}
