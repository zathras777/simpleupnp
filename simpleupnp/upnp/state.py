from __future__ import print_function

"""
  <serviceStateTable>
    <stateVariable sendEvents="yes">
      <name>SourceProtocolInfo</name>
      <dataType>string</dataType>
    </stateVariable>
"""

class StateVariable(object):
    def __init__(self, xml_dict):
        (self.min, self.max, self.step) = [-1, -1, -1]
        self.send_events = xml_dict['@attr']['sendEvents']
        self.name = xml_dict['name']
        self.data_type = xml_dict['dataType']
        if 'allowedValueRange' in xml_dict:
            self.min = xml_dict['allowedValueRange'].get('minimum', -1)
            self.max = xml_dict['allowedValueRange'].get('maximum', -1)
            self.step = xml_dict['allowedValueRange'].get('step', -1)
        if 'allowedValueList' in xml_dict:
            self.allowed_values = xml_dict['allowedValueList'].get('allowedValue', None)
        else:
            self.allowed_values = None
        self.default = xml_dict.get('defaultValue', None)

    def get(self, value):
        if value is None and self.default is not None:
            return self.default
        if self.allowed_values and value not in self.allowed_values:
            print("Value '{}' is NOT allowed.\nOptions are {}".format(
                value, ", ".join(self.allowed_values)))
            return None
        print(self.asstring())
        return value

    def convert(self, value):
        if value is None:
            return value
        print(self.data_type)
        if self.data_type == 'string':
            return str(value)
        if self.data_type == 'ui4':
            return int(value)
        return value

    def asstring(self):
        st_str = "{} : {}\n".format(self.name, self.data_type)
        st_str += "    : {}\n".format(self.default)
        st_str += "    : {} to {}, step {}\n".format(self.min, self.max, self.step)
        st_str += "    : {}\n".format(self.allowed_values)
        return st_str