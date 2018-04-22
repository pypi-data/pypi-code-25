
from .. import ConfigUtils
from .DictTree import DictTree

class OfflineJob(DictTree):
  """
  Mimic the functionality of real Job GPI. No enhancement shall be made here.
  (Do it in JobUtils).

  Not everything will be mimic here, only those essential for JobTree for now...

  Use `DictTree`, which allow the quick instantiation to dict
  from the public attribute defined in the class.

  Raises:
    IOError: If the given `jid` leads to missing/corrupt metadata file.

  Attributes taken as of Ganga 6.0.44

 |       comment          comment of the job. (simple property,
 |                        default='',comparable)
 |
 |       fqid             fully qualified job identifier. (simple property,
 |                        default=None,transient,protected,optional)
 |
 |       inputfiles       list of file objects that will act as input files for a
 |                        job. ('gangafiles' object, list, default=[],comparable)
 |
 |       outputdir        location of output directory (file workspace). (simple
 |                        property, default=None,transient,protected,optional)
 |
 |       backend          specification of the resources to be used (e.g. batch
 |                        system). ('backends' object, default=None,comparable)
 |
 |       subjobs          list of subjobs (if splitting). ('jobs' object, list,
 |                        default=[],protected,comparable,optional)
 |
 |       id               unique Ganga job identifier generated automatically.
 |                        (simple property, default='',protected)
 |
 |       application      specification of the application to be executed.
 |                        ('applications' object, default=None,comparable)
 |
 |       master           master job. ('jobs' object,
 |                        default=None,transient,protected,optional)
 |
 |       inputdata        dataset definition (typically this is specific either to
 |                        an application, a site or the virtual organization.
 |                        ('datasets' object, default=None,comparable,optional)
 |
 |       metadata         the metadata. ('metadata' object,
 |                        default=<Ganga.GPIDev.Lib.Job.MetadataDict.MetadataDict
 |                        object at 0x132df10>,protected,comparable)
 |
 |       status           current state of the job, one of "new", "submitted",
 |                        "running", "completed", "killed", "unknown", "incomplete".
 |                        (simple property, default='new',protected,comparable)
 |
 |       outputfiles      list of file objects decorating what have to be done with
 |                        the output files after job is completed . ('gangafiles'
 |                        object, list, default=[],comparable)
 |
 |       do_auto_resubmit Automatically resubmit failed subjobs. (simple property,
 |                        default=False,comparable)
 |
 |       postprocessors   list of postprocessors to run after job has finished.
 |                        ('postprocessor' object, default=None,comparable)
 |
 |       info             JobInfo . ('jobinfos' object, default=None,comparable)
 |
 |       splitter         optional splitter. ('splitters' object,
 |                        default=None,comparable,optional)
 |
 |       name             optional label which may be any combination of ASCII
 |                        characters. (simple property, default='',comparable)
 |
 |       inputsandbox     list of File objects shipped to the worker node . ('files'
 |                        object, list, default=[],comparable)
 |
 |       inputdir         location of input directory (file workspace). (simple
 |                        property, default=None,transient,protected,optional)
 |
 |       outputdata       dataset definition (typically this is specific either to
 |                        an application, a site or the virtual organization.
 |                        ('datasets' object, default=None,comparable,optional)
 |
 |       time             provides timestamps for status transitions. ('jobtime'
 |                        object, default=None,protected)
 |
 |       outputsandbox    list of filenames or patterns shipped from the worker
 |                        node. (simple property, list, default=[],comparable)
  """

  def __init__(self, jid):
    """

    >>> getfixture('job197')
    >>> j = OfflineJob(197)
    >>> j.comment
    ''
    >>> j.status
    'completed'
    >>> OfflineJob('197.2').status
    'completed'

    """

    path = ConfigUtils.dir_repository(jid)+'/data'
    super( OfflineJob, self ).__init__( path )

    # node = self._tree.find('attribute[@name="inputdata"]')
    # self.remove(node)

  @property  
  def fqid(self):
    """

    >>> getfixture('job197')  
    >>> OfflineJob('197').fqid
    '197'

    >> OfflineJob('123.45').fqid
    '123.45'
    >> type(OfflineJob('123').fqid)
    <type 'str'>

    """
    return str(self.id)
