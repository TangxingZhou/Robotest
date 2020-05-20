import sys
import platform
import re
import os.path
import base64
from robot.libraries.OperatingSystem import OperatingSystem


class OSExt(OperatingSystem):

    ROBOT_LIBRARY_VERSION = 1.0
    ROBOT_EXIT_ON_FAILURE = True

    def get_hosts_path(self):
        """
        Get the absolute path of hosts file of the operation system.
        :return: The path of hosts.
        Examples:
        | ${hosts}= | Get Hosts Path |
        """
        if platform.system() == 'Windows':
            return os.path.join(
                self.get_environment_variable('windir', 'C:\\Windows'),
                'System32\\drivers\\etc\\hosts'
            )
        elif platform.system() == 'Linux':
            return '/etc/hosts'
        else:
            self._error('[Runtime ERROR]: OS {} is not support.'.format(platform.system()))
            sys.exit(1)

    def append_content_to_file(self, path, pattern, content):
        """
        Append content to file if the given pattern is not matched.
        :param path: The path of the target file.
        :param pattern: The pattern to search.
        :param content: The content to append.
        :return: None
        Examples:
        | Append Content To File | /etc/hosts | 127.0.0.1 | localhost |
        | Append Content To File | C:\\Windows\\System32\\drivers\\etc\\hosts | 127.0.0.1 | localhost${\n} |
        """
        self.file_should_exist(path)
        matches = self.grep_file(path, pattern)
        if matches == '':
            self.append_to_file(path, content)

    def append_content_to_hosts(self, content):
        """
        Append content to hosts of the system.
        :param content: The content to append.
        :return: None
        Examples:
        | Append Content To Hosts | 127.0.0.1 localhost |
        """
        hosts_path = self.get_hosts_path()
        self.append_content_to_file(hosts_path, content, content + os.linesep)

    def remove_content_from_file(self, path, pattern):
        """
        Remove lines from file if the given pattern is matched.
        :param path: The path of the target file.
        :param pattern: The pattern to search.
        :return: None
        Examples:
        | Remove Content From File | /etc/hosts | 127.0.0.1 |
        | Remove Content From File | C:\\Windows\\System32\\drivers\\etc\\hosts | 127.0.0.1 |
        """
        path = self._absnorm(path)
        self.file_should_exist(path)
        lines = []
        total_lines = 0
        self._link("Reading file '%s'.", path)
        with open(path, mode='r', encoding='UTF-8', errors='strict') as f:
            for line in f.readlines():
                total_lines += 1
                if re.search(re.compile(pattern), line) is None:
                    lines.append(line)
        if len(lines) < total_lines:
            with open(path, mode='w', encoding='UTF-8', errors='strict') as f:
                self._info('%d out of %d lines removed.' % (total_lines - len(lines), total_lines))
                f.writelines(lines)
        else:
            self._log('No lines matched.', 'DEBUG')

    def remove_content_from_hosts(self, pattern):
        """
        Remove lines from hosts of the system if the given pattern is matched.
        :param pattern: The pattern to search.
        :return: None
        Examples:
        | Remove Content From Hosts | 127.0.0.1 |
        """
        hosts_path = self.get_hosts_path()
        self.remove_content_from_file(hosts_path, pattern)

    def replace_content_in_file(self, path, pattern, content, index=None):
        """
        Replace lines by index in file if the given pattern is matched.
        :param path: The path of the target file.
        :param pattern: The pattern to search.
        :param content: The content to replace the lines matched the pattern.
        :param index: To replace the occurence by index, None for all, None by default.
        :return: None
        Examples:
        | Replace Content In File | /etc/hosts | 127.0.0.1 | localhost |
        | Replace Content In File | /etc/hosts | 127.0.0.1 | localhost | ${0} |
        | Replace Content In File | C:\\Windows\\System32\\drivers\\etc\\hosts | 127.0.0.1 | localhost | index=${-1} |
        """
        path = self._absnorm(path)
        self.file_should_exist(path)
        lines = []
        total_lines = 0
        matched_lines_index = []
        self._link("Reading file '%s'.", path)
        with open(path, mode='r', encoding='UTF-8', errors='strict') as f:
            for line in f.readlines():
                lines.append(line)
                if re.search(re.compile(pattern), line) is not None:
                    matched_lines_index.append(total_lines)
                total_lines += 1
        if len(matched_lines_index) > 0:
            self._info('{} out of {} lines matched.'.format(len(matched_lines_index), total_lines))
            if index is None:
                lines = [content if i in matched_lines_index else l for i, l in enumerate(lines)]
            else:
                if not isinstance(index, int):
                    self._error('[Runtime ERROR]: index \'{}\' must be int or NoneType.'.format(index))
                    sys.exit(1)
                else:
                    if index < len(matched_lines_index):
                        lines[index] = content
                    else:
                        self._error('[Runtime ERROR]: index \'{}\' out of range, it should be less than {}.'.
                                    format(index, len(matched_lines_index)))
                        sys.exit(1)
            with open(path, mode='w', encoding='UTF-8', errors='strict') as f:
                f.writelines(lines)
        else:
            self._log('No lines matched.', 'DEBUG')

    @classmethod
    def encode_str_with_base64(cls, s):
        """
        To encode the input strings with base64.
        :param s: The input strings.
        :return: The strings encoded by base64.
        """
        if isinstance(s, str):
            return base64.b64encode(s.encode()).decode()
        else:
            raise TypeError('Strings are required.')

    def encode_file_with_base64(self, path):
        """
        To encode the input file with base64.
        :param path: The path of the target file.
        :return: The content in the input file encoded by base64.
        """
        path = self._absnorm(path)
        self.file_should_exist(path)
        with open(path, mode='rb') as f:
            return base64.b64encode(f.read()).decode()
