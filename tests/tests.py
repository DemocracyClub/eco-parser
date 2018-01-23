import os
import unittest
from eco_parser import EcoParser, ParseError


SCHEDULE_WITH_TABLE = 'http://www.legislation.gov.uk/uksi/2017/1067/schedule/1/made/data.xml'
SCHEDULE_WITHOUT_TABLE = 'http://www.legislation.gov.uk/uksi/2017/477/schedule/1/made/data.xml'
ARTICLE_WITHOUT_TABLE = 'http://www.legislation.gov.uk/uksi/2017/1270/article/3/made/data.xml'
TABLE_WITHOUT_HEADER = 'http://www.legislation.gov.uk/uksi/2015/1873/schedule/1/made/data.xml'


# stub parser implementation we can run tests against
class StubParser(EcoParser):

    def get_data(self):
        fixtures = {
            SCHEDULE_WITH_TABLE: 'fixtures/schedule_with_table.xml',
            SCHEDULE_WITHOUT_TABLE: 'fixtures/schedule_without_table.xml',
            ARTICLE_WITHOUT_TABLE: 'fixtures/article_without_table.xml',
            TABLE_WITHOUT_HEADER: 'fixtures/table_without_header.xml',
        }
        dirname = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.abspath(os.path.join(dirname, fixtures[self.url]))
        if self.url in fixtures:
            return bytes(open(file_path, 'r').read(), 'utf-8')
        else:
            raise Exception("no test fixture defined for url '%s'" % self.url)


class ParserTest(unittest.TestCase):

    def test_no_parser_found(self):
        p = StubParser('foo.bar/baz')
        with self.assertRaises(ParseError):
            p.parse()

    def test_schedule_with_table(self):
        p = StubParser(SCHEDULE_WITH_TABLE)
        self.assertSequenceEqual([
            ('(1) Name of borough ward', '(2) Number of councillors'),
            ('Crummock & Derwent Valley', '1'),
            ('St John’s', '3'),
            ('Warnell', '1'),
            ('Westward Ho!', '2'),
            ('Audley & Queen’s Park', '2'),
        ], p.parse())

    def test_table_without_header(self):
        p = StubParser(TABLE_WITHOUT_HEADER)
        self.assertSequenceEqual([
            ('Crummock & Derwent Valley', '1'),
            ('St John’s', '3'),
            ('Warnell', '1'),
            ('Westward Ho!', '2'),
            ('Audley & Queen’s Park', '2'),
        ], p.parse())

    def test_schedule_without_table(self):
        p = StubParser(SCHEDULE_WITHOUT_TABLE)
        self.assertSequenceEqual([
            ('Crummock & Derwent Valley',),
            ('St John’s',),
            ('Warnell',),
            ('Westward Ho!',),
            ('Audley & Queen’s Park',),
        ], p.parse())

    def test_article_without_table(self):
        p = StubParser(ARTICLE_WITHOUT_TABLE)
        self.assertSequenceEqual([
            ('The existing wards of the borough of Foo Town are abolished',),
            ('The borough of Foo Town is divided into 5 wards as follows—',),
            ('Crummock & Derwent Valley',),
            ('St John’s',),
            ('Warnell',),
            ('Westward Ho!',),
            ('Audley & Queen’s Park',),
            ('Each ward comprises the area identified on the map by reference to the name of the ward',),
            ('Three councillors are to be elected for each ward',),
        ], p.parse())
