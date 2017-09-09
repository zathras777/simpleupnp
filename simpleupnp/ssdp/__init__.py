from __future__ import print_function

import socket
import re
import requests

from upnp.device import Device


class SSDP(object):
    def __init__(self):
        self.devices = {}

    def discover(self):
        msg = \
            'M-SEARCH * HTTP/1.1\r\n' \
            'HOST:239.255.255.250:1900\r\n' \
            'ST:upnp:rootdevice\r\n' \
            'MX:2\r\n' \
            'MAN:"ssdp:discover"\r\n' \
            '\r\n'

        # reset service list...
        self.services = {}
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.settimeout(2)
        s.sendto(msg, ('239.255.255.250', 1900) )

        try:
            while True:
                data, addr = s.recvfrom(65507)
                hdrs = {}
                for hdr in data.split("\r\n"):
                    if hdr.startswith('HTTP'):
                        reg = re.match("^HTTP/[0|1]\.[0-9] ([0-9]{3}) (.*)", hdr)
                        if reg is not None:
                            if int(reg.group(1)) != 200:
                                print("Invalid response code, {} {}".format(reg.groups(1), reg.groups(2)))
                                break
                    else:
                        if len(hdr.strip()) == 0:
                            continue
                        (key, val) = hdr.strip().split(":", 1)
                        hdrs[key] = val.strip()
                dvc_key = "{}:{}".format(*addr)
                dvc = Device(hdrs, addr)
                self.devices[dvc_key] = dvc

        except socket.timeout:
            pass

    def dump(self):
        for key in sorted(self.devices.keys()):
            print(key)
            print(self.devices[key].location or "No location available...")

    def __len__(self):
        return len(self.devices)

    def __iter__(self):
        for dvc in self.devices:
            yield self.devices[dvc]


__ALL__ = [SSDP]
