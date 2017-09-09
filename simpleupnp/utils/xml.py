import re
from lxml import etree
from pprint import pprint


def plain_tag(node):
    tag_info = re.match(r"\{(.*)\}(.*)", node.tag.strip())
    if tag_info is None:
        return node.tag
    return tag_info.group(2)


def tag_ns(node):
    tag_info = re.match(r"\{(.*)\}(.*)", node.tag.strip())
    if tag_info is None:
        return None
    return tag_info.group(1)


def tag_text(node):
    if node.text is None:
        return None
    rtext = node.text.strip()
    return rtext if len(rtext) > 0 else None


def string_to_xml_to_dict(xml_string, with_root=True):
    try:
        xml = etree.fromstring(xml_string)
    except etree.XMLSyntaxError as e:
        print(e)
        return None
    return xml_to_dict(xml, with_root)


def xml_to_dict(xml, with_root=False):
    rvd = {}
    if len(xml.attrib) > 0:
        rvd['@attr'] = xml.attrib
    for node in xml.getchildren():
        tag = plain_tag(node)
        _tag_attrs = "{}@attrs".format(tag)
        _tag_ns = "{}@ns".format(tag)

        tag_dict_or_text = tag_text(node) if len(list(node)) == 0 else xml_to_dict(node)
        if tag_dict_or_text is None:
            continue
        
        if tag in rvd:
            if type(rvd[tag]) != list:
                rvd[tag] = [rvd[tag], tag_dict_or_text]
            else:
                rvd[tag].append(tag_dict_or_text)
            if _tag_attrs in rvd:
                rvd.pop(_tag_attrs)
        else:
            rvd[tag] = tag_dict_or_text
            ns = tag_ns(node)
            if ns is not None:
                rvd[_tag_ns] = ns
            if len(node.attrib) > 0:
                rvd[_tag_attrs] = node.attrib

    if with_root:
        rvd = {plain_tag(xml): rvd}
        nss = tag_ns(xml)
        if nss is not None:
            rvd['@ns'] = nss
    return rvd


def xml_dict_get(xml_dict, path, default=None):
    parts = path.split('/')
    if parts[0] in xml_dict:
        if len(parts) == 1:
            return xml_dict[parts[0]]
        return xml_dict_get(xml_dict[parts[0]], "/".join(parts[1:]), default)
    return default


def search_xml(root, node, raw=False):
    xpath_expr = './/' + '/'.join(['*[local-name()="{}"]'.format(p) for p in node.split('/')])
    matches = root.xpath(xpath_expr)
    if raw:
        return matches
    if len(matches) > 0:
        return matches[0].text
    return ''
