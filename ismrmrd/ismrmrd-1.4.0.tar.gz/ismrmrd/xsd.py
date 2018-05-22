# ismrmrd/xsd.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:8e430fd0cf80804f8a43258f54c17461e9f07a76
# Generated 2018-05-07 09:56:30.880234 by PyXB version 1.2.6 using Python 2.7.14.final.0
# Namespace http://www.ismrm.org/ISMRMRD

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:273be9f6-51cc-11e8-ac07-1831bf4c3ca1')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.6'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('http://www.ismrm.org/ISMRMRD', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 28, 8)
    _Documentation = None
STD_ANON._CF_pattern = pyxb.binding.facets.CF_pattern()
STD_ANON._CF_pattern.addPattern(pattern='[MFO]')
STD_ANON._InitializeFacetMap(STD_ANON._CF_pattern)
_module_typeBindings.STD_ANON = STD_ANON

# Atomic simple type: [anonymous]
class STD_ANON_ (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 55, 8)
    _Documentation = None
STD_ANON_._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_, enum_prefix=None)
STD_ANON_.HFP = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='HFP', tag='HFP')
STD_ANON_.HFS = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='HFS', tag='HFS')
STD_ANON_.HFDR = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='HFDR', tag='HFDR')
STD_ANON_.HFDL = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='HFDL', tag='HFDL')
STD_ANON_.FFP = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='FFP', tag='FFP')
STD_ANON_.FFS = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='FFS', tag='FFS')
STD_ANON_.FFDR = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='FFDR', tag='FFDR')
STD_ANON_.FFDL = STD_ANON_._CF_enumeration.addEnumeration(unicode_value='FFDL', tag='FFDL')
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_enumeration)
_module_typeBindings.STD_ANON_ = STD_ANON_

# Atomic simple type: {http://www.ismrm.org/ISMRMRD}trajectoryType
class trajectoryType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'trajectoryType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 169, 2)
    _Documentation = None
trajectoryType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=trajectoryType, enum_prefix=None)
trajectoryType.cartesian = trajectoryType._CF_enumeration.addEnumeration(unicode_value='cartesian', tag='cartesian')
trajectoryType.epi = trajectoryType._CF_enumeration.addEnumeration(unicode_value='epi', tag='epi')
trajectoryType.radial = trajectoryType._CF_enumeration.addEnumeration(unicode_value='radial', tag='radial')
trajectoryType.goldenangle = trajectoryType._CF_enumeration.addEnumeration(unicode_value='goldenangle', tag='goldenangle')
trajectoryType.spiral = trajectoryType._CF_enumeration.addEnumeration(unicode_value='spiral', tag='spiral')
trajectoryType.other = trajectoryType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
trajectoryType._InitializeFacetMap(trajectoryType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'trajectoryType', trajectoryType)
_module_typeBindings.trajectoryType = trajectoryType

# Atomic simple type: {http://www.ismrm.org/ISMRMRD}calibrationModeType
class calibrationModeType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'calibrationModeType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 251, 2)
    _Documentation = None
calibrationModeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=calibrationModeType, enum_prefix=None)
calibrationModeType.embedded = calibrationModeType._CF_enumeration.addEnumeration(unicode_value='embedded', tag='embedded')
calibrationModeType.interleaved = calibrationModeType._CF_enumeration.addEnumeration(unicode_value='interleaved', tag='interleaved')
calibrationModeType.separate = calibrationModeType._CF_enumeration.addEnumeration(unicode_value='separate', tag='separate')
calibrationModeType.external = calibrationModeType._CF_enumeration.addEnumeration(unicode_value='external', tag='external')
calibrationModeType.other = calibrationModeType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
calibrationModeType._InitializeFacetMap(calibrationModeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'calibrationModeType', calibrationModeType)
_module_typeBindings.calibrationModeType = calibrationModeType

# Atomic simple type: {http://www.ismrm.org/ISMRMRD}interleavingDimensionType
class interleavingDimensionType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'interleavingDimensionType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 261, 2)
    _Documentation = None
interleavingDimensionType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=interleavingDimensionType, enum_prefix=None)
interleavingDimensionType.phase = interleavingDimensionType._CF_enumeration.addEnumeration(unicode_value='phase', tag='phase')
interleavingDimensionType.repetition = interleavingDimensionType._CF_enumeration.addEnumeration(unicode_value='repetition', tag='repetition')
interleavingDimensionType.contrast = interleavingDimensionType._CF_enumeration.addEnumeration(unicode_value='contrast', tag='contrast')
interleavingDimensionType.average = interleavingDimensionType._CF_enumeration.addEnumeration(unicode_value='average', tag='average')
interleavingDimensionType.other = interleavingDimensionType._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
interleavingDimensionType._InitializeFacetMap(interleavingDimensionType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'interleavingDimensionType', interleavingDimensionType)
_module_typeBindings.interleavingDimensionType = interleavingDimensionType

# Atomic simple type: [anonymous]
class STD_ANON_2 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 285, 8)
    _Documentation = None
STD_ANON_2._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_2, enum_prefix=None)
STD_ANON_2.ecg = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='ecg', tag='ecg')
STD_ANON_2.pulse = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='pulse', tag='pulse')
STD_ANON_2.respiratory = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='respiratory', tag='respiratory')
STD_ANON_2.trigger = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='trigger', tag='trigger')
STD_ANON_2.gradientwaveform = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='gradientwaveform', tag='gradientwaveform')
STD_ANON_2.other = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value='other', tag='other')
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_enumeration)
_module_typeBindings.STD_ANON_2 = STD_ANON_2

