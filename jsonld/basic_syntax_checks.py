#!/usr/bin/python3

"""
Performs basic syntax checks on JSON-LD files. Takes path to files as only argument
"""

from json import load
from os import listdir
from os.path import isfile, join
from sys import argv, stderr, stdout


class Entity:

    def __init__(self, obj, filename, lineno):
        self.filename = filename
        self.lineno = lineno
        self.obj = obj
        if '@id' in obj:
            self.id = obj['@id']
        else:
            print('ERROR\t{}:{}:\tNo @id field!'.format(filename, lineno), file=stderr)
            self.id = 'n/a'

    def check_for_field_value(self, fieldname, value, startswith=True):
        if fieldname in self.obj:
            if startswith:
                if not self.obj[fieldname].startswith(value):
                    print('ERROR\t{}:{}:\tWrong value in field "{}" in record {}! \'{}\' instead of \'{}\''.format(self.filename, self.lineno, fieldname, self.id, self.obj[fieldname], value), file=stderr)
            else:
                if not self.obj[fieldname].endswith(value):
                    print('ERROR\t{}:{}:\tWrong value in field "{}" in record {}! \'{}\' instead of \'{}\''.format(self.filename, self.lineno, fieldname, self.id, self.obj[fieldname], value), file=stderr)
        else:
            print('ERROR\t{}:{}:\tNo "{}" field in record {}'.format(self.filename, self.lineno, fieldname, self.id), file=stderr)



class Resource(Entity):
    id_prefix = 'https://data.swissbib.ch/bibliographicResource/'
    doctype = 'http://purl.org/dc/terms/BibliographicResource'
    context = 'https://resources.swissbib.ch/bibliographicResource/context.jsonld'
    is_defined_by_prefix = 'https://data.swissbib.ch/document/'

    def check(self):
        self.check_for_field_value('@id', self.id_prefix)
        self.check_for_field_value('@type', self.doctype)
        self.check_for_field_value('@context', self.context)
        self.check_for_field_value('rdfs:isDefinedBy', self.is_defined_by_prefix)
        if 'dct:contributor' in self.obj and len([e for e in self.obj['dct:contributor'] if 'NO_HASH' in e]):
            print('ERROR\t{}:{}:\tNO_HASH ids in field dct:contributor in record {}! {}'.format(self.filename, self.lineno, self.id, self.obj['dct:contributor']), file=stderr)
        elif 'dct:contributor' not in self.obj:
            print('WARNING\t{}:{}:\tNo dct:contributor field in record {}'.format(self.filename, self.lineno, self.id), file=stderr)


class Document(Entity):
    id_prefix = 'https://data.swissbib.ch/bibliographicResource/'
    id_postfix = '/about'
    doctype = 'http://purl.org/ontology/bibo/document'
    context = 'https://resources.swissbib.ch/document/context.jsonld'
    primary_topic_prefix = 'https://data.swissbib.ch/bibliographicResource/'

    def check(self):
        self.check_for_field_value('@id', self.id_prefix)
        self.check_for_field_value('@id', self.id_postfix, False)
        self.check_for_field_value('@type', self.doctype)
        self.check_for_field_value('@context', self.context)
        self.check_for_field_value('foaf:primaryTopic', self.primary_topic_prefix)


class Item(Entity):
    id_prefix = 'https://data.swissbib.ch/item/'
    doctype = 'http://bibframe.org/vocab/HeldItem'
    context = 'https://resources.swissbib.ch/item/context.jsonld'
    holding_for_prefix = 'https://data.swissbib.ch/bibliographicResource/'
    owner_prefix = 'https://data.swissbib.ch/organisation/'

    def check(self):
        self.check_for_field_value('@id', self.id_prefix)
        self.check_for_field_value('@type', self.doctype)
        self.check_for_field_value('@context', self.context)
        self.check_for_field_value('bf:holdingFor', self.holding_for_prefix)
        self.check_for_field_value('bibo:owner', self.owner_prefix)


class Person(Entity):
    id_prefix = 'https://data.swissbib.ch/person/'
    doctype = 'http://xmlns.com/foaf/0.1/Person'
    context = 'https://resources.swissbib.ch/person/context.jsonld'

    def check(self):
        self.check_for_field_value('@id', self.id_prefix)
        if '@id' in self.obj and 'NO_HASH' in self.obj['@id']:
            print('ERROR\t{}:{}:\tNO_HASH id in record {}!'.format(self.filename, self.lineno, self.id), file=stderr)
        self.check_for_field_value('@type', self.doctype)
        self.check_for_field_value('@context', self.context)


class Organisation(Entity):
    id_prefix = 'https://data.swissbib.ch/organisation/'
    doctype = 'http://xmlns.com/foaf/0.1/Organization'
    context = 'https://resources.swissbib.ch/organisation/context.jsonld'

    def check(self):
        self.check_for_field_value('@id', self.id_prefix)
        if '@id' in self.obj and 'NO_HASH' in self.obj['@id']:
            print('ERROR\t{}:{}:\tNO_HASH id in record {}!'.format(self.filename, self.lineno, self.id), file=stderr)
        self.check_for_field_value('@type', self.doctype)
        self.check_for_field_value('@context', self.context)
        if 'rdfs:label' not in self.obj:
            print('ERROR\t{}:{}\tNo rdfs:label field in record {}'.format(self.filename, self.lineno, self.id), file=stderr)


if __name__ == "__main__":
    path = argv[1]
    filenames = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

    i = 0
    for filename in filenames:
        i = i + 1
        stdout.write('\rReading file {} of {}'.format(i, len(filenames)))
        with open(filename) as f:
            lineno = 1
            j = load(f)
            for obj in j:
                lineno = lineno + 1
                if 'bibliographicResource' in filename:
                    entity = Resource(obj, filename, lineno)
                    entity.check()
                elif 'document' in filename:
                    entity = Document(obj, filename, lineno)
                    entity.check()
                elif 'item' in filename:
                    entity = Item(obj, filename, lineno)
                    entity.check()
                elif 'person' in filename:
                    entity = Person(obj, filename, lineno)
                    entity.check()
                elif 'organisation' in filename:
                    entity = Organisation(obj, filename, lineno)
                    entity.check()
