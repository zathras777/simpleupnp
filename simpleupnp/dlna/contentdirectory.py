from __future__ import print_function

from pprint import pprint

from utils.xml import xml_dict_get, string_to_xml_to_dict


class ContentDirectory(object):
    def __init__(self, service):
        self.service = service
        self.updateID = 0

        self.containers = []
        self.items = []
        self.GetUpdateID()
        self.structure = []

    @property
    def parent(self):
        if len(self.structure) < 2:
            return 0
        return self.structure[-2][0]

    def GetUpdateID(self):
        result = self.service.GetSystemUpdateID()
        if not 'Id' in result:
            print("Unable to get the system updateId")
            return False
        self.updateId = result['Id']
        return True

    def update_structure(self, fid):
        if fid == 0:
            self.structure = [(0, 'Root')]
            return
        for poss in self.containers:
            if poss['@attr']['id'] == fid:
                self.structure.append((fid, poss['title']))
                return
        print("Unable to update structure...")

    def Browse(self, folder_id=0, flag="BrowseDirectChildren", **kwargs):
        self.update_structure(folder_id)
        self.containers = []
        self.items = []

        args = {'ObjectID': folder_id, 'BrowseFlag': flag}
        args.update(**kwargs)
        b_result = self.service.Browse(**args)
        if b_result is None:
            print("Invalid folder id?")
            return False
        if b_result['NumberReturned'] == 0:
            return True
        result = string_to_xml_to_dict(b_result['Result'])
        if result is None:
            print("Invalid XML returned???\n{}".format(b_result['Result']))
            return False

        self.containers = xml_dict_get(result, 'DIDL-Lite/container', [])
        self.items = xml_dict_get(result, 'DIDL-Lite/item', [])
        return True

    def display_containers(self, expand=False):
        nnn = 1
        print("\nLocation: {}\n".format(" / ".join([x[1] for x in self.structure])))

        for container in self.containers:
            print("  {:3d}: {}".format(nnn, container['title']))
            if expand:
                for key in container.keys():
                    if key == '@attr':
                        print("        Attributes: ")
                        continue
                    elif '@' in key:
                        continue
                    print("        {:30s} : {}".format(key, container[key]))
            nnn += 1
        if len(self.containers) == 0 and len(self.items) > 0:
            print("\nThere are {} items available...".format(len(self.items)))
            nnn = 1
            for item in self.items:
                print("  {:3d}: {}".format(nnn, item['title']))
                if expand:
                    for key in item.keys():
                        if key == '@attr':
                            print("        Attributes: ")
                            continue
                        elif '@' in key:
                            continue
                        print("        {:30s} : {}".format(key, item[key]))
                nnn += 1
                

    def id_for_container(self, idx):
        if idx > len(self.containers) or len(self.containers) == 0:
            return None
        return self.containers[idx]['@attr']['id']