# Complex type {http://www.ismrm.org/ISMRMRD}ismrmrdHeader with content type ELEMENT_ONLY
class ismrmrdHeader_ (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}ismrmrdHeader with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ismrmrdHeader')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 6, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}version uses Python identifier version
    __version = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'version'), 'version', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDversion', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 8, 8), )

    
    version = property(__version.value, __version.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}subjectInformation uses Python identifier subjectInformation
    __subjectInformation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'subjectInformation'), 'subjectInformation', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDsubjectInformation', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 9, 8), )

    
    subjectInformation = property(__subjectInformation.value, __subjectInformation.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}studyInformation uses Python identifier studyInformation
    __studyInformation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'studyInformation'), 'studyInformation', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDstudyInformation', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 10, 8), )

    
    studyInformation = property(__studyInformation.value, __studyInformation.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}measurementInformation uses Python identifier measurementInformation
    __measurementInformation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'measurementInformation'), 'measurementInformation', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDmeasurementInformation', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 11, 8), )

    
    measurementInformation = property(__measurementInformation.value, __measurementInformation.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}acquisitionSystemInformation uses Python identifier acquisitionSystemInformation
    __acquisitionSystemInformation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'acquisitionSystemInformation'), 'acquisitionSystemInformation', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDacquisitionSystemInformation', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 12, 8), )

    
    acquisitionSystemInformation = property(__acquisitionSystemInformation.value, __acquisitionSystemInformation.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}experimentalConditions uses Python identifier experimentalConditions
    __experimentalConditions = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'experimentalConditions'), 'experimentalConditions', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDexperimentalConditions', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 13, 8), )

    
    experimentalConditions = property(__experimentalConditions.value, __experimentalConditions.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}encoding uses Python identifier encoding
    __encoding = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'encoding'), 'encoding', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDencoding', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 14, 8), )

    
    encoding = property(__encoding.value, __encoding.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}sequenceParameters uses Python identifier sequenceParameters
    __sequenceParameters = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'sequenceParameters'), 'sequenceParameters', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDsequenceParameters', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 15, 8), )

    
    sequenceParameters = property(__sequenceParameters.value, __sequenceParameters.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}userParameters uses Python identifier userParameters
    __userParameters = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameters'), 'userParameters', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDuserParameters', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 16, 8), )

    
    userParameters = property(__userParameters.value, __userParameters.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}waveformInformation uses Python identifier waveformInformation
    __waveformInformation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'waveformInformation'), 'waveformInformation', '__httpwww_ismrm_orgISMRMRD_ismrmrdHeader__httpwww_ismrm_orgISMRMRDwaveformInformation', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 17, 7), )

    
    waveformInformation = property(__waveformInformation.value, __waveformInformation.set, None, None)

    _ElementMap.update({
        __version.name() : __version,
        __subjectInformation.name() : __subjectInformation,
        __studyInformation.name() : __studyInformation,
        __measurementInformation.name() : __measurementInformation,
        __acquisitionSystemInformation.name() : __acquisitionSystemInformation,
        __experimentalConditions.name() : __experimentalConditions,
        __encoding.name() : __encoding,
        __sequenceParameters.name() : __sequenceParameters,
        __userParameters.name() : __userParameters,
        __waveformInformation.name() : __waveformInformation
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ismrmrdHeader_ = ismrmrdHeader_
Namespace.addCategoryObject('typeBinding', 'ismrmrdHeader', ismrmrdHeader_)


# Complex type {http://www.ismrm.org/ISMRMRD}subjectInformationType with content type ELEMENT_ONLY
class subjectInformationType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}subjectInformationType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'subjectInformationType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 21, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}patientName uses Python identifier patientName
    __patientName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'patientName'), 'patientName', '__httpwww_ismrm_orgISMRMRD_subjectInformationType_httpwww_ismrm_orgISMRMRDpatientName', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 23, 6), )

    
    patientName = property(__patientName.value, __patientName.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}patientWeight_kg uses Python identifier patientWeight_kg
    __patientWeight_kg = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'patientWeight_kg'), 'patientWeight_kg', '__httpwww_ismrm_orgISMRMRD_subjectInformationType_httpwww_ismrm_orgISMRMRDpatientWeight_kg', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 24, 6), )

    
    patientWeight_kg = property(__patientWeight_kg.value, __patientWeight_kg.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}patientID uses Python identifier patientID
    __patientID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'patientID'), 'patientID', '__httpwww_ismrm_orgISMRMRD_subjectInformationType_httpwww_ismrm_orgISMRMRDpatientID', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 25, 6), )

    
    patientID = property(__patientID.value, __patientID.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}patientBirthdate uses Python identifier patientBirthdate
    __patientBirthdate = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'patientBirthdate'), 'patientBirthdate', '__httpwww_ismrm_orgISMRMRD_subjectInformationType_httpwww_ismrm_orgISMRMRDpatientBirthdate', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 26, 6), )

    
    patientBirthdate = property(__patientBirthdate.value, __patientBirthdate.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}patientGender uses Python identifier patientGender
    __patientGender = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'patientGender'), 'patientGender', '__httpwww_ismrm_orgISMRMRD_subjectInformationType_httpwww_ismrm_orgISMRMRDpatientGender', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 27, 6), )

    
    patientGender = property(__patientGender.value, __patientGender.set, None, None)

    _ElementMap.update({
        __patientName.name() : __patientName,
        __patientWeight_kg.name() : __patientWeight_kg,
        __patientID.name() : __patientID,
        __patientBirthdate.name() : __patientBirthdate,
        __patientGender.name() : __patientGender
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.subjectInformationType = subjectInformationType
Namespace.addCategoryObject('typeBinding', 'subjectInformationType', subjectInformationType)


# Complex type {http://www.ismrm.org/ISMRMRD}studyInformationType with content type ELEMENT_ONLY
class studyInformationType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}studyInformationType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'studyInformationType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 37, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}studyDate uses Python identifier studyDate
    __studyDate = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'studyDate'), 'studyDate', '__httpwww_ismrm_orgISMRMRD_studyInformationType_httpwww_ismrm_orgISMRMRDstudyDate', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 39, 6), )

    
    studyDate = property(__studyDate.value, __studyDate.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}studyTime uses Python identifier studyTime
    __studyTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'studyTime'), 'studyTime', '__httpwww_ismrm_orgISMRMRD_studyInformationType_httpwww_ismrm_orgISMRMRDstudyTime', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 40, 6), )

    
    studyTime = property(__studyTime.value, __studyTime.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}studyID uses Python identifier studyID
    __studyID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'studyID'), 'studyID', '__httpwww_ismrm_orgISMRMRD_studyInformationType_httpwww_ismrm_orgISMRMRDstudyID', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 41, 6), )

    
    studyID = property(__studyID.value, __studyID.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}accessionNumber uses Python identifier accessionNumber
    __accessionNumber = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'accessionNumber'), 'accessionNumber', '__httpwww_ismrm_orgISMRMRD_studyInformationType_httpwww_ismrm_orgISMRMRDaccessionNumber', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 42, 6), )

    
    accessionNumber = property(__accessionNumber.value, __accessionNumber.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}referringPhysicianName uses Python identifier referringPhysicianName
    __referringPhysicianName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'referringPhysicianName'), 'referringPhysicianName', '__httpwww_ismrm_orgISMRMRD_studyInformationType_httpwww_ismrm_orgISMRMRDreferringPhysicianName', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 43, 6), )

    
    referringPhysicianName = property(__referringPhysicianName.value, __referringPhysicianName.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}studyDescription uses Python identifier studyDescription
    __studyDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'studyDescription'), 'studyDescription', '__httpwww_ismrm_orgISMRMRD_studyInformationType_httpwww_ismrm_orgISMRMRDstudyDescription', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 44, 6), )

    
    studyDescription = property(__studyDescription.value, __studyDescription.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}studyInstanceUID uses Python identifier studyInstanceUID
    __studyInstanceUID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'studyInstanceUID'), 'studyInstanceUID', '__httpwww_ismrm_orgISMRMRD_studyInformationType_httpwww_ismrm_orgISMRMRDstudyInstanceUID', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 45, 6), )

    
    studyInstanceUID = property(__studyInstanceUID.value, __studyInstanceUID.set, None, None)

    _ElementMap.update({
        __studyDate.name() : __studyDate,
        __studyTime.name() : __studyTime,
        __studyID.name() : __studyID,
        __accessionNumber.name() : __accessionNumber,
        __referringPhysicianName.name() : __referringPhysicianName,
        __studyDescription.name() : __studyDescription,
        __studyInstanceUID.name() : __studyInstanceUID
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.studyInformationType = studyInformationType
Namespace.addCategoryObject('typeBinding', 'studyInformationType', studyInformationType)


# Complex type {http://www.ismrm.org/ISMRMRD}measurementInformationType with content type ELEMENT_ONLY
class measurementInformationType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}measurementInformationType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'measurementInformationType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 49, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}measurementID uses Python identifier measurementID
    __measurementID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'measurementID'), 'measurementID', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDmeasurementID', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 51, 6), )

    
    measurementID = property(__measurementID.value, __measurementID.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}seriesDate uses Python identifier seriesDate
    __seriesDate = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'seriesDate'), 'seriesDate', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDseriesDate', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 52, 6), )

    
    seriesDate = property(__seriesDate.value, __seriesDate.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}seriesTime uses Python identifier seriesTime
    __seriesTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'seriesTime'), 'seriesTime', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDseriesTime', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 53, 6), )

    
    seriesTime = property(__seriesTime.value, __seriesTime.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}patientPosition uses Python identifier patientPosition
    __patientPosition = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'patientPosition'), 'patientPosition', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDpatientPosition', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 54, 6), )

    
    patientPosition = property(__patientPosition.value, __patientPosition.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}initialSeriesNumber uses Python identifier initialSeriesNumber
    __initialSeriesNumber = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'initialSeriesNumber'), 'initialSeriesNumber', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDinitialSeriesNumber', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 68, 6), )

    
    initialSeriesNumber = property(__initialSeriesNumber.value, __initialSeriesNumber.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}protocolName uses Python identifier protocolName
    __protocolName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'protocolName'), 'protocolName', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDprotocolName', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 69, 6), )

    
    protocolName = property(__protocolName.value, __protocolName.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}seriesDescription uses Python identifier seriesDescription
    __seriesDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'seriesDescription'), 'seriesDescription', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDseriesDescription', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 70, 6), )

    
    seriesDescription = property(__seriesDescription.value, __seriesDescription.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}measurementDependency uses Python identifier measurementDependency
    __measurementDependency = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'measurementDependency'), 'measurementDependency', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDmeasurementDependency', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 71, 6), )

    
    measurementDependency = property(__measurementDependency.value, __measurementDependency.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}seriesInstanceUIDRoot uses Python identifier seriesInstanceUIDRoot
    __seriesInstanceUIDRoot = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'seriesInstanceUIDRoot'), 'seriesInstanceUIDRoot', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDseriesInstanceUIDRoot', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 72, 6), )

    
    seriesInstanceUIDRoot = property(__seriesInstanceUIDRoot.value, __seriesInstanceUIDRoot.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}frameOfReferenceUID uses Python identifier frameOfReferenceUID
    __frameOfReferenceUID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'frameOfReferenceUID'), 'frameOfReferenceUID', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDframeOfReferenceUID', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 73, 6), )

    
    frameOfReferenceUID = property(__frameOfReferenceUID.value, __frameOfReferenceUID.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}referencedImageSequence uses Python identifier referencedImageSequence
    __referencedImageSequence = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'referencedImageSequence'), 'referencedImageSequence', '__httpwww_ismrm_orgISMRMRD_measurementInformationType_httpwww_ismrm_orgISMRMRDreferencedImageSequence', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 74, 6), )

    
    referencedImageSequence = property(__referencedImageSequence.value, __referencedImageSequence.set, None, None)

    _ElementMap.update({
        __measurementID.name() : __measurementID,
        __seriesDate.name() : __seriesDate,
        __seriesTime.name() : __seriesTime,
        __patientPosition.name() : __patientPosition,
        __initialSeriesNumber.name() : __initialSeriesNumber,
        __protocolName.name() : __protocolName,
        __seriesDescription.name() : __seriesDescription,
        __measurementDependency.name() : __measurementDependency,
        __seriesInstanceUIDRoot.name() : __seriesInstanceUIDRoot,
        __frameOfReferenceUID.name() : __frameOfReferenceUID,
        __referencedImageSequence.name() : __referencedImageSequence
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.measurementInformationType = measurementInformationType
Namespace.addCategoryObject('typeBinding', 'measurementInformationType', measurementInformationType)


# Complex type {http://www.ismrm.org/ISMRMRD}measurementDependencyType with content type ELEMENT_ONLY
class measurementDependencyType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}measurementDependencyType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'measurementDependencyType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 78, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}dependencyType uses Python identifier dependencyType
    __dependencyType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'dependencyType'), 'dependencyType', '__httpwww_ismrm_orgISMRMRD_measurementDependencyType_httpwww_ismrm_orgISMRMRDdependencyType', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 80, 8), )

    
    dependencyType = property(__dependencyType.value, __dependencyType.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}measurementID uses Python identifier measurementID
    __measurementID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'measurementID'), 'measurementID', '__httpwww_ismrm_orgISMRMRD_measurementDependencyType_httpwww_ismrm_orgISMRMRDmeasurementID', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 81, 8), )

    
    measurementID = property(__measurementID.value, __measurementID.set, None, None)

    _ElementMap.update({
        __dependencyType.name() : __dependencyType,
        __measurementID.name() : __measurementID
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.measurementDependencyType = measurementDependencyType
Namespace.addCategoryObject('typeBinding', 'measurementDependencyType', measurementDependencyType)


# Complex type {http://www.ismrm.org/ISMRMRD}coilLabelType with content type ELEMENT_ONLY
class coilLabelType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}coilLabelType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'coilLabelType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 85, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}coilNumber uses Python identifier coilNumber
    __coilNumber = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'coilNumber'), 'coilNumber', '__httpwww_ismrm_orgISMRMRD_coilLabelType_httpwww_ismrm_orgISMRMRDcoilNumber', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 87, 6), )

    
    coilNumber = property(__coilNumber.value, __coilNumber.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}coilName uses Python identifier coilName
    __coilName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'coilName'), 'coilName', '__httpwww_ismrm_orgISMRMRD_coilLabelType_httpwww_ismrm_orgISMRMRDcoilName', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 88, 6), )

    
    coilName = property(__coilName.value, __coilName.set, None, None)

    _ElementMap.update({
        __coilNumber.name() : __coilNumber,
        __coilName.name() : __coilName
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.coilLabelType = coilLabelType
Namespace.addCategoryObject('typeBinding', 'coilLabelType', coilLabelType)


# Complex type {http://www.ismrm.org/ISMRMRD}acquisitionSystemInformationType with content type ELEMENT_ONLY
class acquisitionSystemInformationType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}acquisitionSystemInformationType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'acquisitionSystemInformationType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 92, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}systemVendor uses Python identifier systemVendor
    __systemVendor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'systemVendor'), 'systemVendor', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDsystemVendor', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 94, 6), )

    
    systemVendor = property(__systemVendor.value, __systemVendor.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}systemModel uses Python identifier systemModel
    __systemModel = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'systemModel'), 'systemModel', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDsystemModel', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 95, 6), )

    
    systemModel = property(__systemModel.value, __systemModel.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}systemFieldStrength_T uses Python identifier systemFieldStrength_T
    __systemFieldStrength_T = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'systemFieldStrength_T'), 'systemFieldStrength_T', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDsystemFieldStrength_T', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 96, 6), )

    
    systemFieldStrength_T = property(__systemFieldStrength_T.value, __systemFieldStrength_T.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}relativeReceiverNoiseBandwidth uses Python identifier relativeReceiverNoiseBandwidth
    __relativeReceiverNoiseBandwidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'relativeReceiverNoiseBandwidth'), 'relativeReceiverNoiseBandwidth', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDrelativeReceiverNoiseBandwidth', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 97, 6), )

    
    relativeReceiverNoiseBandwidth = property(__relativeReceiverNoiseBandwidth.value, __relativeReceiverNoiseBandwidth.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}receiverChannels uses Python identifier receiverChannels
    __receiverChannels = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'receiverChannels'), 'receiverChannels', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDreceiverChannels', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 98, 6), )

    
    receiverChannels = property(__receiverChannels.value, __receiverChannels.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}coilLabel uses Python identifier coilLabel
    __coilLabel = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'coilLabel'), 'coilLabel', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDcoilLabel', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 99, 6), )

    
    coilLabel = property(__coilLabel.value, __coilLabel.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}institutionName uses Python identifier institutionName
    __institutionName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'institutionName'), 'institutionName', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDinstitutionName', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 100, 6), )

    
    institutionName = property(__institutionName.value, __institutionName.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}stationName uses Python identifier stationName
    __stationName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'stationName'), 'stationName', '__httpwww_ismrm_orgISMRMRD_acquisitionSystemInformationType_httpwww_ismrm_orgISMRMRDstationName', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 101, 6), )

    
    stationName = property(__stationName.value, __stationName.set, None, None)

    _ElementMap.update({
        __systemVendor.name() : __systemVendor,
        __systemModel.name() : __systemModel,
        __systemFieldStrength_T.name() : __systemFieldStrength_T,
        __relativeReceiverNoiseBandwidth.name() : __relativeReceiverNoiseBandwidth,
        __receiverChannels.name() : __receiverChannels,
        __coilLabel.name() : __coilLabel,
        __institutionName.name() : __institutionName,
        __stationName.name() : __stationName
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.acquisitionSystemInformationType = acquisitionSystemInformationType
Namespace.addCategoryObject('typeBinding', 'acquisitionSystemInformationType', acquisitionSystemInformationType)


# Complex type {http://www.ismrm.org/ISMRMRD}experimentalConditionsType with content type ELEMENT_ONLY
class experimentalConditionsType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}experimentalConditionsType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'experimentalConditionsType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 105, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}H1resonanceFrequency_Hz uses Python identifier H1resonanceFrequency_Hz
    __H1resonanceFrequency_Hz = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'H1resonanceFrequency_Hz'), 'H1resonanceFrequency_Hz', '__httpwww_ismrm_orgISMRMRD_experimentalConditionsType_httpwww_ismrm_orgISMRMRDH1resonanceFrequency_Hz', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 107, 6), )

    
    H1resonanceFrequency_Hz = property(__H1resonanceFrequency_Hz.value, __H1resonanceFrequency_Hz.set, None, None)

    _ElementMap.update({
        __H1resonanceFrequency_Hz.name() : __H1resonanceFrequency_Hz
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.experimentalConditionsType = experimentalConditionsType
Namespace.addCategoryObject('typeBinding', 'experimentalConditionsType', experimentalConditionsType)


# Complex type {http://www.ismrm.org/ISMRMRD}encoding with content type ELEMENT_ONLY
class encoding (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}encoding with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'encoding')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 111, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}encodedSpace uses Python identifier encodedSpace
    __encodedSpace = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'encodedSpace'), 'encodedSpace', '__httpwww_ismrm_orgISMRMRD_encoding_httpwww_ismrm_orgISMRMRDencodedSpace', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 113, 6), )

    
    encodedSpace = property(__encodedSpace.value, __encodedSpace.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}reconSpace uses Python identifier reconSpace
    __reconSpace = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'reconSpace'), 'reconSpace', '__httpwww_ismrm_orgISMRMRD_encoding_httpwww_ismrm_orgISMRMRDreconSpace', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 114, 6), )

    
    reconSpace = property(__reconSpace.value, __reconSpace.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}encodingLimits uses Python identifier encodingLimits
    __encodingLimits = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'encodingLimits'), 'encodingLimits', '__httpwww_ismrm_orgISMRMRD_encoding_httpwww_ismrm_orgISMRMRDencodingLimits', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 115, 6), )

    
    encodingLimits = property(__encodingLimits.value, __encodingLimits.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}trajectory uses Python identifier trajectory
    __trajectory = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'trajectory'), 'trajectory', '__httpwww_ismrm_orgISMRMRD_encoding_httpwww_ismrm_orgISMRMRDtrajectory', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 116, 6), )

    
    trajectory = property(__trajectory.value, __trajectory.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}trajectoryDescription uses Python identifier trajectoryDescription
    __trajectoryDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'trajectoryDescription'), 'trajectoryDescription', '__httpwww_ismrm_orgISMRMRD_encoding_httpwww_ismrm_orgISMRMRDtrajectoryDescription', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 117, 6), )

    
    trajectoryDescription = property(__trajectoryDescription.value, __trajectoryDescription.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}parallelImaging uses Python identifier parallelImaging
    __parallelImaging = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'parallelImaging'), 'parallelImaging', '__httpwww_ismrm_orgISMRMRD_encoding_httpwww_ismrm_orgISMRMRDparallelImaging', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 118, 6), )

    
    parallelImaging = property(__parallelImaging.value, __parallelImaging.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}echoTrainLength uses Python identifier echoTrainLength
    __echoTrainLength = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'echoTrainLength'), 'echoTrainLength', '__httpwww_ismrm_orgISMRMRD_encoding_httpwww_ismrm_orgISMRMRDechoTrainLength', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 119, 6), )

    
    echoTrainLength = property(__echoTrainLength.value, __echoTrainLength.set, None, None)

    _ElementMap.update({
        __encodedSpace.name() : __encodedSpace,
        __reconSpace.name() : __reconSpace,
        __encodingLimits.name() : __encodingLimits,
        __trajectory.name() : __trajectory,
        __trajectoryDescription.name() : __trajectoryDescription,
        __parallelImaging.name() : __parallelImaging,
        __echoTrainLength.name() : __echoTrainLength
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.encoding = encoding
Namespace.addCategoryObject('typeBinding', 'encoding', encoding)


# Complex type {http://www.ismrm.org/ISMRMRD}encodingSpaceType with content type ELEMENT_ONLY
class encodingSpaceType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}encodingSpaceType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'encodingSpaceType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 123, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}matrixSize uses Python identifier matrixSize
    __matrixSize = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'matrixSize'), 'matrixSize', '__httpwww_ismrm_orgISMRMRD_encodingSpaceType_httpwww_ismrm_orgISMRMRDmatrixSize', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 125, 6), )

    
    matrixSize = property(__matrixSize.value, __matrixSize.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}fieldOfView_mm uses Python identifier fieldOfView_mm
    __fieldOfView_mm = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'fieldOfView_mm'), 'fieldOfView_mm', '__httpwww_ismrm_orgISMRMRD_encodingSpaceType_httpwww_ismrm_orgISMRMRDfieldOfView_mm', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 126, 6), )

    
    fieldOfView_mm = property(__fieldOfView_mm.value, __fieldOfView_mm.set, None, None)

    _ElementMap.update({
        __matrixSize.name() : __matrixSize,
        __fieldOfView_mm.name() : __fieldOfView_mm
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.encodingSpaceType = encodingSpaceType
Namespace.addCategoryObject('typeBinding', 'encodingSpaceType', encodingSpaceType)


# Complex type {http://www.ismrm.org/ISMRMRD}matrixSize with content type ELEMENT_ONLY
class matrixSize (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}matrixSize with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'matrixSize')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 130, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}x uses Python identifier x
    __x = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'x'), 'x', '__httpwww_ismrm_orgISMRMRD_matrixSize_httpwww_ismrm_orgISMRMRDx', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 132, 6), )

    
    x = property(__x.value, __x.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}y uses Python identifier y
    __y = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'y'), 'y', '__httpwww_ismrm_orgISMRMRD_matrixSize_httpwww_ismrm_orgISMRMRDy', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 133, 6), )

    
    y = property(__y.value, __y.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}z uses Python identifier z
    __z = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'z'), 'z', '__httpwww_ismrm_orgISMRMRD_matrixSize_httpwww_ismrm_orgISMRMRDz', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 134, 6), )

    
    z = property(__z.value, __z.set, None, None)

    _ElementMap.update({
        __x.name() : __x,
        __y.name() : __y,
        __z.name() : __z
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.matrixSize = matrixSize
Namespace.addCategoryObject('typeBinding', 'matrixSize', matrixSize)


# Complex type {http://www.ismrm.org/ISMRMRD}fieldOfView_mm with content type ELEMENT_ONLY
class fieldOfView_mm (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}fieldOfView_mm with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'fieldOfView_mm')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 138, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}x uses Python identifier x
    __x = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'x'), 'x', '__httpwww_ismrm_orgISMRMRD_fieldOfView_mm_httpwww_ismrm_orgISMRMRDx', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 140, 6), )

    
    x = property(__x.value, __x.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}y uses Python identifier y
    __y = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'y'), 'y', '__httpwww_ismrm_orgISMRMRD_fieldOfView_mm_httpwww_ismrm_orgISMRMRDy', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 141, 6), )

    
    y = property(__y.value, __y.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}z uses Python identifier z
    __z = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'z'), 'z', '__httpwww_ismrm_orgISMRMRD_fieldOfView_mm_httpwww_ismrm_orgISMRMRDz', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 142, 6), )

    
    z = property(__z.value, __z.set, None, None)

    _ElementMap.update({
        __x.name() : __x,
        __y.name() : __y,
        __z.name() : __z
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.fieldOfView_mm = fieldOfView_mm
Namespace.addCategoryObject('typeBinding', 'fieldOfView_mm', fieldOfView_mm)


# Complex type {http://www.ismrm.org/ISMRMRD}limitType with content type ELEMENT_ONLY
class limitType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}limitType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'limitType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 146, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}minimum uses Python identifier minimum
    __minimum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'minimum'), 'minimum', '__httpwww_ismrm_orgISMRMRD_limitType_httpwww_ismrm_orgISMRMRDminimum', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 148, 6), )

    
    minimum = property(__minimum.value, __minimum.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}maximum uses Python identifier maximum
    __maximum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'maximum'), 'maximum', '__httpwww_ismrm_orgISMRMRD_limitType_httpwww_ismrm_orgISMRMRDmaximum', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 149, 6), )

    
    maximum = property(__maximum.value, __maximum.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}center uses Python identifier center
    __center = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'center'), 'center', '__httpwww_ismrm_orgISMRMRD_limitType_httpwww_ismrm_orgISMRMRDcenter', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 150, 6), )

    
    center = property(__center.value, __center.set, None, None)

    _ElementMap.update({
        __minimum.name() : __minimum,
        __maximum.name() : __maximum,
        __center.name() : __center
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.limitType = limitType
Namespace.addCategoryObject('typeBinding', 'limitType', limitType)


# Complex type {http://www.ismrm.org/ISMRMRD}encodingLimitsType with content type ELEMENT_ONLY
class encodingLimitsType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}encodingLimitsType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'encodingLimitsType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 154, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}kspace_encoding_step_0 uses Python identifier kspace_encoding_step_0
    __kspace_encoding_step_0 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_0'), 'kspace_encoding_step_0', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDkspace_encoding_step_0', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 156, 6), )

    
    kspace_encoding_step_0 = property(__kspace_encoding_step_0.value, __kspace_encoding_step_0.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}kspace_encoding_step_1 uses Python identifier kspace_encoding_step_1
    __kspace_encoding_step_1 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_1'), 'kspace_encoding_step_1', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDkspace_encoding_step_1', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 157, 6), )

    
    kspace_encoding_step_1 = property(__kspace_encoding_step_1.value, __kspace_encoding_step_1.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}kspace_encoding_step_2 uses Python identifier kspace_encoding_step_2
    __kspace_encoding_step_2 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_2'), 'kspace_encoding_step_2', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDkspace_encoding_step_2', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 158, 6), )

    
    kspace_encoding_step_2 = property(__kspace_encoding_step_2.value, __kspace_encoding_step_2.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}average uses Python identifier average
    __average = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'average'), 'average', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDaverage', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 159, 6), )

    
    average = property(__average.value, __average.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}slice uses Python identifier slice
    __slice = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'slice'), 'slice', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDslice', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 160, 6), )

    
    slice = property(__slice.value, __slice.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}contrast uses Python identifier contrast
    __contrast = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'contrast'), 'contrast', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDcontrast', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 161, 6), )

    
    contrast = property(__contrast.value, __contrast.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}phase uses Python identifier phase
    __phase = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'phase'), 'phase', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDphase', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 162, 6), )

    
    phase = property(__phase.value, __phase.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}repetition uses Python identifier repetition
    __repetition = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'repetition'), 'repetition', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDrepetition', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 163, 6), )

    
    repetition = property(__repetition.value, __repetition.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}set uses Python identifier set_
    __set = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'set'), 'set_', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDset', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 164, 6), )

    
    set_ = property(__set.value, __set.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}segment uses Python identifier segment
    __segment = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'segment'), 'segment', '__httpwww_ismrm_orgISMRMRD_encodingLimitsType_httpwww_ismrm_orgISMRMRDsegment', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 165, 6), )

    
    segment = property(__segment.value, __segment.set, None, None)

    _ElementMap.update({
        __kspace_encoding_step_0.name() : __kspace_encoding_step_0,
        __kspace_encoding_step_1.name() : __kspace_encoding_step_1,
        __kspace_encoding_step_2.name() : __kspace_encoding_step_2,
        __average.name() : __average,
        __slice.name() : __slice,
        __contrast.name() : __contrast,
        __phase.name() : __phase,
        __repetition.name() : __repetition,
        __set.name() : __set,
        __segment.name() : __segment
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.encodingLimitsType = encodingLimitsType
Namespace.addCategoryObject('typeBinding', 'encodingLimitsType', encodingLimitsType)


# Complex type {http://www.ismrm.org/ISMRMRD}trajectoryDescriptionType with content type ELEMENT_ONLY
class trajectoryDescriptionType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}trajectoryDescriptionType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'trajectoryDescriptionType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 180, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}identifier uses Python identifier identifier
    __identifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'identifier'), 'identifier', '__httpwww_ismrm_orgISMRMRD_trajectoryDescriptionType_httpwww_ismrm_orgISMRMRDidentifier', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 182, 6), )

    
    identifier = property(__identifier.value, __identifier.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}userParameterLong uses Python identifier userParameterLong
    __userParameterLong = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameterLong'), 'userParameterLong', '__httpwww_ismrm_orgISMRMRD_trajectoryDescriptionType_httpwww_ismrm_orgISMRMRDuserParameterLong', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 183, 6), )

    
    userParameterLong = property(__userParameterLong.value, __userParameterLong.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}userParameterDouble uses Python identifier userParameterDouble
    __userParameterDouble = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameterDouble'), 'userParameterDouble', '__httpwww_ismrm_orgISMRMRD_trajectoryDescriptionType_httpwww_ismrm_orgISMRMRDuserParameterDouble', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 184, 6), )

    
    userParameterDouble = property(__userParameterDouble.value, __userParameterDouble.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}comment uses Python identifier comment
    __comment = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'comment'), 'comment', '__httpwww_ismrm_orgISMRMRD_trajectoryDescriptionType_httpwww_ismrm_orgISMRMRDcomment', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 185, 6), )

    
    comment = property(__comment.value, __comment.set, None, None)

    _ElementMap.update({
        __identifier.name() : __identifier,
        __userParameterLong.name() : __userParameterLong,
        __userParameterDouble.name() : __userParameterDouble,
        __comment.name() : __comment
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.trajectoryDescriptionType = trajectoryDescriptionType
Namespace.addCategoryObject('typeBinding', 'trajectoryDescriptionType', trajectoryDescriptionType)


# Complex type {http://www.ismrm.org/ISMRMRD}sequenceParametersType with content type ELEMENT_ONLY
class sequenceParametersType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}sequenceParametersType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'sequenceParametersType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 189, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}TR uses Python identifier TR
    __TR = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TR'), 'TR', '__httpwww_ismrm_orgISMRMRD_sequenceParametersType_httpwww_ismrm_orgISMRMRDTR', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 191, 6), )

    
    TR = property(__TR.value, __TR.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}TE uses Python identifier TE
    __TE = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TE'), 'TE', '__httpwww_ismrm_orgISMRMRD_sequenceParametersType_httpwww_ismrm_orgISMRMRDTE', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 192, 6), )

    
    TE = property(__TE.value, __TE.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}TI uses Python identifier TI
    __TI = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'TI'), 'TI', '__httpwww_ismrm_orgISMRMRD_sequenceParametersType_httpwww_ismrm_orgISMRMRDTI', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 193, 6), )

    
    TI = property(__TI.value, __TI.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}flipAngle_deg uses Python identifier flipAngle_deg
    __flipAngle_deg = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'flipAngle_deg'), 'flipAngle_deg', '__httpwww_ismrm_orgISMRMRD_sequenceParametersType_httpwww_ismrm_orgISMRMRDflipAngle_deg', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 194, 6), )

    
    flipAngle_deg = property(__flipAngle_deg.value, __flipAngle_deg.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}sequence_type uses Python identifier sequence_type
    __sequence_type = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'sequence_type'), 'sequence_type', '__httpwww_ismrm_orgISMRMRD_sequenceParametersType_httpwww_ismrm_orgISMRMRDsequence_type', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 195, 6), )

    
    sequence_type = property(__sequence_type.value, __sequence_type.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}echo_spacing uses Python identifier echo_spacing
    __echo_spacing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'echo_spacing'), 'echo_spacing', '__httpwww_ismrm_orgISMRMRD_sequenceParametersType_httpwww_ismrm_orgISMRMRDecho_spacing', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 196, 6), )

    
    echo_spacing = property(__echo_spacing.value, __echo_spacing.set, None, None)

    _ElementMap.update({
        __TR.name() : __TR,
        __TE.name() : __TE,
        __TI.name() : __TI,
        __flipAngle_deg.name() : __flipAngle_deg,
        __sequence_type.name() : __sequence_type,
        __echo_spacing.name() : __echo_spacing
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.sequenceParametersType = sequenceParametersType
Namespace.addCategoryObject('typeBinding', 'sequenceParametersType', sequenceParametersType)


# Complex type {http://www.ismrm.org/ISMRMRD}userParameterLongType with content type ELEMENT_ONLY
class userParameterLongType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}userParameterLongType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'userParameterLongType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 201, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'name'), 'name', '__httpwww_ismrm_orgISMRMRD_userParameterLongType_httpwww_ismrm_orgISMRMRDname', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 203, 6), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'value'), 'value_', '__httpwww_ismrm_orgISMRMRD_userParameterLongType_httpwww_ismrm_orgISMRMRDvalue', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 204, 6), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __name.name() : __name,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.userParameterLongType = userParameterLongType
Namespace.addCategoryObject('typeBinding', 'userParameterLongType', userParameterLongType)


# Complex type {http://www.ismrm.org/ISMRMRD}userParameterDoubleType with content type ELEMENT_ONLY
class userParameterDoubleType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}userParameterDoubleType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'userParameterDoubleType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 208, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'name'), 'name', '__httpwww_ismrm_orgISMRMRD_userParameterDoubleType_httpwww_ismrm_orgISMRMRDname', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 210, 6), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'value'), 'value_', '__httpwww_ismrm_orgISMRMRD_userParameterDoubleType_httpwww_ismrm_orgISMRMRDvalue', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 211, 6), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __name.name() : __name,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.userParameterDoubleType = userParameterDoubleType
Namespace.addCategoryObject('typeBinding', 'userParameterDoubleType', userParameterDoubleType)


