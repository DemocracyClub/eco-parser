DEFAULT_SCHEMA = "http://www.legislation.gov.uk/namespaces/legislation"


class ParseError(Exception):
    pass


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