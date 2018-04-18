# -*- coding: ISO-8859-15 -*-

'''
API For Web Map Service version 1.3.0
'''

from __future__ import (absolute_import, division, print_function)

try:                    # Python 3
    from urllib.parse import urlencode
except ImportError:     # Python 2
    from urllib import urlencode

import warnings
import six
from owslib.etree import etree
from owslib.util import openURL, ServiceException, testXMLValue, extract_xml_list, xmltag_split, OrderedDict
from owslib.util import nspath
from owslib.fgdc import Metadata
from owslib.iso import MD_Metadata
from owslib.crs import Crs
from owslib.namespaces import Namespaces
from owslib.map.common import WMSCapabilitiesReader

from owslib.util import log

n = Namespaces()
WMS_NAMESPACE = n.get_namespace("wms")


class WebMapService_1_3_0(object):

    def __getitem__(self, name):
        ''' check contents dictionary to allow dict
        like access to service layers
        '''
        if name in self.__getattribute__('contents'):
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError("No content named %s" % name)

    def __init__(self, url, version='1.3.0', xml=None, username=None,
                 password=None, parse_remote_metadata=False, timeout=30):
        """initialize"""
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        self.timeout = timeout
        self._capabilities = None

        # Authentication handled by Reader
        reader = WMSCapabilitiesReader(self.version, url=self.url,
                                       un=self.username, pw=self.password)
        if xml:  # read from stored xml
            self._capabilities = reader.readString(xml)
        else:  # read from server
            self._capabilities = reader.read(self.url, timeout=self.timeout)

        print("1.3.0 CAPABILITIES OF", self.url)
        print("  ",self._capabilities)

        # avoid building capabilities metadata if the
        # response is a ServiceExceptionReport
        se = self._capabilities.find('ServiceException')
        if se is not None:
            err_message = str(se.text).strip()
            raise ServiceException(err_message, xml)

        # build metadata objects
        self._buildMetadata(parse_remote_metadata)

    def _buildMetadata(self, parse_remote_metadata=False):
        '''set up capabilities metadata objects: '''

        # serviceIdentification metadata
        serviceelem = self._capabilities.find(nspath('Service',
                                              ns=WMS_NAMESPACE))
        self.identification = ServiceIdentification(serviceelem, self.version)

        # serviceProvider metadata
        self.provider = ServiceProvider(serviceelem)

        # serviceOperations metadata
        self.operations = []
        for elem in self._capabilities.find(nspath('Capability/Request',
                                            ns=WMS_NAMESPACE))[:]:
            self.operations.append(OperationMetadata(elem))

        # serviceContents metadata: our assumption is that services use a top-level
        # layer as a metadata organizer, nothing more.
        self.contents = OrderedDict()
        caps = self._capabilities.find(nspath('Capability', WMS_NAMESPACE))

        # recursively gather content metadata for all layer elements.
        # To the WebMapService.contents store only metadata of named layers.
        def gather_layers(parent_elem, parent_metadata):
            for index, elem in enumerate(parent_elem.findall(nspath('Layer', WMS_NAMESPACE))):
                cm = ContentMetadata(elem, parent=parent_metadata, index=index + 1,
                                     parse_remote_metadata=parse_remote_metadata)
                if cm.id:
                    if cm.id in self.contents:
                        warnings.warn('Content metadata for layer "%s" already exists. Using child layer' % cm.id)
                    self.contents[cm.id] = cm
                gather_layers(elem, cm)
        gather_layers(caps, None)

        # exceptions
        self.exceptions = [f.text for f
                           in self._capabilities.findall(nspath('Capability/Exception/Format',
                                                         WMS_NAMESPACE))]

    def items(self):
        '''supports dict-like items() access'''
        items = []
        for item in self.contents:
            items.append((item, self.contents[item]))
        return items

    def getServiceXML(self):
        xml = None
        if self._capabilities is not None:
            xml = etree.tostring(self._capabilities)
        return xml

    def getfeatureinfo(self):
        raise NotImplementedError

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)

    def getmap(self, layers=None,
               styles=None,
               srs=None,
               bbox=None,
               format=None,
               size=None,
               time=None,
               elevation=None,
               dimensions={},
               transparent=False,
               bgcolor='#FFFFFF',
               exceptions='XML',
               method='Get',
               **kwargs
               ):
        """Request and return an image from the WMS as a file-like object.

        Parameters
        ----------
        layers : list
            List of content layer names.
        styles : list
            Optional list of named styles, must be the same length as the
            layers list.
        srs : string
            A spatial reference system identifier.
            Note: this is an invalid query parameter key for 1.3.0 but is being
                  retained for standardization with 1.1.1.
            Note: throws exception if the spatial ref is ESRI's "no reference"
                  code (EPSG:0)
        bbox : tuple
            (left, bottom, right, top) in srs units (note, this order does not
                change depending on axis order of the crs).

            CRS:84: (long, lat)
            EPSG:4326: (lat, long)
        format : string
            Output image format such as 'image/jpeg'.
        size : tuple
            (width, height) in pixels.

        time : string or list or range
            Optional. Time value of the specified layer as ISO-8601 (per value)
        elevation : string or list or range
            Optional. Elevation value of the specified layer.
        dimensions: dict (dimension : string or list or range)
            Optional. Any other Dimension option, as specified in the GetCapabilities

        transparent : bool
            Optional. Transparent background if True.
        bgcolor : string
            Optional. Image background color.
        method : string
            Optional. HTTP DCP method name: Get or Post.
        **kwargs : extra arguments
            anything else e.g. vendor specific parameters

        Example
        -------
            >>> wms = WebMapService('http://webservices.nationalatlas.gov/wms/1million',
                                    version='1.3.0')
            >>> img = wms.getmap(layers=['airports1m'],\
                                 styles=['default'],\
                                 srs='EPSG:4326',\
                                 bbox=(-176.646, 17.7016, -64.8017, 71.2854),\
                                 size=(300, 300),\
                                 format='image/jpeg',\
                                 transparent=True)
            >>> out = open('example.jpg.jpg', 'wb')
            >>> out.write(img.read())
            >>> out.close()

        """

        try:
            base_url = next((m.get('url') for m in
                            self.getOperationByName('GetMap').methods if
                            m.get('type').lower() == method.lower()))
        except StopIteration:
            base_url = self.url
        request = {'version': self.version, 'request': 'GetMap'}

        # check layers and styles
        assert len(layers) > 0
        request['layers'] = ','.join(layers)
        if styles:
            assert len(styles) == len(layers)
            request['styles'] = ','.join(styles)
        else:
            request['styles'] = ''

        # size
        request['width'] = str(size[0])
        request['height'] = str(size[1])

        # remap srs to crs for the actual request
        if srs.upper() == 'EPSG:0':
            # if it's esri's unknown spatial ref code, bail
            raise Exception('Undefined spatial reference (%s).' % srs)
        sref = Crs(srs)
        if sref.axisorder == 'yx':
            # remap the given bbox
            bbox = (bbox[1], bbox[0], bbox[3], bbox[2])

        # remapping the srs to crs for the request
        request['crs'] = str(srs)
        request['bbox'] = ','.join([repr(x) for x in bbox])
        request['format'] = str(format)
        request['transparent'] = str(transparent).upper()
        request['bgcolor'] = '0x' + bgcolor[1:7]
        request['exceptions'] = str(exceptions)

        # the predefined dimensions
        if time is not None:
            request['time'] = str(time)

        if elevation is not None:
            request['elevation'] = str(elevation)

        # any other specified dimension, prefixed with "dim_"
        for k, v in six.iteritems(dimensions):
            request['dim_' + k] = str(v)

        if kwargs:
            for kw in kwargs:
                request[kw] = kwargs[kw]

        if True:
            d = dict()
            for k,v in request.iteritems():
                d[k.upper()] = v
            request = d

        data = urlencode(request)
        print ("URL: ", data)

        u = openURL(base_url,
                    data,
                    method,
                    username=self.username,
                    password=self.password)

        # need to handle casing in the header keys
        headers = {}
        for k, v in six.iteritems(u.info()):
            headers[k.lower()] = v

        if headers['content-type'] in ['application/vnd.ogc.se_xml', 'text/xml']:
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            err_message = unicode(next(iter(se_tree.find('{http://www.opengis.net/ogc}ServiceException/text()')), '')).strip()
            raise ServiceException(err_message, se_xml)
        return u


