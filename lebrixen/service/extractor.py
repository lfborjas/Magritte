#wrapper for the extractor web service
#makes request in SOAP 1.1
#based on http://effbot.org/zone/elementsoap-2.htm

from elementsoap.ElementSOAP import SoapService, SoapRequest, SoapElement
from xml.dom.minidom import getDOMImplementation
from xml.etree.ElementTree import tostring


class ExtractorService(SoapService):
    def __init__(self, key, url=None):
        SoapService.__init__(self, url)
        self.__key = key

    def create_request_body(self, text):
        impl = getDOMImplementation()
        doc = impl.createDocument(None, 'ExtractionRequest', None)
        x = doc.createElement('EXTRACTEE')
        y = doc.createTextNode(text)
        x.appendChild(y)
        doc.documentElement.appendChild(x)
        return doc.toxml()


    def extract(self, text):
        action = 'http://www.picofocus.com/DemoEngine/DBIExtractorDemoWebService/ProcessXtraction'
        request = SoapRequest('ProcessXtraction')
        #.set('xmlns','http://www.picofocus.com/DemoEngine/DBIExtractorDemoWebService')
        SoapElement(request, name='applicationID', type= "string", text=self.__key )
        SoapElement(request, name='xTractionRequest', text=self.create_request_body(text))
        raw_res= self.call(action, request).findall("*")[0].findall('*')[0]
        #print raw_res
        #print raw_res.get('ExtractionStatus')
        return raw_res


