import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
from sys import argv, stderr
import gzip
import curses
from subprocess import *

path_to_marc_files = argv[1]

filelist = [f for f in listdir(path_to_marc_files) if isfile(join(path_to_marc_files, f))]
totalfiles = len(filelist)
filecounter = 0

items = 0
organisations = 0
persons = 0
resources = 0

def check_for_tag(element, field, ind1='',ind2=''):
    if element.tag.endswith('datafield') and 'tag' in element.attrib and element.attrib['tag'] == field:
        if ind1 != '' and 'ind1' in element.attrib and ind2 != '' and 'ind2' in element.attrib:
            if element.attrib['ind1'] == ind1 and element.attrib['ind2'] == ind2:
                return True
        else:
            return True
    return False


for fi in filelist:
    filecounter += 1
    with gzip.open(join(path_to_marc_files, fi)) as f:
        print('Open file {} ({}/{})'.format(fi, filecounter, totalfiles), file=stderr)
        treeroot = ET.parse(f).getroot()
        for record in treeroot:
            tpersons = 0
            torganisations = 0
            titems = 0
            f245a = False
            for field in record:
                if check_for_tag(field, '100', '0', ' '):
                    tpersons += 1
                elif check_for_tag(field, '100', '1', ' '):
                    tpersons += 1
                elif check_for_tag(field, '110'):
                    torganisations += 1
                elif check_for_tag(field, '111'):
                    torganisations += 1
                elif check_for_tag(field, '245'):
                    for subfield in field:
                        if subfield.attrib['code'] == 'a':
                            f245a = True
                elif check_for_tag(field, '700', '0', ' '):
                    skip = False
                    for subfield in field:
                        if subfield.attrib['code'] == 't':
                            skip = True
                    if not skip:
                        tpersons += 1
                elif check_for_tag(field, '700', '1', ' '):
                    skip = False
                    for subfield in field:
                        if subfield.attrib['code'] == 't':
                            skip = True
                    if not skip:
                        tpersons += 1
                elif check_for_tag(field, '710'):
                    torganisations += 1
                elif check_for_tag(field, '711'):
                    torganisations += 1
                elif check_for_tag(field, '949'):
                    titems += 1
            if f245a:
                resources += 1
                persons += tpersons
                organisations += torganisations
                items += titems

print('Results:')
print('--------')
print('Documents:     {}'.format(resources))
print('Items:         {}'.format(items))
print('Organisations: {}'.format(organisations))
print('Persons:       {}'.format(persons))
print('Resources:     {}'.format(resources))
print('--------')
print('Total:         {}'.format(2 * resources + items + organisations + persons))