class ServiceIdentification(object):
    def __init__(self, infoset, version):
        self._root = infoset
        self.type = testXMLValue(self._root.find(nspath('Name', WMS_NAMESPACE)))
        self.version = version
        self.title = testXMLValue(self._root.find(nspath('Title', WMS_NAMESPACE)))
        self.abstract = testXMLValue(self._root.find(nspath('Abstract', WMS_NAMESPACE)))
        self.keywords = extract_xml_list(self._root.findall(nspath('KeywordList/Keyword', WMS_NAMESPACE)))
        self.accessconstraints = testXMLValue(self._root.find(nspath('AccessConstraints', WMS_NAMESPACE)))
        self.fees = testXMLValue(self._root.find(nspath('Fees', WMS_NAMESPACE)))


class ServiceProvider(object):
    def __init__(self, infoset):
        self._root = infoset
        name = self._root.find(nspath('ContactInformation/ContactPersonPrimary/ContactOrganization', WMS_NAMESPACE))
        if name is not None:
            self.name = name.text
        else:
            self.name = None
        self.url = self._root.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib.get('{http://www.w3.org/1999/xlink}href', '')
        # contact metadata
        contact = self._root.find(nspath('ContactInformation', WMS_NAMESPACE))
        # sometimes there is a contact block that is empty, so make
        # sure there are children to parse
        if contact is not None and contact[:] != []:
            self.contact = ContactMetadata(contact)
        else:
            self.contact = None