# Complex type {http://www.ismrm.org/ISMRMRD}userParameterStringType with content type ELEMENT_ONLY
class userParameterStringType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}userParameterStringType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'userParameterStringType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 215, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'name'), 'name', '__httpwww_ismrm_orgISMRMRD_userParameterStringType_httpwww_ismrm_orgISMRMRDname', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 217, 6), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'value'), 'value_', '__httpwww_ismrm_orgISMRMRD_userParameterStringType_httpwww_ismrm_orgISMRMRDvalue', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 218, 6), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __name.name() : __name,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.userParameterStringType = userParameterStringType
Namespace.addCategoryObject('typeBinding', 'userParameterStringType', userParameterStringType)


# Complex type {http://www.ismrm.org/ISMRMRD}userParameterBase64Type with content type ELEMENT_ONLY
class userParameterBase64Type (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}userParameterBase64Type with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'userParameterBase64Type')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 222, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'name'), 'name', '__httpwww_ismrm_orgISMRMRD_userParameterBase64Type_httpwww_ismrm_orgISMRMRDname', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 224, 6), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'value'), 'value_', '__httpwww_ismrm_orgISMRMRD_userParameterBase64Type_httpwww_ismrm_orgISMRMRDvalue', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 225, 6), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __name.name() : __name,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.userParameterBase64Type = userParameterBase64Type
Namespace.addCategoryObject('typeBinding', 'userParameterBase64Type', userParameterBase64Type)


