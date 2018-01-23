import abc
import re
from eco_parser.core import get_single_element, get_elements_recursive, ParseError


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

    def is_header(self, row):
        header_row = False
        for col in row:
            if col.tag == '{http://www.w3.org/1999/xhtml}th':
                header_row = True
        return header_row

    def parse_body(self):
        tbody = get_single_element(self.element, 'tbody', schema='http://www.w3.org/1999/xhtml')
        data = []
        for row in tbody:
            if not self.is_header(row):
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
