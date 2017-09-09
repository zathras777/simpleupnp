from __future__ import print_function

from lxml import etree
import requests
import re
from urlparse import urlparse
from pprint import pprint

from utils.xml import xml_to_dict, search_xml
from service import Service


class Device(object):
    def __init__(self, info, host):
        self.host = host
        self.location = info.get('LOCATION')
        self.st = info.get('ST')
        self.usn = info.get('USN')
        self.root = None
        self.friendlyName = None
        self.services = []
        self.get_description()

    def get_description(self):
        if self.location is None:
            return False
        req = requests.get(self.location)
        if req.status_code != 200:
            return False
        self.root = etree.fromstring(req.content)
        self.friendlyName = search_xml(self.root, "device/friendlyName")
        for svc in self.service_entries():
            if 'SCPDURL' in svc:
                self.services.append(Service(self, svc))
            else:
                print("No SCPDURL...")

    def service_entries(self):
        if self.root is not None:
            for svc in search_xml(self.root, 'device/serviceList/service', True):
                yield(xml_to_dict(svc))

    def host_string(self):
        return "{}:{}".format(*self.host)

    def url(self, uri):
        base = urlparse(self.location)
        if not uri.startswith('/'):
            uri = '/{}'.format(uri)
        return "{}://{}{}".format(base.scheme, base.netloc, uri)

