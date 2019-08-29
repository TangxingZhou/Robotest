import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from jinja2 import Environment, FileSystemLoader


class EmailReport(object):

    def __init__(self, host, user, password, receivers='', subject='', port=25):
        self.__smtp = smtplib.SMTP(host, port)
        self.__sender = user
        self.__login_auth = (user, password)
        self.__receivers = receivers.replace(' ', '')
        self.__header = Header(subject, charset='utf-8')
        self.__content = ''

    def login(self):
        self.__smtp.login(*self.__login_auth)

    def send(self, mime_type='html', content=''):
        if content:
            message = MIMEText(content, _subtype=mime_type, _charset='utf-8')
        else:
            message = MIMEText(self.__content, _subtype=mime_type, _charset='utf-8')
        message['Subject'] = self.__header
        message['From'] = self.__sender
        message['To'] = self.__receivers
        self.__smtp.sendmail(self.__sender, self.__receivers.split(','), message.as_string())

    def render(self, template, out='', **kwargs):
        if os.path.isfile(template):
            env = Environment(loader=FileSystemLoader(os.path.dirname(template)))
        else:
            raise FileNotFoundError('Template file \'{}\' for email is not found.'.format(template))
        email_template = env.get_template(os.path.basename(template))
        self.__content = email_template.render(**kwargs)
        if out:
            with open(out, 'w') as f:
                f.write(self.__content)

    def quit(self):
        return self.__smtp.quit()


TestRuns = {
    '__table__': 'test_runs',
    'id': int,
    'started_at': str,
    'finished_at': str
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
