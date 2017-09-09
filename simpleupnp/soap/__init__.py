SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"

def SOAP_TAG(tag):
    return "{{{}}}{}".format(SOAP_NS, tag)