# Complex type {http://www.ismrm.org/ISMRMRD}referencedImageSequence with content type ELEMENT_ONLY
class referencedImageSequence (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}referencedImageSequence with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'referencedImageSequence')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 229, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}referencedSOPInstanceUID uses Python identifier referencedSOPInstanceUID
    __referencedSOPInstanceUID = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'referencedSOPInstanceUID'), 'referencedSOPInstanceUID', '__httpwww_ismrm_orgISMRMRD_referencedImageSequence_httpwww_ismrm_orgISMRMRDreferencedSOPInstanceUID', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 231, 6), )

    
    referencedSOPInstanceUID = property(__referencedSOPInstanceUID.value, __referencedSOPInstanceUID.set, None, None)

    _ElementMap.update({
        __referencedSOPInstanceUID.name() : __referencedSOPInstanceUID
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.referencedImageSequence = referencedImageSequence
Namespace.addCategoryObject('typeBinding', 'referencedImageSequence', referencedImageSequence)


# Complex type {http://www.ismrm.org/ISMRMRD}userParameters with content type ELEMENT_ONLY
class userParameters (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}userParameters with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'userParameters')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 235, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}userParameterLong uses Python identifier userParameterLong
    __userParameterLong = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameterLong'), 'userParameterLong', '__httpwww_ismrm_orgISMRMRD_userParameters_httpwww_ismrm_orgISMRMRDuserParameterLong', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 237, 6), )

    
    userParameterLong = property(__userParameterLong.value, __userParameterLong.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}userParameterDouble uses Python identifier userParameterDouble
    __userParameterDouble = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameterDouble'), 'userParameterDouble', '__httpwww_ismrm_orgISMRMRD_userParameters_httpwww_ismrm_orgISMRMRDuserParameterDouble', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 238, 6), )

    
    userParameterDouble = property(__userParameterDouble.value, __userParameterDouble.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}userParameterString uses Python identifier userParameterString
    __userParameterString = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameterString'), 'userParameterString', '__httpwww_ismrm_orgISMRMRD_userParameters_httpwww_ismrm_orgISMRMRDuserParameterString', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 239, 6), )

    
    userParameterString = property(__userParameterString.value, __userParameterString.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}userParameterBase64 uses Python identifier userParameterBase64
    __userParameterBase64 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameterBase64'), 'userParameterBase64', '__httpwww_ismrm_orgISMRMRD_userParameters_httpwww_ismrm_orgISMRMRDuserParameterBase64', True, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 240, 6), )

    
    userParameterBase64 = property(__userParameterBase64.value, __userParameterBase64.set, None, None)

    _ElementMap.update({
        __userParameterLong.name() : __userParameterLong,
        __userParameterDouble.name() : __userParameterDouble,
        __userParameterString.name() : __userParameterString,
        __userParameterBase64.name() : __userParameterBase64
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.userParameters = userParameters
Namespace.addCategoryObject('typeBinding', 'userParameters', userParameters)


# Complex type {http://www.ismrm.org/ISMRMRD}accelerationFactorType with content type ELEMENT_ONLY
class accelerationFactorType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}accelerationFactorType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'accelerationFactorType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 244, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}kspace_encoding_step_1 uses Python identifier kspace_encoding_step_1
    __kspace_encoding_step_1 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_1'), 'kspace_encoding_step_1', '__httpwww_ismrm_orgISMRMRD_accelerationFactorType_httpwww_ismrm_orgISMRMRDkspace_encoding_step_1', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 246, 6), )

    
    kspace_encoding_step_1 = property(__kspace_encoding_step_1.value, __kspace_encoding_step_1.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}kspace_encoding_step_2 uses Python identifier kspace_encoding_step_2
    __kspace_encoding_step_2 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_2'), 'kspace_encoding_step_2', '__httpwww_ismrm_orgISMRMRD_accelerationFactorType_httpwww_ismrm_orgISMRMRDkspace_encoding_step_2', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 247, 6), )

    
    kspace_encoding_step_2 = property(__kspace_encoding_step_2.value, __kspace_encoding_step_2.set, None, None)

    _ElementMap.update({
        __kspace_encoding_step_1.name() : __kspace_encoding_step_1,
        __kspace_encoding_step_2.name() : __kspace_encoding_step_2
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.accelerationFactorType = accelerationFactorType
Namespace.addCategoryObject('typeBinding', 'accelerationFactorType', accelerationFactorType)


# Complex type {http://www.ismrm.org/ISMRMRD}parallelImagingType with content type ELEMENT_ONLY
class parallelImagingType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}parallelImagingType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'parallelImagingType')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 271, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}accelerationFactor uses Python identifier accelerationFactor
    __accelerationFactor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'accelerationFactor'), 'accelerationFactor', '__httpwww_ismrm_orgISMRMRD_parallelImagingType_httpwww_ismrm_orgISMRMRDaccelerationFactor', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 273, 4), )

    
    accelerationFactor = property(__accelerationFactor.value, __accelerationFactor.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}calibrationMode uses Python identifier calibrationMode
    __calibrationMode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'calibrationMode'), 'calibrationMode', '__httpwww_ismrm_orgISMRMRD_parallelImagingType_httpwww_ismrm_orgISMRMRDcalibrationMode', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 274, 4), )

    
    calibrationMode = property(__calibrationMode.value, __calibrationMode.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}interleavingDimension uses Python identifier interleavingDimension
    __interleavingDimension = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'interleavingDimension'), 'interleavingDimension', '__httpwww_ismrm_orgISMRMRD_parallelImagingType_httpwww_ismrm_orgISMRMRDinterleavingDimension', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 275, 4), )

    
    interleavingDimension = property(__interleavingDimension.value, __interleavingDimension.set, None, None)

    _ElementMap.update({
        __accelerationFactor.name() : __accelerationFactor,
        __calibrationMode.name() : __calibrationMode,
        __interleavingDimension.name() : __interleavingDimension
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.parallelImagingType = parallelImagingType
Namespace.addCategoryObject('typeBinding', 'parallelImagingType', parallelImagingType)


# Complex type {http://www.ismrm.org/ISMRMRD}waveformInformation with content type ELEMENT_ONLY
class waveformInformation (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.ismrm.org/ISMRMRD}waveformInformation with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'waveformInformation')
    _XSDLocation = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 281, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.ismrm.org/ISMRMRD}waveformName uses Python identifier waveformName
    __waveformName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'waveformName'), 'waveformName', '__httpwww_ismrm_orgISMRMRD_waveformInformation_httpwww_ismrm_orgISMRMRDwaveformName', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 283, 6), )

    
    waveformName = property(__waveformName.value, __waveformName.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}waveformType uses Python identifier waveformType
    __waveformType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'waveformType'), 'waveformType', '__httpwww_ismrm_orgISMRMRD_waveformInformation_httpwww_ismrm_orgISMRMRDwaveformType', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 284, 6), )

    
    waveformType = property(__waveformType.value, __waveformType.set, None, None)

    
    # Element {http://www.ismrm.org/ISMRMRD}userParameters uses Python identifier userParameters
    __userParameters = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'userParameters'), 'userParameters', '__httpwww_ismrm_orgISMRMRD_waveformInformation_httpwww_ismrm_orgISMRMRDuserParameters', False, pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 296, 4), )

    
    userParameters = property(__userParameters.value, __userParameters.set, None, None)

    _ElementMap.update({
        __waveformName.name() : __waveformName,
        __waveformType.name() : __waveformType,
        __userParameters.name() : __userParameters
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.waveformInformation = waveformInformation
Namespace.addCategoryObject('typeBinding', 'waveformInformation', waveformInformation)


ismrmrdHeader = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ismrmrdHeader'), ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 4, 4))
Namespace.addCategoryObject('elementBinding', ismrmrdHeader.name().localName(), ismrmrdHeader)



ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'version'), pyxb.binding.datatypes.long, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 8, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'subjectInformation'), subjectInformationType, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 9, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'studyInformation'), studyInformationType, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 10, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'measurementInformation'), measurementInformationType, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 11, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'acquisitionSystemInformation'), acquisitionSystemInformationType, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 12, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'experimentalConditions'), experimentalConditionsType, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 13, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'encoding'), encoding, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 14, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'sequenceParameters'), sequenceParametersType, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 15, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameters'), userParameters, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 16, 8)))

