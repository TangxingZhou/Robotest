import sys, os
from ftplib import FTP, error_perm


class FTPService(object):

    def __init__(self, server, user, password):
        self.__ftp = FTP(server)
        try:
            self.__ftp.login(user, password)
        except Exception as e:
            sys.stdout.write('[FTP ERROR]: Fail to login to {} for {}.\n{}'.format(server, user, e))

    def cwd(self, target_dir):
        for path in target_dir.split('/'):
            if path != '':
                try:
                    self.__ftp.cwd(path)
                except error_perm:
                    self.__ftp.mkd(path)
                    self.__ftp.cwd(path)

    def upload(self, file_path, target_file):
        self.__ftp.pwd()
        try:
            self.__ftp.storbinary('STOR {}'.format(os.path.basename(target_file)), open(os.path.normpath(file_path), 'rb'))
        except Exception as e:
            sys.stdout.write('[FTP ERROR]: Fail to upload {} to FTP Server.\n{}'.format(os.path.normpath(file_path), e))

    def close(self):
        self.__ftp.quit()
