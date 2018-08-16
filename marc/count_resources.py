import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
from sys import argv, stderr
import gzip

path_to_marc_files = argv[1]

filelist = [f for f in listdir(path_to_marc_files) if isfile(join(path_to_marc_files, f))]
totalfiles = len(filelist)
filecounter = 0

items = 0
organisations = 0
persons = 0
resources = 0

def check_for_tag(element, field, ind1=''):
    if element.tag.endswith('datafield') and 'tag' in element.attrib and element.attrib['tag'] == field:
        if ind1 != '' and 'ind1' in element.attrib:
            if element.attrib['ind1'] == ind1:
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
            resources += 1
            for field in record:
                if check_for_tag(field, '100', '0'):
                    persons += 1
                elif check_for_tag(field, '100', '1'):
                    persons += 1
                elif check_for_tag(field, '110'):
                    organisations += 1
                elif check_for_tag(field, '111'):
                    organisations += 1
                elif check_for_tag(field, '700', '0'):
                    persons += 1
                elif check_for_tag(field, '700', '1'):
                    persons += 1
                elif check_for_tag(field, '710'):
                    organisations += 1
                elif check_for_tag(field, '711'):
                    organisations += 1
                elif check_for_tag(field, '949'):
                    items += 1

print('Results:')
print('--------')
print('Documents:     {}'.format(resources))
print('Items:         {}'.format(items))
print('Organisations: {}'.format(organisations))
print('Persons:       {}'.format(persons))
print('Resources:     {}'.format(resources))