ismrmrdHeader_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'waveformInformation'), waveformInformation, scope=ismrmrdHeader_, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 17, 7)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 8, 8))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 9, 8))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 10, 8))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 11, 8))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 12, 8))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 15, 8))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 16, 8))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=32, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 17, 7))
    counters.add(cc_7)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'version')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 8, 8))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'subjectInformation')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 9, 8))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'studyInformation')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 10, 8))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'measurementInformation')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 11, 8))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'acquisitionSystemInformation')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 12, 8))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'experimentalConditions')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 13, 8))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'encoding')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 14, 8))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'sequenceParameters')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 15, 8))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameters')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 16, 8))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(ismrmrdHeader_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'waveformInformation')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 17, 7))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ismrmrdHeader_._Automaton = _BuildAutomaton()




subjectInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'patientName'), pyxb.binding.datatypes.string, scope=subjectInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 23, 6)))

subjectInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'patientWeight_kg'), pyxb.binding.datatypes.float, scope=subjectInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 24, 6)))

subjectInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'patientID'), pyxb.binding.datatypes.string, scope=subjectInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 25, 6)))

subjectInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'patientBirthdate'), pyxb.binding.datatypes.date, scope=subjectInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 26, 6)))

subjectInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'patientGender'), STD_ANON, scope=subjectInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 27, 6)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 23, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(subjectInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'patientName')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 23, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 24, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(subjectInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'patientWeight_kg')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 24, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 25, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(subjectInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'patientID')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 25, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 26, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(subjectInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'patientBirthdate')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 26, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 27, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(subjectInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'patientGender')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 27, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 23, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 24, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 25, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 26, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 27, 6))
    counters.add(cc_4)
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_2())
    sub_automata.append(_BuildAutomaton_3())
    sub_automata.append(_BuildAutomaton_4())
    sub_automata.append(_BuildAutomaton_5())
    sub_automata.append(_BuildAutomaton_6())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 22, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
