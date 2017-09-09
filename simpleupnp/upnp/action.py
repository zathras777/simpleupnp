from __future__ import print_function

from lxml import etree
from pprint import pprint
import requests

from utils.xml import xml_dict_get
from soap.response import parse_response


class ActionArgument(object):
    def __init__(self, data):
        self.name = data['name']
        self.direction = data['direction']
        self.related = data['relatedStateVariable']
        self.related_obj = None

    def value(self, val=None):
        typ = self.related_obj
        if typ is None:
            return val
        return typ.get(val)

    def convert_value(self, val):
        typ = self.related_obj
        if typ is None:
            return val
        return typ.convert(val)


class Action(object):
    def __init__(self, svc, xml_dict):
        self.service = svc
        self.name = xml_dict['name']
        self.args = []

        arg_list_or_none = xml_dict_get(xml_dict, 'argumentList/argument', None)
        if arg_list_or_none is None:
            return
        if type(arg_list_or_none) is not list:
            self.args.append(ActionArgument(arg_list_or_none))
        else:
            for arg in arg_list_or_none:
                self.args.append(ActionArgument(arg))

    def resolve_arguments(self, variables):
        for arg in self.args:
            if arg.related in variables:
                arg.related_obj = variables[arg.related]
            else:
                print("Unable to find related variable {}".format(arg.related))

    def __call__(self, **kwargs):
        if self.check_args(**kwargs) is False:
            return None

        body = self.make_soap_body(**kwargs)
        return self.make_soap_request(body)

    def find_arg(self, key, direction):
        for arg in self.args:
            if arg.name == key and arg.direction == direction:
                return arg
        return None

    def check_args(self, **kwargs):
        for key in kwargs.keys():
            arg = self.find_arg(key, "in")
            if arg is None:
                print("Unknown key '{}' passed to {}".format(key, self.name))
                return False
        return True

    def convert_response(self, resp):
        for key in resp.keys():
            arg = self.find_arg(key, "out")
            if arg is None:
                print("Unexpected argument in response, {}".format(key))
                return False
            print(arg)
            resp[key] = arg.convert_value(resp[key])

        return True

    def make_soap_body(self, **kwargs):
        NSMAP = {'SOAP-ENV': "http://schemas.xmlsoap.org/soap/envelope"}
        NSMAP_2 = {'u': self.service.serviceType}
        def soap_tag(tag):
            return "{{{}}}{}".format(NSMAP['SOAP-ENV'], tag)
        def upnp_tag(tag):
            return "{{{}}}{}".format(self.service.serviceType, tag)
        root = etree.Element(soap_tag('Envelope'), nsmap=NSMAP)
        body = etree.Element(soap_tag('Body'))
        root.append(body)
        action = etree.Element(upnp_tag(self.name), nsmap=NSMAP_2)
        for arg in [x for x in self.args if x.direction == "in"]:
            arg_el = etree.Element(upnp_tag(arg.name))
            txt = arg.value(kwargs.get(arg.name, None))
            if txt is None:
                print("No suitable value for {}, omitting".format(arg.name))
                continue
            arg_el.text = str(txt)
            action.append(arg_el)
        body.append(action)
        print(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        return etree.tostring(root, xml_declaration=True, encoding='UTF-8')

    def make_soap_request(self, body):
        headers = {
            'SOAPAction': u'"%s"' % self.service.make_action(self.name),
            'Host': "{}:{}".format(*self.service.host()),
            'Content-Type': 'text/xml',
            'Content-Length': str(len(body))
        }
        req = requests.post(self.service.url(), data=body, headers=headers)
        print(req.content)
        if req.status_code == 500:
            valid, resp = parse_response(req.content)
            if not valid:
                return None
            if not '{}Response'.format(self.name) in resp:
                print("Invalid response received?")
                return None
        elif req.status_code == 200:
            valid, resp = parse_response(req.content)
            if not valid:
                return None
            resp_key = '{}Response'.format(self.name)
            if not resp_key in resp or not resp_key+'@ns' in resp:
                print("Unexpected response received...")
                return None
            if resp[resp_key+'@ns'] != self.service.serviceType:
                print("Namespace for response does not match serviceId\n{} vs {}".format(resp[resp_key+'@ns'], self.service.serviceType))
                return None

            resp = resp[resp_key]
            if not self.convert_response(resp):
                return None
            return resp
            
        elif req.status_code == 200:
            return req.content

        print("status_code {}".format(req.status_code))
        print(req.content)
        return None

    def full_str(self):
        act_str = """
        {}
            Inputs:\n""".format(self.name)
        for arg in [x for x in self.args if x.direction == "in"]:
            act_str += "                {} {}\n".format(arg.related_obj.data_type, arg.name)
        act_str += "            Outputs:\n"
        for arg in [x for x in self.args if x.direction == "out"]:
            act_str += "                {} {}\n".format(arg.related_obj.data_type, arg.name)
        return act_str
