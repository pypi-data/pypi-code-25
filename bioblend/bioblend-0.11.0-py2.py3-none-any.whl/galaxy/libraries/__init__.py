"""
Contains possible interactions with the Galaxy Data Libraries
"""
import logging
import time

from six.moves import range

from bioblend.galaxy.client import Client
from bioblend.galaxy.datasets import DatasetTimeoutException, terminal_states
from bioblend.util import attach_file

log = logging.getLogger(__name__)


class LibraryClient(Client):

    def __init__(self, galaxy_instance):
        self.module = 'libraries'
        super(LibraryClient, self).__init__(galaxy_instance)

    def create_library(self, name, description=None, synopsis=None):
        """
        Create a data library with the properties defined in the arguments.

        :type name: str
        :param name: Name of the new data library

        :type description: str
        :param description: Optional data library description

        :type synopsis: str
        :param synopsis: Optional data library synopsis

        :rtype: dict
        :return: Details of the created library.
          For example::

            {'id': 'f740ab636b360a70',
             'name': 'Library from bioblend',
             'url': '/api/libraries/f740ab636b360a70'}
        """
        payload = {'name': name}
        if description:
            payload['description'] = description
        if synopsis:
            payload['synopsis'] = synopsis
        return self._post(payload)

    def delete_library(self, library_id):
        """
        Delete a data library.

        :type library_id: str
        :param library_id: Encoded data library ID identifying the library to be
          deleted

        .. warning::
          Deleting a data library is irreversible - all of the data from the
          library will be permanently deleted.
        """
        return self._delete(id=library_id)

    def _show_item(self, library_id, item_id):
        """
        Get details about a given library item.
        """
        url = self.gi._make_url(self, library_id, contents=True)
        url = '/'.join([url, item_id])
        return self._get(url=url)

    def delete_library_dataset(self, library_id, dataset_id, purged=False):
        """
        Delete a library dataset in a data library.

        :type library_id: str
        :param library_id: library id where dataset is found in

        :type dataset_id: str
        :param dataset_id: id of the dataset to be deleted

        :type purged: bool
        :param purged: Indicate that the dataset should be purged (permanently
          deleted)

        :rtype: dict
        :return: A dictionary containing the dataset id and whether the dataset
          has been deleted.
          For example::

            {u'deleted': True,
             u'id': u'60e680a037f41974'}
        """
        url = self.gi._make_url(self, library_id, contents=True)
        # Append the dataset_id to the base history contents URL
        url = '/'.join([url, dataset_id])
        return self._delete(payload={'purged': purged}, url=url)

    def show_dataset(self, library_id, dataset_id):
        """
        Get details about a given library dataset. The required ``library_id``
        can be obtained from the datasets's library content details.

        :type library_id: str
        :param library_id: library id where dataset is found in

        :type dataset_id: str
        :param dataset_id: id of the dataset to be inspected

        :rtype: dict
        :return: A dictionary containing information about the dataset in the
          library
        """
        return self._show_item(library_id, dataset_id)

    def wait_for_dataset(self, library_id, dataset_id, maxwait=12000, interval=3):
        """
        Wait until the library dataset state is terminal ('ok', 'empty',
        'error', 'discarded' or 'failed_metadata').

        :type library_id: str
        :param library_id: library id where dataset is found in

        :type dataset_id: str
        :param dataset_id: id of the dataset to wait for

        :type maxwait: float
        :param maxwait: Total time (in seconds) to wait for the dataset state to
          become terminal. If the dataset state is not terminal within this
          time, a ``DatasetTimeoutException`` will be thrown.

        :type interval: float
        :param interval: Time (in seconds) to wait between 2 consecutive checks.

        :rtype: dict
        :return: A dictionary containing information about the dataset in the
          library
        """
        assert maxwait > 0
        assert interval > 0

        for time_left in range(maxwait, 0, -interval):
            dataset = self.show_dataset(library_id, dataset_id)
            state = dataset['state']
            if state in terminal_states:
                return dataset
            if time_left > 0:
                log.warning("Waiting for library %s dataset %s to complete. Will wait another %i s", library_id, dataset_id, time_left)
                time.sleep(min(time_left, interval))
            else:
                raise DatasetTimeoutException("Waited too long for library %s dataset %s to complete" % (library_id, dataset_id))

    def show_folder(self, library_id, folder_id):
        """
        Get details about a given folder. The required ``folder_id`` can be
        obtained from the folder's library content details.

        :type library_id: str
        :param library_id: library id to inspect folders in

        :type folder_id: str
        :param folder_id: id of the folder to be inspected
        """
        return self._show_item(library_id, folder_id)

    def _get_root_folder_id(self, library_id):
        """
        Find the root folder (i.e. '/') of a library.

        :type library_id: str
        :param library_id: library id to find root of
        """
        l = self.show_library(library_id=library_id)
        if 'root_folder_id' in l:
            return l['root_folder_id']
        # Galaxy previous to release_13.04 does not have root_folder_id in
        # library dictionary, so resort to find the folder with name '/'
        library_contents = self.show_library(library_id=library_id, contents=True)
        for f in library_contents:
            if f['name'] == '/':
                return f['id']

    def create_folder(self, library_id, folder_name, description=None, base_folder_id=None):
        """
        Create a folder in a library.

        :type library_id: str
        :param library_id: library id to use

        :type folder_name: str
        :param folder_name: name of the new folder in the data library

        :type description: str
        :param description: description of the new folder in the data library

        :type base_folder_id: str
        :param base_folder_id: id of the folder where to create the new folder.
          If not provided, the root folder will be used
        """
        # Get root folder ID if no ID was provided
        if base_folder_id is None:
            base_folder_id = self._get_root_folder_id(library_id)
        # Compose the payload
        payload = {}
        payload['name'] = folder_name
        payload['folder_id'] = base_folder_id
        payload['create_type'] = 'folder'
        if description is not None:
            payload['description'] = description
        return self._post(payload, id=library_id, contents=True)

    def get_folders(self, library_id, folder_id=None, name=None):
        """
        Get all the folders or filter specific one(s) via the provided ``name``
        or ``folder_id`` in data library with id ``library_id``. Provide only
        one argument: ``name`` or ``folder_id``, but not both.

        :type folder_id: str
        :param folder_id: filter for folder by folder id

        :type name: str
        :param name: filter for folder by name. For ``name`` specify the full
                     path of the folder starting from the library's root
                     folder, e.g. ``/subfolder/subsubfolder``.

        :rtype: list
        :return: list of dicts each containing basic information about a folder
        """
        if folder_id is not None and name is not None:
            raise ValueError('Provide only one argument between name or folder_id, but not both')
        library_contents = self.show_library(library_id=library_id, contents=True)
        if folder_id is not None:
            folder = next((_ for _ in library_contents if _['type'] == 'folder' and _['id'] == folder_id), None)
            folders = [folder] if folder is not None else []
        elif name is not None:
            folders = [_ for _ in library_contents if _['type'] == 'folder' and _['name'] == name]
        else:
            folders = [_ for _ in library_contents if _['type'] == 'folder']
        return folders

    def get_libraries(self, library_id=None, name=None, deleted=False):
        """
        Get all the libraries or filter for specific one(s) via the provided
        name or ID. Provide only one argument: ``name`` or ``library_id``, but
        not both.

        :type library_id: str
        :param library_id: filter for library by library id

        :type name: str
        :param name: If ``name`` is set and multiple names match the given name,
          all the libraries matching the argument will be returned

        :type deleted: bool
        :param deleted: If set to ``True``, return libraries that have been
          deleted

        :rtype: list
        :return: list of dicts each containing basic information about a library
        """
        if library_id is not None and name is not None:
            raise ValueError('Provide only one argument between name or library_id, but not both')
        libraries = self._get(deleted=deleted)
        if library_id is not None:
            library = next((_ for _ in libraries if _['id'] == library_id), None)
            libraries = [library] if library is not None else []
        if name is not None:
            libraries = [_ for _ in libraries if _['name'] == name]
        return libraries

    def show_library(self, library_id, contents=False):
        """
        Get information about a library.

        :type library_id: str
        :param library_id: filter for library by library id

        :type contents: bool
        :param contents: True if want to get contents of the library (rather
          than just the library details)

        :rtype: dict
        :return: details of the given library
        """
        return self._get(id=library_id, contents=contents)

    def _do_upload(self, library_id, **keywords):
        """
        Set up the POST request and do the actual data upload to a data library.
        This method should not be called directly but instead refer to the
        methods specific for the desired type of data upload.
        """
        folder_id = keywords.get('folder_id', None)
        if folder_id is None:
            folder_id = self._get_root_folder_id(library_id)
        files_attached = False
        # Compose the payload dict
        payload = {}
        payload['folder_id'] = folder_id
        payload['file_type'] = keywords.get('file_type', 'auto')
        payload['dbkey'] = keywords.get('dbkey', '?')
        payload['create_type'] = 'file'
        if keywords.get("roles", None):
            payload["roles"] = keywords["roles"]
        if keywords.get("link_data_only", None) and keywords['link_data_only'] != 'copy_files':
            payload["link_data_only"] = 'link_to_files'
        # upload options
        if keywords.get('file_url', None) is not None:
            payload['upload_option'] = 'upload_file'
            payload['files_0|url_paste'] = keywords['file_url']
        elif keywords.get('pasted_content', None) is not None:
            payload['upload_option'] = 'upload_file'
            payload['files_0|url_paste'] = keywords['pasted_content']
        elif keywords.get('server_dir', None) is not None:
            payload['upload_option'] = 'upload_directory'
            payload['server_dir'] = keywords['server_dir']
        elif keywords.get('file_local_path', None) is not None:
            payload['upload_option'] = 'upload_file'
            payload['files_0|file_data'] = attach_file(keywords['file_local_path'])
            files_attached = True
        elif keywords.get("filesystem_paths", None) is not None:
            payload["upload_option"] = "upload_paths"
            payload["filesystem_paths"] = keywords["filesystem_paths"]

        try:
            return self._post(payload, id=library_id, contents=True,
                              files_attached=files_attached)
        finally:
            if payload.get('files_0|file_data', None) is not None:
                payload['files_0|file_data'].close()

    def upload_file_from_url(self, library_id, file_url, folder_id=None, file_type='auto', dbkey='?'):
        """
        Upload a file to a library from a URL.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type file_url: str
        :param file_url: URL of the file to upload

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded file.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey
        """
        return self._do_upload(library_id, file_url=file_url,
                               folder_id=folder_id, file_type=file_type,
                               dbkey=dbkey)

    def upload_file_contents(self, library_id, pasted_content, folder_id=None, file_type='auto', dbkey='?'):
        """
        Upload pasted_content to a data library as a new file.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type pasted_content: str
        :param pasted_content: Content to upload into the library

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded file.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey
        """
        return self._do_upload(library_id, pasted_content=pasted_content,
                               folder_id=folder_id, file_type=file_type,
                               dbkey=dbkey)

    def upload_file_from_local_path(self, library_id, file_local_path,
                                    folder_id=None, file_type='auto', dbkey='?'):
        """
        Read local file contents from file_local_path and upload data to a
        library.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type file_local_path: str
        :param file_local_path: path of local file to upload

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded file.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey
        """
        return self._do_upload(library_id, file_local_path=file_local_path,
                               folder_id=folder_id, file_type=file_type,
                               dbkey=dbkey)

    def upload_file_from_server(self, library_id, server_dir, folder_id=None,
                                file_type='auto', dbkey='?', link_data_only=None,
                                roles=""):
        """
        Upload all files in the specified subdirectory of the Galaxy library
        import directory to a library.

        .. note::
          For this method to work, the Galaxy instance must have the
          ``library_import_dir`` option configured in the ``config/galaxy.ini``
          configuration file.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type server_dir: str
        :param server_dir: relative path of the subdirectory of
          ``library_import_dir`` to upload. All and only the files (i.e. no
          subdirectories) contained in the specified directory will be
          uploaded

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded files.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey

        :type link_data_only: str
        :param link_data_only: either 'copy_files' (default) or
          'link_to_files'. Setting to 'link_to_files' symlinks instead of
          copying the files

        :type roles: str
        :param roles: ???
        """
        return self._do_upload(library_id, server_dir=server_dir,
                               folder_id=folder_id, file_type=file_type,
                               dbkey=dbkey, link_data_only=link_data_only,
                               roles=roles)

    def upload_from_galaxy_filesystem(self, library_id, filesystem_paths, folder_id=None,
                                      file_type="auto", dbkey="?", link_data_only=None,
                                      roles=""):
        """
        Upload a set of files already present on the filesystem of the Galaxy
        server to a library.

        .. note::
          For this method to work, the Galaxy instance must have the
          ``allow_path_paste`` (``allow_library_path_paste`` in Galaxy
          ``release_17.05`` and earlier) option set to ``True`` in the
          ``config/galaxy.ini`` configuration file.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type filesystem_paths: str
        :param filesystem_paths: file paths on the Galaxy server to upload to
          the library, one file per line

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded files.
          If not provided, the root folder will be used

        :type file_type: str
        :param file_type: Galaxy file format name

        :type dbkey: str
        :param dbkey: Dbkey

        :type link_data_only: str
        :param link_data_only: either 'copy_files' (default) or
          'link_to_files'. Setting to 'link_to_files' symlinks instead of
          copying the files

        :type roles: str
        :param roles: ???
        """
        return self._do_upload(library_id, filesystem_paths=filesystem_paths,
                               folder_id=folder_id, file_type=file_type,
                               dbkey=dbkey, link_data_only=link_data_only,
                               roles=roles)

    def copy_from_dataset(self, library_id, dataset_id, folder_id=None, message=''):
        """
        Copy a Galaxy dataset into a library.

        :type library_id: str
        :param library_id: id of the library where to place the uploaded file

        :type dataset_id: str
        :param dataset_id: id of the dataset to copy from

        :type folder_id: str
        :param folder_id: id of the folder where to place the uploaded files.
          If not provided, the root folder will be used

        :type message: str
        :param message: message for copying action
        """
        if folder_id is None:
            folder_id = self._get_root_folder_id(library_id)
        payload = {}
        payload['folder_id'] = folder_id
        payload['create_type'] = 'file'
        payload['from_hda_id'] = dataset_id
        payload['ldda_message'] = message
        return self._post(payload, id=library_id, contents=True)

    def get_library_permissions(self, library_id):
        """
        Get the permessions for a library.

        :type library_id: str
        :param library_id: id of the library

        :rtype: dict
        :return: dictionary with all applicable permissions' values
        """
        url = '/'.join([self.gi._make_url(self, library_id), 'permissions'])
        return self._get(url=url)

    def set_library_permissions(self, library_id, access_in=None,
                                modify_in=None, add_in=None, manage_in=None):
        """
        Set the permissions for a library.  Note: it will override all security
        for this library even if you leave out a permission type.

        :type library_id: str
        :param library_id: id of the library

        :type access_in: list
        :param access_in: list of role ids

        :type modify_in: list
        :param modify_in: list of role ids

        :type add_in: list
        :param add_in: list of role ids

        :type manage_in: list
        :param manage_in: list of role ids
        """
        payload = {}
        if access_in:
            payload['LIBRARY_ACCESS_in'] = access_in
        if modify_in:
            payload['LIBRARY_MODIFY_in'] = modify_in
        if add_in:
            payload['LIBRARY_ADD_in'] = add_in
        if manage_in:
            payload['LIBRARY_MANAGE_in'] = manage_in
        url = '/'.join([self.gi._make_url(self, library_id), 'permissions'])
        return self._post(payload, url=url)
