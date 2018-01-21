#!/usr/bin/env python

import abc
import argparse
import csv
import re
import requests
import sys
from lxml import etree


DEFAULT_SCHEMA = "http://www.legislation.gov.uk/namespaces/legislation"


def get_single_element(parent, tag, schema=None):
    if not schema:
        schema = DEFAULT_SCHEMA

    elements = parent.findall("{%s}%s" % (schema, tag))
    if len(elements) != 1:
        raise ParseError("Expected one match for tag '%s', found %i" % (tag, len(elements)))
    return elements[0]


def get_elements_recursive(parent, tag, schema=None):
    if not schema:
        schema = DEFAULT_SCHEMA

    data = []
    target = "{%s}%s" % (schema, tag)
    for child in parent:
        if (child.tag == target):
            data.append(child)
        data = data + get_elements_recursive(child, tag, schema)
    return data


class ParseError(Exception):
    pass


class ElementParser(metaclass=abc.ABCMeta):

    def __init__(self, element):
        self.element = element

    @abc.abstractmethod
    def parse(self):
        pass


class TableParser(ElementParser):

    def parse_head(self):
        thead = get_single_element(self.element, 'thead', schema='http://www.w3.org/1999/xhtml')
        headers = []
        for th in thead[0]:
            text = "".join(th.itertext())
            text = re.sub('\s+', ' ', text).strip()
            headers.append(text)
        return tuple(th for th in headers)

    def parse_body(self):
        tbody = get_single_element(self.element, 'tbody', schema='http://www.w3.org/1999/xhtml')
        data = []
        for row in tbody:
            data.append(tuple(col.text for col in row))
        return data

    def parse(self):
        return [self.parse_head()] + self.parse_body()


class BodyParser(ElementParser):

    def parse(self):
        elements = get_elements_recursive(self.element, 'Text')
        return [(el.text.strip().rstrip(',.;'),) for el in elements]


class ElementParserFactory:

    @staticmethod
    def create(element):
        try:
            tabular = get_single_element(element, 'Tabular')
            table = get_single_element(tabular, 'table', schema='http://www.w3.org/1999/xhtml')
            return TableParser(table)
        except ParseError:
            return BodyParser(element)


class EcoParser:

    def __init__(self, url):
        self.url = url

    def get_data(self):
        r = requests.get(self.url)
        r.raise_for_status()
        return r.content

    def parse_schedule(self):
        tree = etree.fromstring(self.get_data())
        secondary = get_single_element(tree, 'Secondary')
        schedules = get_single_element(secondary, 'Schedules')
        schedule = get_single_element(schedules, 'Schedule')
        schedule_body = get_single_element(schedule, 'ScheduleBody')
        p = ElementParserFactory.create(schedule_body)
        return p.parse()

    def parse_article(self):
        tree = etree.fromstring(self.get_data())
        secondary = get_single_element(tree, 'Secondary')
        body = get_single_element(secondary, 'Body')
        p = ElementParserFactory.create(body)
        return p.parse()

    def parse(self):
        schedule_pattern = r'http[s]?\:\/\/(www\.)?legislation\.gov\.uk\/(.)+\/schedule\/(.)+\/data\.xml'
        article_pattern  = r'http[s]?\:\/\/(www\.)?legislation\.gov\.uk\/(.)+\/article\/(.)+\/data\.xml'
        if re.match(schedule_pattern, self.url):
            return self.parse_schedule()
        elif re.match(article_pattern, self.url):
            return self.parse_article()
        else:
            raise ParseError('Could not find a suitable parser for %s' % (self.url))


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(
        description='Parse ward lists from Electoral Change Orders on legislation.gov.uk')
    arg_parser.add_argument(
        'url',
        help='URL to grab XML from e.g: http://www.legislation.gov.uk/uksi/2017/1067/schedule/1/made/data.xml'
    )
    args = arg_parser.parse_args()

    p = EcoParser(args.url)
    data = p.parse()
    writer = csv.writer(sys.stdout)
    for row in data:
        writer.writerow(row)
