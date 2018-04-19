import ntpath
import re
import os

class Version_Helper(object):
    """
    @file: core.py
    @author: Dustin Gulley
    @date: 04/16/2018
    Helper for versioning pages in the wiki-440 system
    """
    def __init__(self):
        pass

    @staticmethod
    def get_filename_from_path(path):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        returns the filename from a given path
        'path/to/file/myfile.txt' -> 'myfile.txt'
        """
        return ntpath.basename(path)

    @staticmethod
    def get_path_without_filename(path):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        returns the filename from a given path
        'path/to/file/myfile.txt' -> 'path/to/file'
        """
        return ntpath.dirname(path)

    @staticmethod
    def __split_filename_from_extension(filename):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Separates the filename from the extension, returns a pair
        'myfile.txt' -> ['myfile', 'txt']
        """
        return filename.rsplit('.', 1)

    @staticmethod
    def __get_filename_without_version(filename):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Expects an extensionless filename and removes _v# from the end
        'myfile_v1' -> 'myfile'
        """
        return re.sub(r'_v\d+$', '', filename)

    @staticmethod
    def __get_all_versions_of_unversioned_file(path, unversioned_filename, ext):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Gets all versions of a file
        'myfile' -> ['path/to/myfile_v1.txt', 'path/to/myfile_v2.txt']
        """
        files_to_return = []
        for root, dirs, files in os.walk(path):
            for f in files:
                temp = f.replace(unversioned_filename, '', 1)  # Remove the filename
                temp = temp.replace('.' + ext, '')  # Remove the extension
                if re.match(r'^_v\d+$', temp):  # Only the version should be left
                    files_to_return.append(f)
        return files_to_return

    @staticmethod
    def __get_filename_without_extension(filepath):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Expects a path with a filename and returns a file without the ext
        'path/to/myfile.txt' - > 'myfile'
        """
        filename = Version_Helper.get_filename_from_path(filepath)
        filenamename_ext = Version_Helper.__split_filename_from_extension(filename)
        return filenamename_ext[0]

    @staticmethod
    def __get_version_from_filename(filename):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Expects a filename without
        'myfile_v1.txt' - > 1
        """
        temp_file = Version_Helper.__get_filename_without_extension(filename)
        version = re.findall('^.*([0-9]+)$', temp_file)

        if len(version) == 0:
            return 0
        else:
            return int(version[0])

        return version

    @staticmethod
    def __get_highest_version_number(file_list):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Returns highest version from a list of files, 0 if no version exists
        ['path/to/myfile_v1.txt', path/to/myfile_v2.txt] -> 2
        """
        version = 0
        for f in file_list:
            temp_version = Version_Helper.__get_version_from_filename(f)
            if temp_version > version:
                version = temp_version
        return version

    @staticmethod
    def __get_all_versions_of_file(file_path):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Returns all versions of a file
        'path/to/myfile_v2.txt' -> ['path/to/myfile_v1.txt', path/to/myfile_v2.txt]
        """
        file_path_without_file = Version_Helper.get_path_without_filename(file_path)
        filename = Version_Helper.get_filename_from_path(file_path)
        filename_ext = Version_Helper.__split_filename_from_extension(filename)
        unversioned_filename = Version_Helper.__get_filename_without_version(filename_ext[0])
        return Version_Helper.__get_all_versions_of_unversioned_file(file_path_without_file, unversioned_filename,
                                                           filename_ext[1])

    @staticmethod
    def __get_highest_version_number_from_file_path(file_path):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Returns highest version from a file path, 0 if no version exists
        'path/to/myfile_v1.txt' -> 2
        """
        all_versions = Version_Helper.__get_all_versions_of_file(file_path)
        return Version_Helper.__get_highest_version_number(all_versions)

    @staticmethod
    def get_highest_version_of_file_path(file_path):
        """
        @file: core.py
        @author: Dustin Gulley
        @date: 04/08/2018
        Returns highest version from a file path, 0 if no version exists
        'path/to/myfile_v1.txt' -> 'path/to/myfile_v2.txt'
        """
        version = Version_Helper.__get_highest_version_number_from_file_path(file_path)
        path = Version_Helper.get_path_without_filename(file_path)
        filename = Version_Helper.get_filename_from_path(file_path)
        filename_ext = Version_Helper.__split_filename_from_extension(filename)
        filename_no_version = Version_Helper.__get_filename_without_version(filename_ext[0])

        if version > 0:
            return os.path.join(path, filename_no_version + '_v' + str(version) + '.' + filename_ext[1])
        else:
            return file_path
