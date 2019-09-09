import os, sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from jinja2 import Environment, FileSystemLoader


class EmailReport(object):

    def __init__(self, host, user, password, receivers='', port=25):
        self.__ready = False
        if None not in (host, user, password, receivers):
            self.__sender = user
            try:
                self.__receivers = receivers.replace(' ', '')
                self.__smtp = smtplib.SMTP(host, port)
                self.__smtp.login(user, password)
                self.__ready = True
            except Exception as e:
                sys.stderr.write('[SMTP ERROR]: Fail to log in to {}@{}.\n{}\n'.format(user, host, e))

    @property
    def ready(self):
        return self.__ready

    def send(self, mime_type='html', subject=None, content=''):
        if self.__ready:
            message = MIMEText(content, _subtype=mime_type, _charset='utf-8')
            message['Subject'] = Header(subject, charset='utf-8')
            message['From'] = self.__sender
            message['To'] = self.__receivers
            self.__smtp.sendmail(self.__sender, self.__receivers.split(','), message.as_string())

    @classmethod
    def render(cls, email_template_file, email_file='', **kwargs):
        if os.path.isfile(email_template_file):
            env = Environment(loader=FileSystemLoader(os.path.dirname(email_template_file)))
        else:
            raise FileNotFoundError('Template file \'{}\' for email is not found.'.format(email_template_file))
        email_template_file = env.get_template(os.path.basename(email_template_file))
        content = email_template_file.render(**kwargs)
        if email_file:
            with open(email_file, 'w') as f:
                f.write(content)
        return content

    def quit(self):
        return self.__smtp.quit()


TestRuns = {
    '__table__': 'test_runs',
    'id': int,
    'started_at': str,
    'finished_at': str,
    'source_file': str
}

TestRunStatus = {
    '__table__': 'test_run_status',
    'name': str,
    'passed': int,
    'failed': int,
    'elapsed': int
}

Suites = {
    '__table__': 'suites',
    'suite_key': str,
    'parent_suite': str,
    'name': str,
    'source': str,
    'doc': str
}

SuiteStatus = {
    '__table__': 'suite_status',
    'suite_id': int,
    'passed': int,
    'failed': int,
    'elapsed': int,
    'status': str
}

Tests = {
    '__table__': 'tests',
    'id': int,
    'suite_id': int,
    'test_key': str,
    'name': str,
    'doc': str
}

TestStatus = {
    '__table__': 'test_status',
    'test_run_id': int,
    'test_id': int,
    'elapsed': int,
    'status': str
}

TestTagStatus = {
    '__table__': 'test_tag_status',
    'name': str,
    'passed': int,
    'failed': int,
    'elapsed': int
}
