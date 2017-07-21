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
    def __init__(self, path, delimiter=None):
        self.path = self.__fix_path(path=path)

        self.delimiter = delimiter

    @staticmethod
    def __fix_path(path):
        return path.replace('~', '/home/{0}'.format(_username))

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
    def stat(self):
        return os.stat(self.path)

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
            file_.write(what)
            file_.write('\n')

    @check_file()
    def copy(self, where):
        raise NotImplementedError

    @check_file()
    def move(self, where):
        self.rename(new_name=where)

    @check_file()
    def delete(self):
        raise NotImplementedError

    @check_file()
    def rename(self, new_name):
        self.__rename(new=new_name)

    def create(self, overwrite_policy=False):
        """
        Create an empty file
        """
        if self.is_file:
            if not overwrite_policy:
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
        new = self.__fix_path(path=new)
        os.renames(self.path, new)

        self.__update_path(new=new)

    def __update_path(self, new):
        if not new.startswith('/home'):
            new = os.path.join(os.getcwd(), new)

        self.path = new

    @check_file()
    def extract(self, where):
        raise NotImplementedError

    @check_file()
    def send(self):
        raise NotImplementedError


if __name__ == '__main__':
    f = File('my_file.txt')

    f.create(overwrite_policy=True)

    f.write(what='content')
    f.append(what='more content')

    # This moves the file to current directory if absolute path is not used
    f.rename(new_name='temp_file.txt')
