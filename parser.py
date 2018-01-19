#!/usr/bin/env python

import argparse
import csv
import re
import requests
import sys
from lxml import etree


class EcoParser:

    default_schema = "http://www.legislation.gov.uk/namespaces/legislation"

    def __init__(self, url):
        self.url = url

    def get_data(self):
        r = requests.get(self.url)
        r.raise_for_status()
        return r.content

    def _get_single_element(self, parent, tag, schema=None):
        if not schema:
            schema = self.default_schema
        elements = parent.findall("{%s}%s" % (schema, tag))
        if len(elements) != 1:
            raise Exception("Expected one match for tag '%s', found %i" % (tag, len(elements)))
        return elements[0]

    def _parse_table(self, table):
        thead = self._get_single_element(table, 'thead', 'http://www.w3.org/1999/xhtml')
        # TODO: parse headers

        tbody = self._get_single_element(table, 'tbody', 'http://www.w3.org/1999/xhtml')

        data = []
        for row in tbody:
            data.append(tuple(col.text for col in row))
        return data

    def parse_schedule(self):
        tree = etree.fromstring(self.get_data())
        secondary = self._get_single_element(tree, 'Secondary')
        schedules = self._get_single_element(secondary, 'Schedules')
        schedule = self._get_single_element(schedules, 'Schedule')
        schedule_body = self._get_single_element(schedule, 'ScheduleBody')
        tabular = self._get_single_element(schedule_body, 'Tabular')
        table = self._get_single_element(tabular, 'table', 'http://www.w3.org/1999/xhtml')
        return self._parse_table(table)

    def parse_article(self):
        raise NotImplementedError('TODO')

    def parse(self):
        schedule_pattern = r'http[s]?\:\/\/(www\.)?legislation\.gov\.uk\/(.)+\/schedule\/(.)+\/data\.xml'
        article_pattern  = r'http[s]?\:\/\/(www\.)?legislation\.gov\.uk\/(.)+\/article\/(.)+\/data\.xml'
        if re.match(schedule_pattern, self.url):
            return self.parse_schedule()
        elif re.match(article_pattern, self.url):
            return self.parse_article()
        else:
            raise Exception('Could not find a suitable parser for %s' % (self.url))


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