subjectInformationType._Automaton = _BuildAutomaton_()




studyInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'studyDate'), pyxb.binding.datatypes.date, scope=studyInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 39, 6)))

studyInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'studyTime'), pyxb.binding.datatypes.time, scope=studyInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 40, 6)))

studyInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'studyID'), pyxb.binding.datatypes.string, scope=studyInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 41, 6)))

studyInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'accessionNumber'), pyxb.binding.datatypes.long, scope=studyInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 42, 6)))

studyInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'referringPhysicianName'), pyxb.binding.datatypes.string, scope=studyInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 43, 6)))

studyInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'studyDescription'), pyxb.binding.datatypes.string, scope=studyInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 44, 6)))

studyInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'studyInstanceUID'), pyxb.binding.datatypes.string, scope=studyInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 45, 6)))

def _BuildAutomaton_8 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 39, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(studyInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'studyDate')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 39, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_9 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 40, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(studyInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'studyTime')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 40, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_10 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 41, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(studyInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'studyID')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 41, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_11 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 42, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(studyInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'accessionNumber')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 42, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_12 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_12
    del _BuildAutomaton_12
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 43, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(studyInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'referringPhysicianName')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 43, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_13 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_13
    del _BuildAutomaton_13
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 44, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(studyInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'studyDescription')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 44, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_14 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_14
    del _BuildAutomaton_14
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 45, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(studyInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'studyInstanceUID')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 45, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 39, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 40, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 41, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 42, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 43, 6))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 44, 6))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 45, 6))
    counters.add(cc_6)
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_8())
    sub_automata.append(_BuildAutomaton_9())
    sub_automata.append(_BuildAutomaton_10())
    sub_automata.append(_BuildAutomaton_11())
    sub_automata.append(_BuildAutomaton_12())
    sub_automata.append(_BuildAutomaton_13())
    sub_automata.append(_BuildAutomaton_14())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 38, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
studyInformationType._Automaton = _BuildAutomaton_7()




measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'measurementID'), pyxb.binding.datatypes.string, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 51, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'seriesDate'), pyxb.binding.datatypes.date, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 52, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'seriesTime'), pyxb.binding.datatypes.time, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 53, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'patientPosition'), STD_ANON_, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 54, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'initialSeriesNumber'), pyxb.binding.datatypes.long, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 68, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'protocolName'), pyxb.binding.datatypes.string, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 69, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'seriesDescription'), pyxb.binding.datatypes.string, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 70, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'measurementDependency'), measurementDependencyType, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 71, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'seriesInstanceUIDRoot'), pyxb.binding.datatypes.string, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 72, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'frameOfReferenceUID'), pyxb.binding.datatypes.string, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 73, 6)))

measurementInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'referencedImageSequence'), referencedImageSequence, scope=measurementInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 74, 6)))

def _BuildAutomaton_15 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_15
    del _BuildAutomaton_15
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 51, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 52, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 53, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 68, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 69, 6))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 70, 6))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 71, 6))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 72, 6))
    counters.add(cc_7)
    cc_8 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 73, 6))
    counters.add(cc_8)
    cc_9 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 74, 6))
    counters.add(cc_9)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'measurementID')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 51, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'seriesDate')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 52, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'seriesTime')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 53, 6))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'patientPosition')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 54, 6))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'initialSeriesNumber')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 68, 6))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'protocolName')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 69, 6))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'seriesDescription')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 70, 6))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'measurementDependency')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 71, 6))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'seriesInstanceUIDRoot')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 72, 6))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_8, False))
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'frameOfReferenceUID')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 73, 6))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_9, False))
    symbol = pyxb.binding.content.ElementUse(measurementInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'referencedImageSequence')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 74, 6))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    transitions.append(fac.Transition(st_8, [
         ]))
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_6, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
        fac.UpdateInstruction(cc_7, True) ]))
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_7, False) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_7, False) ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_8, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_8, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_9, True) ]))
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
measurementInformationType._Automaton = _BuildAutomaton_15()




measurementDependencyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'dependencyType'), pyxb.binding.datatypes.string, scope=measurementDependencyType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 80, 8)))

measurementDependencyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'measurementID'), pyxb.binding.datatypes.string, scope=measurementDependencyType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 81, 8)))

def _BuildAutomaton_16 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_16
    del _BuildAutomaton_16
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(measurementDependencyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'dependencyType')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 80, 8))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(measurementDependencyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'measurementID')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 81, 8))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
measurementDependencyType._Automaton = _BuildAutomaton_16()




coilLabelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'coilNumber'), pyxb.binding.datatypes.unsignedShort, scope=coilLabelType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 87, 6)))

coilLabelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'coilName'), pyxb.binding.datatypes.string, scope=coilLabelType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 88, 6)))

def _BuildAutomaton_17 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_17
    del _BuildAutomaton_17
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(coilLabelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'coilNumber')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 87, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(coilLabelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'coilName')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 88, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
coilLabelType._Automaton = _BuildAutomaton_17()




acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'systemVendor'), pyxb.binding.datatypes.string, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 94, 6)))

acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'systemModel'), pyxb.binding.datatypes.string, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 95, 6)))

acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'systemFieldStrength_T'), pyxb.binding.datatypes.float, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 96, 6)))

acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'relativeReceiverNoiseBandwidth'), pyxb.binding.datatypes.float, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 97, 6)))

acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'receiverChannels'), pyxb.binding.datatypes.unsignedShort, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 98, 6)))

acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'coilLabel'), coilLabelType, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 99, 6)))

acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'institutionName'), pyxb.binding.datatypes.string, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 100, 6)))

acquisitionSystemInformationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'stationName'), pyxb.binding.datatypes.string, scope=acquisitionSystemInformationType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 101, 6)))

def _BuildAutomaton_18 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_18
    del _BuildAutomaton_18
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 94, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 95, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 96, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 97, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 98, 6))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 99, 6))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 100, 6))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 101, 6))
    counters.add(cc_7)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'systemVendor')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 94, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'systemModel')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 95, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'systemFieldStrength_T')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 96, 6))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'relativeReceiverNoiseBandwidth')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 97, 6))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'receiverChannels')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 98, 6))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'coilLabel')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 99, 6))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_6, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'institutionName')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 100, 6))
    st_6 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_7, False))
    symbol = pyxb.binding.content.ElementUse(acquisitionSystemInformationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'stationName')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 101, 6))
    st_7 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_4, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_5, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_6, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_6, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_7, True) ]))
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
acquisitionSystemInformationType._Automaton = _BuildAutomaton_18()




experimentalConditionsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'H1resonanceFrequency_Hz'), pyxb.binding.datatypes.long, scope=experimentalConditionsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 107, 6)))

def _BuildAutomaton_19 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_19
    del _BuildAutomaton_19
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(experimentalConditionsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'H1resonanceFrequency_Hz')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 107, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
experimentalConditionsType._Automaton = _BuildAutomaton_19()




encoding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'encodedSpace'), encodingSpaceType, scope=encoding, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 113, 6)))

encoding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'reconSpace'), encodingSpaceType, scope=encoding, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 114, 6)))

encoding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'encodingLimits'), encodingLimitsType, scope=encoding, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 115, 6)))

encoding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'trajectory'), trajectoryType, scope=encoding, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 116, 6)))

encoding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'trajectoryDescription'), trajectoryDescriptionType, scope=encoding, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 117, 6)))

encoding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'parallelImaging'), parallelImagingType, scope=encoding, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 118, 6)))

encoding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'echoTrainLength'), pyxb.binding.datatypes.long, scope=encoding, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 119, 6)))

def _BuildAutomaton_21 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_21
    del _BuildAutomaton_21
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(encoding._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'encodedSpace')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 113, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_22 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_22
    del _BuildAutomaton_22
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(encoding._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'reconSpace')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 114, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_23 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_23
    del _BuildAutomaton_23
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(encoding._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'encodingLimits')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 115, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_24 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_24
    del _BuildAutomaton_24
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(encoding._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'trajectory')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 116, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_25 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_25
    del _BuildAutomaton_25
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 117, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encoding._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'trajectoryDescription')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 117, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_26 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_26
    del _BuildAutomaton_26
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 118, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encoding._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'parallelImaging')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 118, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_27 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_27
    del _BuildAutomaton_27
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 119, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encoding._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'echoTrainLength')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 119, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_20 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_20
    del _BuildAutomaton_20
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 117, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 118, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 119, 6))
    counters.add(cc_2)
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_21())
    sub_automata.append(_BuildAutomaton_22())
    sub_automata.append(_BuildAutomaton_23())
    sub_automata.append(_BuildAutomaton_24())
    sub_automata.append(_BuildAutomaton_25())
    sub_automata.append(_BuildAutomaton_26())
    sub_automata.append(_BuildAutomaton_27())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 112, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
encoding._Automaton = _BuildAutomaton_20()




encodingSpaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'matrixSize'), matrixSize, scope=encodingSpaceType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 125, 6)))

encodingSpaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'fieldOfView_mm'), fieldOfView_mm, scope=encodingSpaceType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 126, 6)))

def _BuildAutomaton_29 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_29
    del _BuildAutomaton_29
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(encodingSpaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'matrixSize')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 125, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_30 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_30
    del _BuildAutomaton_30
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(encodingSpaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'fieldOfView_mm')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 126, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_28 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_28
    del _BuildAutomaton_28
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_29())
    sub_automata.append(_BuildAutomaton_30())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 124, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
encodingSpaceType._Automaton = _BuildAutomaton_28()




matrixSize._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'x'), pyxb.binding.datatypes.unsignedShort, scope=matrixSize, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 132, 6), unicode_default='1'))

matrixSize._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'y'), pyxb.binding.datatypes.unsignedShort, scope=matrixSize, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 133, 6), unicode_default='1'))

matrixSize._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'z'), pyxb.binding.datatypes.unsignedShort, scope=matrixSize, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 134, 6), unicode_default='1'))

def _BuildAutomaton_31 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_31
    del _BuildAutomaton_31
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(matrixSize._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'x')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 132, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(matrixSize._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'y')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 133, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(matrixSize._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'z')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 134, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
matrixSize._Automaton = _BuildAutomaton_31()




fieldOfView_mm._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'x'), pyxb.binding.datatypes.float, scope=fieldOfView_mm, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 140, 6)))

fieldOfView_mm._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'y'), pyxb.binding.datatypes.float, scope=fieldOfView_mm, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 141, 6)))

fieldOfView_mm._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'z'), pyxb.binding.datatypes.float, scope=fieldOfView_mm, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 142, 6)))

def _BuildAutomaton_32 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_32
    del _BuildAutomaton_32
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(fieldOfView_mm._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'x')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 140, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(fieldOfView_mm._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'y')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 141, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(fieldOfView_mm._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'z')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 142, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
fieldOfView_mm._Automaton = _BuildAutomaton_32()




limitType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'minimum'), pyxb.binding.datatypes.unsignedShort, scope=limitType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 148, 6), unicode_default='0'))

limitType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'maximum'), pyxb.binding.datatypes.unsignedShort, scope=limitType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 149, 6), unicode_default='0'))

limitType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'center'), pyxb.binding.datatypes.unsignedShort, scope=limitType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 150, 6), unicode_default='0'))

def _BuildAutomaton_34 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_34
    del _BuildAutomaton_34
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(limitType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'minimum')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 148, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_35 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_35
    del _BuildAutomaton_35
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(limitType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'maximum')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 149, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_36 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_36
    del _BuildAutomaton_36
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(limitType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'center')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 150, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_33 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_33
    del _BuildAutomaton_33
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_34())
    sub_automata.append(_BuildAutomaton_35())
    sub_automata.append(_BuildAutomaton_36())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 147, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
limitType._Automaton = _BuildAutomaton_33()




encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_0'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 156, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_1'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 157, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_2'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 158, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'average'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 159, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'slice'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 160, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'contrast'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 161, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'phase'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 162, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'repetition'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 163, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'set'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 164, 6)))

encodingLimitsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'segment'), limitType, scope=encodingLimitsType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 165, 6)))

def _BuildAutomaton_38 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_38
    del _BuildAutomaton_38
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 156, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_0')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 156, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_39 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_39
    del _BuildAutomaton_39
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 157, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_1')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 157, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_40 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_40
    del _BuildAutomaton_40
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 158, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_2')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 158, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_41 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_41
    del _BuildAutomaton_41
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 159, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'average')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 159, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_42 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_42
    del _BuildAutomaton_42
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 160, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'slice')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 160, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_43 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_43
    del _BuildAutomaton_43
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 161, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'contrast')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 161, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_44 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_44
    del _BuildAutomaton_44
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 162, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'phase')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 162, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_45 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_45
    del _BuildAutomaton_45
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 163, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'repetition')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 163, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_46 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_46
    del _BuildAutomaton_46
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 164, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'set')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 164, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_47 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_47
    del _BuildAutomaton_47
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 165, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(encodingLimitsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'segment')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 165, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=st_0)

