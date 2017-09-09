from __future__ import print_function

from lxml import etree

from utils.xml import xml_to_dict, string_to_xml_to_dict, xml_dict_get
from __init__ import SOAP_NS, SOAP_TAG


def check_nsmap(node):
    for key in node.nsmap:
        if node.nsmap[key] == SOAP_NS:
            return True
    return False


def parse_response(content):
    """ SOAP Response """
    soap = string_to_xml_to_dict(content)
    if soap is None:
        return False, None
    if not '@ns' in soap or soap['@ns'] != SOAP_NS:
        print("Non SOAP response?")
        return False, None
    body_nodes = xml_dict_get(soap, "Envelope/Body", [])
    if body_nodes == []:
        print("Empty SOAP body?")
        return False, None
    if len(body_nodes) != 2:
        print("Multiple responses???")
        return False, None
    return True, body_nodes
