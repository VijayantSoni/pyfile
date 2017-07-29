import os
import pwd
from functools import wraps

__author__ = 'Vijayant Soni <vijayant4129@gmail.com>'
__status__ = 'Development'


_username = pwd.getpwuid(os.getuid()).pw_name


class FileNotFoundError(Exception):
    pass


class FileNotAccessibleError(Exception):
    pass


class FileAlreadyExists(Exception):
    pass


def check_file():
    """
    Check if file is present and accessible
    """
    def _decorator(fn):

        @wraps(fn)
        def _wrapped(*args, **kwargs):
            file_ = args[0]

            if not file_.is_file:
                raise FileNotFoundError(file_.path)

            if not file_.is_accessible:
                raise FileNotAccessibleError(file_.path)

            return fn(*args, **kwargs)

        return _wrapped

    return _decorator


class File(object):
    def __init__(self, path):
        self.path = self.__fix_path(path=path)

    @staticmethod
    def __fix_path(path):
        return path.replace('~', '/home/{0}'.format(_username))

    # Properties
    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def directory_path(self):
        return os.path.dirname(self.path) or os.getcwd()

    @property
    def extension(self):
        return self.name.rsplit('.', 1)[1]

    @property
    def is_empty(self):
        return self.size == 0

    @property
    def is_file(self):
        return os.path.isfile(self.path)

    @property
    def is_accessible(self):
        return os.access(self.path, os.R_OK)

    @property
    def size(self):
        return 0 if not (self.is_file and self.is_accessible) else self.stat.st_size

    @property
    def mtime(self):
        return self.stat.st_mtime

    @property
    def atime(self):
        return self.stat.st_atime

    @property
    def ctime(self):
        return self.stat.st_ctime

    @property
    def uid(self):
        return self.stat.st_uid

    @property
    def gid(self):
        return self.stat.st_gid

    @property
    def mode(self):
        return self.stat.st_mode

    @property
    @check_file()
    def stat(self):
        return os.stat(self.path)

    @property
    def empty_lines(self):
        return sum(1 for line in self if not line)

    @property
    def total_lines(self):
        return sum(1 for _ in self)

    @property
    def non_empty_lines(self):
        return self.total_lines - self.empty_lines
    # Properties

    # Content related behaviours
    @check_file()
    def get_pointer(self):
        return open(self.path, 'r')

    def search(self, what):
        raise NotImplementedError

    def get_line(self, lno=1):
        content = ''
        if lno < 0 or lno > self.total_lines:
            return content

        c_lno = 1
        for line in self:
            if c_lno == lno:
                content = line
                break
            c_lno += 1

        return content

    def read(self, size=-1):
        fp = self.get_pointer()
        content = fp.read(size)
        fp.close()

        return content

    def append(self, what):
        try:
            self.create(overwrite_policy=False)
        except FileAlreadyExists:
            pass

        self.__write(what=what, mode='a')

    def write(self, what):
        self.create(overwrite_policy=True)

        self.__write(what=what)

    def __write(self, what, mode='w'):
        with open(self.path, mode=mode) as file_:
            file_.write(str(what))
            file_.write('\n')

    def __iter__(self):
        """
        Iterate through each line of the file
        """
        fp = self.get_pointer()

        for line in fp:
            yield line

        fp.close()
    # Content related behaviours

    # File level behaviours
    @check_file()
    def copy(self, where):
        raise NotImplementedError

    @check_file()
    def move(self, where, overwrite_policy=True):
        where = self.__fix_path(path=where)

        # If a directory is provided then new name is same as existing name
        if os.path.isdir(where):
            where = os.path.join(where, self.name)

        self.rename(new_name=where, overwrite_policy=overwrite_policy)

    @check_file()
    def delete(self):
        os.remove(self.path)

    @check_file()
    def rename(self, new_name, overwrite_policy=True):
        new = self.__fix_path(path=new_name)

        if '/' not in new:
            new = os.path.join(self.directory_path, new)

        temp_file = File(path=new)
        if temp_file.is_file and not overwrite_policy:
            raise FileAlreadyExists(temp_file.path)

        self.__rename(new=new)

    def create(self, overwrite_policy=False):
        """
        Create an empty file
        """
        if self.is_file and not overwrite_policy:
            raise FileAlreadyExists(self.path)

        if self.path_exists():
            with open(self.path, 'w') as _:
                pass

            return

        os.makedirs(self.directory_path)

        self.create(overwrite_policy=overwrite_policy)

    def path_exists(self):
        return os.path.exists(self.directory_path)

    def __rename(self, new):
        os.renames(self.path, new)

        self.__update_path(new=new)

    def __update_path(self, new):
        if not new.startswith('/home'):
            new = os.path.join(os.getcwd(), new)

        self.path = new
    # File level behaviours

    # Extraction
    @check_file()
    def extract(self, where):
        raise NotImplementedError
    # Extraction

    # Send
    @check_file()
    def send(self):
        raise NotImplementedError
    # Send


if __name__ == '__main__':
    f = File('<file_path>')

    # Create new file, overwrite if exists
    f.create(overwrite_policy=True)

    # Create new file, do not overwrite if exists
    try:
        f.create(overwrite_policy=False)
    except FileAlreadyExists:
        pass

    # Truncate the file and write
    f.write(what='content')

    # Append to file
    f.append(what='more content')

    # Read
    print f.read()
    print f.read(size=11)

    # Line counts
    print f.total_lines
    print f.empty_lines
    print f.non_empty_lines

    # Iterate over each line
    for l in f:
        pass

    # Get specific line
    print f.get_line(lno=5)

    # Rename file, overwrite existing file with same name
    f.rename(new_name='<new_name>', overwrite_policy=True)

    # Rename file, do not overwrite existing file with same name
    try:
        f.rename(new_name='<new_name>', overwrite_policy=False)
    except FileAlreadyExists:
        pass

    # Move file to new location, overwrite existing file with same name
    f.move(where='<new_location>', overwrite_policy=True)

    # Move file to new location, do not overwrite existing file with same name
    try:
        f.move(where='<new_location>', overwrite_policy=False)
    except FileAlreadyExists:
        pass

    # Continue modifying the file, no need to reopen the file explicitly
    f.append(what='New content')