def _BuildAutomaton_37 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_37
    del _BuildAutomaton_37
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 156, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 157, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 158, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 159, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 160, 6))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 161, 6))
    counters.add(cc_5)
    cc_6 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 162, 6))
    counters.add(cc_6)
    cc_7 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 163, 6))
    counters.add(cc_7)
    cc_8 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 164, 6))
    counters.add(cc_8)
    cc_9 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 165, 6))
    counters.add(cc_9)
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_38())
    sub_automata.append(_BuildAutomaton_39())
    sub_automata.append(_BuildAutomaton_40())
    sub_automata.append(_BuildAutomaton_41())
    sub_automata.append(_BuildAutomaton_42())
    sub_automata.append(_BuildAutomaton_43())
    sub_automata.append(_BuildAutomaton_44())
    sub_automata.append(_BuildAutomaton_45())
    sub_automata.append(_BuildAutomaton_46())
    sub_automata.append(_BuildAutomaton_47())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 155, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
encodingLimitsType._Automaton = _BuildAutomaton_37()




trajectoryDescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'identifier'), pyxb.binding.datatypes.string, scope=trajectoryDescriptionType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 182, 6)))

trajectoryDescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameterLong'), userParameterLongType, scope=trajectoryDescriptionType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 183, 6)))

trajectoryDescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameterDouble'), userParameterDoubleType, scope=trajectoryDescriptionType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 184, 6)))

trajectoryDescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'comment'), pyxb.binding.datatypes.string, scope=trajectoryDescriptionType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 185, 6)))

def _BuildAutomaton_48 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_48
    del _BuildAutomaton_48
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 183, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 184, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 185, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(trajectoryDescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'identifier')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 182, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(trajectoryDescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameterLong')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 183, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(trajectoryDescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameterDouble')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 184, 6))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(trajectoryDescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'comment')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 185, 6))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
trajectoryDescriptionType._Automaton = _BuildAutomaton_48()




sequenceParametersType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TR'), pyxb.binding.datatypes.float, scope=sequenceParametersType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 191, 6)))

sequenceParametersType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TE'), pyxb.binding.datatypes.float, scope=sequenceParametersType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 192, 6)))

sequenceParametersType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'TI'), pyxb.binding.datatypes.float, scope=sequenceParametersType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 193, 6)))

sequenceParametersType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'flipAngle_deg'), pyxb.binding.datatypes.float, scope=sequenceParametersType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 194, 6)))

sequenceParametersType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'sequence_type'), pyxb.binding.datatypes.string, scope=sequenceParametersType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 195, 6)))

sequenceParametersType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'echo_spacing'), pyxb.binding.datatypes.float, scope=sequenceParametersType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 196, 6)))

def _BuildAutomaton_49 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_49
    del _BuildAutomaton_49
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 191, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 192, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 193, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 194, 6))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 195, 6))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 196, 6))
    counters.add(cc_5)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(sequenceParametersType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TR')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 191, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(sequenceParametersType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TE')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 192, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(sequenceParametersType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'TI')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 193, 6))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(sequenceParametersType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'flipAngle_deg')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 194, 6))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(sequenceParametersType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'sequence_type')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 195, 6))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(sequenceParametersType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'echo_spacing')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 196, 6))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_5, True) ]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
sequenceParametersType._Automaton = _BuildAutomaton_49()




userParameterLongType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'name'), pyxb.binding.datatypes.string, scope=userParameterLongType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 203, 6)))

userParameterLongType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'value'), pyxb.binding.datatypes.long, scope=userParameterLongType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 204, 6)))

def _BuildAutomaton_51 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_51
    del _BuildAutomaton_51
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterLongType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'name')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 203, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_52 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_52
    del _BuildAutomaton_52
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterLongType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'value')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 204, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_50 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_50
    del _BuildAutomaton_50
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_51())
    sub_automata.append(_BuildAutomaton_52())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 202, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
userParameterLongType._Automaton = _BuildAutomaton_50()




userParameterDoubleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'name'), pyxb.binding.datatypes.string, scope=userParameterDoubleType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 210, 6)))

userParameterDoubleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'value'), pyxb.binding.datatypes.double, scope=userParameterDoubleType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 211, 6)))

def _BuildAutomaton_54 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_54
    del _BuildAutomaton_54
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterDoubleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'name')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 210, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_55 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_55
    del _BuildAutomaton_55
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterDoubleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'value')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 211, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_53 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_53
    del _BuildAutomaton_53
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_54())
    sub_automata.append(_BuildAutomaton_55())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 209, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
userParameterDoubleType._Automaton = _BuildAutomaton_53()




userParameterStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'name'), pyxb.binding.datatypes.string, scope=userParameterStringType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 217, 6)))

userParameterStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'value'), pyxb.binding.datatypes.string, scope=userParameterStringType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 218, 6)))

def _BuildAutomaton_57 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_57
    del _BuildAutomaton_57
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'name')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 217, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_58 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_58
    del _BuildAutomaton_58
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'value')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 218, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_56 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_56
    del _BuildAutomaton_56
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_57())
    sub_automata.append(_BuildAutomaton_58())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 216, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
userParameterStringType._Automaton = _BuildAutomaton_56()




userParameterBase64Type._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'name'), pyxb.binding.datatypes.string, scope=userParameterBase64Type, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 224, 6)))

userParameterBase64Type._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'value'), pyxb.binding.datatypes.base64Binary, scope=userParameterBase64Type, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 225, 6)))

def _BuildAutomaton_60 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_60
    del _BuildAutomaton_60
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterBase64Type._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'name')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 224, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_61 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_61
    del _BuildAutomaton_61
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(userParameterBase64Type._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'value')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 225, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_59 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_59
    del _BuildAutomaton_59
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_60())
    sub_automata.append(_BuildAutomaton_61())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 223, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
userParameterBase64Type._Automaton = _BuildAutomaton_59()




referencedImageSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'referencedSOPInstanceUID'), pyxb.binding.datatypes.string, scope=referencedImageSequence, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 231, 6)))

def _BuildAutomaton_62 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_62
    del _BuildAutomaton_62
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 231, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(referencedImageSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'referencedSOPInstanceUID')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 231, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
referencedImageSequence._Automaton = _BuildAutomaton_62()




userParameters._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameterLong'), userParameterLongType, scope=userParameters, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 237, 6)))

userParameters._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameterDouble'), userParameterDoubleType, scope=userParameters, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 238, 6)))

userParameters._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameterString'), userParameterStringType, scope=userParameters, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 239, 6)))

userParameters._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameterBase64'), userParameterBase64Type, scope=userParameters, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 240, 6)))

def _BuildAutomaton_63 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_63
    del _BuildAutomaton_63
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 237, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 238, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 239, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 240, 6))
    counters.add(cc_3)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(userParameters._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameterLong')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 237, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(userParameters._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameterDouble')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 238, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(userParameters._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameterString')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 239, 6))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(userParameters._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameterBase64')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 240, 6))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
userParameters._Automaton = _BuildAutomaton_63()




accelerationFactorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_1'), pyxb.binding.datatypes.unsignedShort, scope=accelerationFactorType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 246, 6)))

accelerationFactorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_2'), pyxb.binding.datatypes.unsignedShort, scope=accelerationFactorType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 247, 6)))

def _BuildAutomaton_65 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_65
    del _BuildAutomaton_65
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(accelerationFactorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_1')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 246, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_66 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_66
    del _BuildAutomaton_66
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(accelerationFactorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'kspace_encoding_step_2')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 247, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=st_0)

def _BuildAutomaton_64 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_64
    del _BuildAutomaton_64
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    sub_automata = []
    sub_automata.append(_BuildAutomaton_65())
    sub_automata.append(_BuildAutomaton_66())
    final_update = set()
    symbol = pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 245, 4)
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=True)
    st_0._set_subAutomata(*sub_automata)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
accelerationFactorType._Automaton = _BuildAutomaton_64()




parallelImagingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'accelerationFactor'), accelerationFactorType, scope=parallelImagingType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 273, 4)))

parallelImagingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'calibrationMode'), calibrationModeType, scope=parallelImagingType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 274, 4)))

parallelImagingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'interleavingDimension'), interleavingDimensionType, scope=parallelImagingType, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 275, 4)))

def _BuildAutomaton_67 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_67
    del _BuildAutomaton_67
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 274, 4))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 275, 4))
    counters.add(cc_1)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(parallelImagingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'accelerationFactor')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 273, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(parallelImagingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'calibrationMode')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 274, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(parallelImagingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'interleavingDimension')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 275, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
parallelImagingType._Automaton = _BuildAutomaton_67()




waveformInformation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'waveformName'), pyxb.binding.datatypes.string, scope=waveformInformation, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 283, 6)))

waveformInformation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'waveformType'), STD_ANON_2, scope=waveformInformation, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 284, 6)))

waveformInformation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'userParameters'), userParameters, scope=waveformInformation, location=pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 296, 4)))

def _BuildAutomaton_68 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_68
    del _BuildAutomaton_68
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(waveformInformation._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'waveformName')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 283, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(waveformInformation._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'waveformType')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 284, 6))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(waveformInformation._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'userParameters')), pyxb.utils.utility.Location('/home/dchansen/src/ismrmrd-python/schema/ismrmrd.xsd', 296, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
waveformInformation._Automaton = _BuildAutomaton_68()


import pyxb.utils.domutils
pyxb.utils.domutils.BindingDOMSupport.SetDefaultNamespace(Namespace)