class ContentMetadata(object):
    def __init__(self, elem, parent=None, index=0, parse_remote_metadata=False, timeout=30):
        if xmltag_split(elem.tag) != 'Layer':
            raise ValueError('%s should be a Layer' % (elem,))

        self.parent = parent
        if parent:
            self.index = "%s.%d" % (parent.index, index)
        else:
            self.index = str(index)

        self.id = self.name = testXMLValue(elem.find(nspath('Name', WMS_NAMESPACE)))

        # layer attributes
        self.queryable = int(elem.attrib.get('queryable', 0))
        self.cascaded = int(elem.attrib.get('cascaded', 0))
        self.opaque = int(elem.attrib.get('opaque', 0))
        self.noSubsets = int(elem.attrib.get('noSubsets', 0))
        self.fixedWidth = int(elem.attrib.get('fixedWidth', 0))
        self.fixedHeight = int(elem.attrib.get('fixedHeight', 0))

        # title is mandatory property
        self.title = None
        title = testXMLValue(elem.find(nspath('Title', WMS_NAMESPACE)))
        if title is not None:
            self.title = title.strip()

        self.abstract = testXMLValue(elem.find(nspath('Abstract', WMS_NAMESPACE)))

        # TODO: what is the preferred response to esri's handling of custom projections
        #       in the spatial ref definitions? see http://resources.arcgis.com/en/help/main/10.1/index.html#//00sq000000m1000000
        #       and an example (20150812) http://maps.ngdc.noaa.gov/arcgis/services/firedetects/MapServer/WMSServer?request=GetCapabilities&service=WMS

        # bboxes
        b = elem.find(nspath('EX_GeographicBoundingBox', WMS_NAMESPACE))
        self.boundingBoxWGS84 = None
        if b is not None:
            minx = b.find(nspath('westBoundLongitude', WMS_NAMESPACE))
            miny = b.find(nspath('southBoundLatitude', WMS_NAMESPACE))
            maxx = b.find(nspath('eastBoundLongitude', WMS_NAMESPACE))
            maxy = b.find(nspath('northBoundLatitude', WMS_NAMESPACE))
            box = tuple(map(float, [minx.text if minx is not None else None,
                              miny.text if miny is not None else None,
                              maxx.text if maxx is not None else None,
                              maxy.text if maxy is not None else None]))

            self.boundingBoxWGS84 = tuple(box)
        elif self.parent:
            if hasattr(self.parent, 'boundingBoxWGS84'):
                self.boundingBoxWGS84 = self.parent.boundingBoxWGS84

        # make a bbox list (of tuples)
        crs_list = []
        for bb in elem.findall(nspath('BoundingBox', WMS_NAMESPACE)):
            srs_str = bb.attrib.get('CRS', None)
            srs = Crs(srs_str)

            box = tuple(map(float, [bb.attrib['minx'],
                        bb.attrib['miny'],
                        bb.attrib['maxx'],
                        bb.attrib['maxy']]
            ))
            minx, miny, maxx, maxy = box[0], box[1], box[2], box[3]

            # handle the ordering so that it always
            # returns (minx, miny, maxx, maxy)
            if srs and srs.axisorder == 'yx':
                # reverse things
                minx, miny, maxx, maxy = box[1], box[0], box[3], box[2]

            crs_list.append((
                minx, miny, maxx, maxy,
                srs_str,
            ))
        self.crs_list = crs_list
        # and maintain the original boundingBox attribute (first in list)
        # or the wgs84 bbox (to handle cases of incomplete parentage)
        self.boundingBox = crs_list[0] if crs_list else self.boundingBoxWGS84

        # ScaleHint
        sh = elem.find(nspath('ScaleHint', WMS_NAMESPACE))
        self.scaleHint = None
        if sh is not None:
            if 'min' in sh.attrib and 'max' in sh.attrib:
                self.scaleHint = {'min': sh.attrib['min'], 'max': sh.attrib['max']}

        attribution = elem.find(nspath('Attribution', WMS_NAMESPACE))
        if attribution is not None:
            self.attribution = dict()
            title = attribution.find(nspath('Title', WMS_NAMESPACE))
            url = attribution.find(nspath('OnlineResource', WMS_NAMESPACE))
            logo = attribution.find(nspath('LogoURL', WMS_NAMESPACE))
            if title is not None:
                self.attribution['title'] = title.text
            if url is not None:
                self.attribution['url'] = url.attrib['{http://www.w3.org/1999/xlink}href']
            if logo is not None:
                self.attribution['logo_size'] = (int(logo.attrib['width']), int(logo.attrib['height']))
                self.attribution['logo_url'] = logo.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']

        # TODO: get this from the bbox attributes instead (deal with parents)
        # SRS options
        self.crsOptions = []

        # Copy any parent SRS options (they are inheritable properties)
        if self.parent:
            self.crsOptions = list(self.parent.crsOptions)

        # Look for SRS option attached to this layer
        if elem.find(nspath('CRS', WMS_NAMESPACE)) is not None:
            # some servers found in the wild use a single SRS
            # tag containing a whitespace separated list of SRIDs
            # instead of several SRS tags. hence the inner loop
            for srslist in map(lambda x: x.text, elem.findall(nspath('CRS', WMS_NAMESPACE))):
                if srslist:
                    for srs in srslist.split():
                        self.crsOptions.append(srs)

        # Get rid of duplicate entries
        self.crsOptions = list(set(self.crsOptions))

        # Set self.crsOptions to None if the layer (and parents) had no SRS options
        if len(self.crsOptions) == 0:
            # raise ValueError('%s no SRS available!?' % (elem,))
            # Comment by D Lowe.
            # Do not raise ValueError as it is possible that a layer is purely a parent layer and does not have SRS specified. Instead set crsOptions to None
            # Comment by Jachym:
            # Do not set it to None, but to [], which will make the code
            # work further. Fixed by anthonybaxter
            self.crsOptions = []

        # Styles
        self.styles = {}

        # Copy any parent styles (they are inheritable properties)
        if self.parent:
            self.styles = self.parent.styles.copy()

        # Get the styles for this layer (items with the same name are replaced)
        for s in elem.findall(nspath('Style', WMS_NAMESPACE)):
            name = s.find(nspath('Name', WMS_NAMESPACE))
            title = s.find(nspath('Title', WMS_NAMESPACE))
            if name is None or title is None:
                raise ValueError('%s missing name or title' % (s,))
            style = {'title': title.text}
            # legend url
            legend = s.find(nspath('LegendURL/OnlineResource', WMS_NAMESPACE))
            if legend is not None:
                style['legend'] = legend.attrib['{http://www.w3.org/1999/xlink}href']

            lgd = s.find(nspath('LegendURL', WMS_NAMESPACE))
            if lgd is not None:
                if 'width' in lgd.attrib.keys():
                    style['legend_width'] = lgd.attrib.get('width')
                if 'height' in lgd.attrib.keys():
                    style['legend_height'] = lgd.attrib.get('height')

                lgd_format = lgd.find(nspath('Format', WMS_NAMESPACE))
                if lgd_format is not None:
                    style['legend_format'] = lgd_format.text.strip()
            self.styles[name.text] = style

        # keywords
        self.keywords = [f.text for f in elem.findall(nspath('KeywordList/Keyword', WMS_NAMESPACE))]

        # extents replaced by dimensions of name
        # comment by Soren Scott
        # <Dimension name="elevation" units="meters" default="500" multipleValues="1"
        #    nearestValue="0" current="true" unitSymbol="m">500, 490, 480</Dimension>
        # it can be repeated with the same name so ? this assumes a single one to match 1.1.1

        self.timepositions = None
        self.defaulttimeposition = None
        time_dimension = next(iter(elem.findall(nspath('Dimension', WMS_NAMESPACE)+'[@name="time"]')), None)
        if time_dimension is not None:
            self.timepositions = time_dimension.text.split(',') if time_dimension.text else None
            self.defaulttimeposition = time_dimension.attrib.get('default', None)

        # Elevations - available vertical levels
        self.elevations = None
        elev_dimension = next(iter(elem.findall(nspath('Dimension', WMS_NAMESPACE)+'[@name="elevation"]')), None)
        if elev_dimension is not None:
            self.elevations = [e.strip() for e in elev_dimension.text.split(',')] if elev_dimension.text else None

        # and now capture the dimensions as more generic things (and custom things)
        self.dimensions = {}
        for dim in elem.findall(nspath('Dimension', WMS_NAMESPACE)):
            dim_name = dim.attrib.get('name')
            dim_data = {k: v for k, v in six.iteritems(dim.attrib) if k !='name'}
            # single values and ranges are not differentiated here
            dim_data['values'] = dim.text.strip().split(',') if dim.text.strip() else None
            self.dimensions[dim_name] = dim_data

        # MetadataURLs
        self.metadataUrls = []
        for m in elem.findall(nspath('MetadataURL', WMS_NAMESPACE)):
            metadataUrl = {
                'type': testXMLValue(m.attrib['type'], attrib=True),
                'format': testXMLValue(m.find(nspath('Format', WMS_NAMESPACE))),
                'url': testXMLValue(m.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href'], attrib=True)
            }

            if metadataUrl['url'] is not None and parse_remote_metadata:  # download URL
                try:
                    content = openURL(metadataUrl['url'], timeout=timeout)
                    doc = etree.parse(content)
                    if metadataUrl['type'] is not None:
                        if metadataUrl['type'] == 'FGDC':
                            metadataUrl['metadata'] = Metadata(doc)
                        if metadataUrl['type'] == 'TC211':
                            metadataUrl['metadata'] = MD_Metadata(doc)
                except Exception:
                    metadataUrl['metadata'] = None

            self.metadataUrls.append(metadataUrl)

        # DataURLs
        self.dataUrls = []
        for m in elem.findall(nspath('DataURL', WMS_NAMESPACE)):
            dataUrl = {
                'format': m.find(nspath('Format', WMS_NAMESPACE)).text.strip(),
                'url': m.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']
            }
            self.dataUrls.append(dataUrl)

        # FeatureListURLs
        self.featureListUrls = []
        for m in elem.findall(nspath('FeatureListURL', WMS_NAMESPACE)):
            featureUrl = {
                'format': m.find(nspath('Format', WMS_NAMESPACE)).text.strip(),
                'url': m.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']
            }
            self.featureListUrls.append(featureUrl)

        self.layers = []
        for child in elem.findall(nspath('Layer', WMS_NAMESPACE)):
            self.layers.append(ContentMetadata(child, self))


class OperationMetadata(object):
    def __init__(self, elem):
        """."""
        self.name = xmltag_split(elem.tag)
        # formatOptions
        self.formatOptions = [f.text for f in elem.findall(nspath('Format', WMS_NAMESPACE))]
        self.methods = []
        for verb in elem.findall(nspath('DCPType/HTTP/*', WMS_NAMESPACE)):
            url = verb.find(nspath('OnlineResource', WMS_NAMESPACE)).attrib['{http://www.w3.org/1999/xlink}href']
            self.methods.append({'type': xmltag_split(verb.tag), 'url': url})


class ContactMetadata(object):
    def __init__(self, elem):
        name = elem.find(nspath('ContactPersonPrimary/ContactPerson', WMS_NAMESPACE))
        if name is not None:
            self.name = name.text
        else:
            self.name = None
        email = elem.find('ContactElectronicMailAddress')
        if email is not None:
            self.email = email.text
        else:
            self.email = None
        self.address = self.city = self.region = None
        self.postcode = self.country = None

        address = elem.find(nspath('ContactAddress', WMS_NAMESPACE))
        if address is not None:
            street = address.find(nspath('Address', WMS_NAMESPACE))
            if street is not None:
                self.address = street.text

            city = address.find(nspath('City', WMS_NAMESPACE))
            if city is not None:
                self.city = city.text

            region = address.find(nspath('StateOrProvince', WMS_NAMESPACE))
            if region is not None:
                self.region = region.text

            postcode = address.find(nspath('PostCode', WMS_NAMESPACE))
            if postcode is not None:
                self.postcode = postcode.text

            country = address.find(nspath('Country', WMS_NAMESPACE))
            if country is not None:
                self.country = country.text

        organization = elem.find(nspath('ContactPersonPrimary/ContactOrganization', WMS_NAMESPACE))
        if organization is not None:
            self.organization = organization.text
        else:
            self.organization = None

        position = elem.find(nspath('ContactPosition', WMS_NAMESPACE))
        if position is not None:
            self.position = position.text
        else:
            self.position = None
