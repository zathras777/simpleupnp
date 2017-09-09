from __future__ import print_function

import sys
import argparse
from pprint import pprint


from ssdp import SSDP
import upnp
from utils.xml import string_to_xml_to_dict, xml_dict_get
from dlna.contentdirectory import ContentDirectory



if __name__ == '__main__':
    parser = argparse.ArgumentParser('Basic UPNP/DLNA command line client')
    parser.add_argument('--name', help='Name of device to look for')
    parser.add_argument('--service', help='Service to look for')
    parser.add_argument('-v', '--verbose', action='store_true', help='Service to look for')
    parser.add_argument('command', nargs="*", help='Service to look for')
    args = parser.parse_args()

    if 'list' in args.command and len(args.command) > 1:
        print("The 'list' command doesn't play well with others. You may not get the expected results.")

    filter_devices = 'list' not in args.command

    if len(args.command) == 0:
        print("Nothing to do. Please specify a command!\nAvailable commands:\n")
        print("    list      - list all available services")
        print("    detail    - show details of filtered services (use with --name and --service)")
        print("    browse    - try and browse a ContentDirectory service\n")
        sys.exit(0)

    sdp = SSDP()
    sdp.discover()
    if args.verbose:
        sdp.dump()

    if len(sdp) == 0:
        print("No devices found...")
        sys.exit(0)

    possible = []
    targets = []

    if filter_devices and args.name is not None:
        for dvc in sdp:
            if dvc.friendlyName is None:
                if args.verbose:
                    print("Skipping device {} as no friendly name available.".format(dvc.host_string()))
                continue
            if args.name in dvc.friendlyName:
                possible.append(dvc)
    else:
        possible = [dvc for dvc in sdp]

    if len(possible) == 0:
        print("No matches found for name '{}'. Exiting.".format(args.name))
        sys.exit(0)
    possible = sorted(possible, key=lambda x: x.host_string())

    if filter_devices and args.service is not None:
        for dvc in possible:
            for svc in dvc.services:
                if args.service in svc.serviceType:
                    targets.append(svc)   
    else:
        for poss in possible:
            targets.extend(poss.services)

    if len(targets) == 0:
        print("No services found that match your criteria. Exiting...")
        sys.exit(0)
    targets = sorted(targets, key=lambda x: x.serviceType)

    if 'browse' in args.command:
        target = None
        for poss in targets:
            if 'ContentDirectory' in poss.serviceType:
                target = poss
                break

        if target is None:
            print("Unable to find a ContentDirectory to browse...")
            sys.exit(0)

        cdd = ContentDirectory(target)
        print("Browsing ContentDirectory for {}".format(target.device.friendlyName))
        print("System Update ID: {}".format(cdd.updateId))

        if cdd.Browse(RequestedCount=10):
            while True:
                cdd.display_containers()
                print("\nEnter folder number to browse. 'U' to go up. 'I' for expanded information. Return or 'Q' to exit.")
                opt = raw_input("Enter folder number to browse [return to exit]: ")
                opt = opt.strip()
                if opt == '' or opt in ['Q', 'q']:
                    break
                if opt in ['U', 'u']:
                    nxt = cdd.parent or 0
                elif opt in ['I', 'i']:
                    cdd.display_containers(True)
                    continue
                else:
                    nxt = cdd.id_for_container(int(opt) - 1)
                    if nxt is None:
                        break
                if not cdd.Browse(nxt, RequestedCount=10):
                    break

    if 'list' in args.command:
        print("Listing all services found.")
        typ = None
        for tgt in targets:
            if typ != tgt.serviceType:
                print("\n{}".format(tgt.serviceType))
            print("    {:20s} - {}".format(tgt.device.host_string(),
                                           tgt.device.friendlyName))
            typ = tgt.serviceType

    if 'detail' in args.command:
        for tgt in targets:
            print(tgt.dump())

