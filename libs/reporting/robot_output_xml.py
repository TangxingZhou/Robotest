from uuid import uuid1
import xml.etree.ElementTree as ET
# https://docs.sqlalchemy.org/en/13/dialects/index.html
# https://www.osgeo.cn/sqlalchemy/core/tutorial.html
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
# # from libs.databases import Base
from sqlalchemy.orm import relationship
#
# from datetime import datetime
# from hashlib import sha1
# from robot.api import ExecutionResult
# from sqlite3 import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
mysql_engine = create_engine('mysql+mysqldb://root:123456@172.26.0.13:3306/robot', echo=False)
sqlite_engine = create_engine('sqlite:///database.db', echo=True)
engine = mysql_engine
session = sessionmaker(bind=engine)()


class Execution(Base):
    __tablename__ = 'executions'
    __xml_element__ = ET.Element('robot')

    id = Column(Integer, primary_key=True)
    taskid = Column(Text, unique=True)
    generator = Column(Text, nullable=False)
    generated = Column(Text, nullable=False)
    rpa = Column(Text, nullable=False)

    suites = relationship("Suite", back_populates="execution")
    errors = relationship("ExecutionError", back_populates="execution")
    suite_statistics = relationship("SuiteStatistics", back_populates="execution")
    test_statistics = relationship("TestStatistics", back_populates="execution")
    tag_statistics = relationship("TagStatistics", back_populates="execution")

    def to_xml_element(self):
        Execution.__xml_element__.attrib = {'generator': self.generator, 'generated':self.generated, 'rpa': self.rpa}


class ExecutionError(Base):
    __tablename__ = 'execution_errors'
    __xml_element__ = ET.Element('errors')

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    level = Column(Text, nullable=False)
    timestamp = Column(Text, nullable=False)
    text = Column(Text, nullable=False)

    execution = relationship("Execution", back_populates="errors")

    def to_xml_element(self):
        msg = ET.Element('msg', {'level': self.level, 'timestamp': self.timestamp})
        msg.text = self.text
        ExecutionError.__xml_element__.append(msg)


class SuiteStatistics(Base):
    __tablename__ = 'suite_statistics'
    __xml_element__ = ET.Element('suite')

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    key = Column(Text, nullable=False)
    _pass = Column(Text, nullable=False)
    _fail = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    text = Column(Text, nullable=False)

    execution = relationship("Execution", back_populates="suite_statistics")

    def to_xml_element(self):
        stat = ET.Element('stat', {'pass': self._pass, 'fail': self._fail, 'id': self.key, 'name': self.name})
        stat.text = self.text
        SuiteStatistics.__xml_element__.append(stat)


class TestStatistics(Base):
    __tablename__ = 'test_statistics'
    __xml_element__ = ET.Element('total')

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    _pass = Column(Text, nullable=False)
    _fail = Column(Text, nullable=False)
    text = Column(Text, nullable=False)

    execution = relationship("Execution", back_populates="test_statistics")

    def to_xml_element(self):
        stat = ET.Element('stat', {'pass': self._pass, 'fail': self._fail})
        stat.text = self.text
        TestStatistics.__xml_element__.append(stat)


class TagStatistics(Base):
    __tablename__ = 'tag_statistics'
    __xml_element__ = ET.Element('tag')

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    _pass = Column(Text, nullable=False)
    _fail = Column(Text, nullable=False)
    text = Column(Text, nullable=False)

    execution = relationship("Execution", back_populates="tag_statistics")

    def to_xml_element(self):
        stat = ET.Element('stat', {'pass': self._pass, 'fail': self._fail})
        stat.text = self.text
        TagStatistics.__xml_element__.append(stat)


class Suite(Base):
    __tablename__ = 'suites'
    __xml_element__ = ET.Element('suite')

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'))
    key = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    source = Column(Text)
    doc = Column(Text)
    parent_id = Column(Integer)
    status = Column(Text, nullable=False)
    starttime = Column(Text, nullable=False)
    endtime = Column(Text, nullable=False)

    execution = relationship("Execution", back_populates="suites")
    # parent = relationship("Suite", back_populates="parent")
    tests = relationship("Test", back_populates="suite")
    keywords = relationship("Keyword", back_populates="suite")

    def to_xml_element(self):
        Suite.__xml_element__.attrib = {'id': self.key, 'name': self.name, 'source': self.source}
        if self.doc:
            doc = ET.Element('doc')
            doc.text = self.doc
            Suite.__xml_element__.append(doc)
        status = ET.Element('status', {'status': self.status, 'starttime': self.starttime, 'endtime': self.endtime})
        Suite.__xml_element__.append(status)


class Test(Base):
    __tablename__ = 'tests'
    __xml_element__ = ET.Element('test')

    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer, ForeignKey('suites.id'), nullable=False)
    key = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    doc = Column(Text)
    status = Column(Text, nullable=False)
    starttime = Column(Text, nullable=False)
    endtime = Column(Text, nullable=False)
    critical = Column(Text, nullable=False)

    suite = relationship("Suite", back_populates="tests")
    tags = relationship("TestTag", back_populates="test")
    keywords = relationship("Keyword", back_populates="test")

    def to_xml_element(self):
        Test.__xml_element__.attrib = {'id': self.key, 'name': self.name}
        if self.doc:
            doc = ET.Element('doc')
            doc.text = self.doc
            Test.__xml_element__.append(doc)
        status = ET.Element('status', {'status': self.status, 'starttime': self.starttime, 'endtime': self.endtime, 'critical': self.critical})
        Test.__xml_element__.append(status)


class TestTag(Base):
    __tablename__ = 'test_tags'
    __xml_element__ = ET.Element('tags')

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    tag = Column(Text, nullable=False)

    test = relationship("Test", back_populates="tags")

    def to_xml_element(self):
        tag = ET.Element('tag')
        tag.text = self.text
        TestTag.__xml_element__.append(tag)


class Keyword(Base):
    __tablename__ = 'keywords'
    __xml_element__ = ET.Element('kw')

    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer, ForeignKey('suites.id'))
    test_id = Column(Integer, ForeignKey('tests.id'))
    name = Column(Text, nullable=False)
    library = Column(Text)
    type = Column(Text)
    doc = Column(Text)
    parent_id = Column(Integer)
    status = Column(Text, nullable=False)
    starttime = Column(Text, nullable=False)
    endtime = Column(Text, nullable=False)

    suite = relationship("Suite", back_populates="keywords")
    test = relationship("Test", back_populates="keywords")
    arguments = relationship("Argument", back_populates="keyword")
    assigns = relationship("Assign", back_populates="keyword")
    message = relationship("Message", uselist=False, back_populates="keyword")

    def to_xml_element(self):
        kw = {'name': self.name, 'library': self.library}
        if self.type:
            kw['type'] = self.type
        Keyword.__xml_element__.attrib = kw
        if self.doc:
            doc = ET.Element('doc')
            doc.text = self.doc
            Keyword.__xml_element__.append(doc)
        status = ET.Element('status', {'status': self.status, 'starttime': self.starttime, 'endtime': self.endtime})
        Keyword.__xml_element__.append(status)


class Argument(Base):
    __tablename__ = 'keyword_arguments'
    __xml_element__ = ET.Element('arguments')

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    arg = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="arguments")

    def to_xml_element(self):
        arg = ET.Element('arg')
        arg.text = self.arg
        Argument.__xml_element__.append(arg)


class Assign(Base):
    __tablename__ = 'keyword_assigns'
    __xml_element__ = ET.Element('assign')

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    var = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="assigns")

    def to_xml_element(self):
        var = ET.Element('var')
        var.text = self.var
        Assign.__xml_element__.append(var)


class Message(Base):
    __tablename__ = 'keyword_messages'
    __xml_element__ = ET.Element('msg')

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    timestamp = Column(Text, nullable=False)
    level = Column(Text, nullable=False)
    text = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="message")

    def to_xml_element(self):
        Message.__xml_element__.attrib = {'level': self.level, 'timestamp': self.timestamp}
        Message.__xml_element__.text = self.text


class RobotResult(object):

    def __init__(self, output_path, session=None):
        self.__output_path = output_path
        self.__session = session
        self.execution_id = 0

    def parse_results_into_db(self, task_id):
        for event, elem in ET.iterparse(self.__output_path, events=['end']):
            if elem.tag == 'robot':
                self.execution_id = self.add_object(
                    Execution,
                    taskid=task_id,
                    generator=elem.attrib['generator'],
                    generated=elem.attrib['generated'],
                    rpa=elem.attrib['rpa']
                )
                for errors in elem.findall('errors'):
                    self.visit_errors(errors, self.execution_id)
                for statistics in elem.findall('statistics'):
                    self.visit_statistics(statistics, self.execution_id)
                for suite in elem.findall('suite'):
                    self.visit_suite(suite, self.execution_id)

    def add_object(self, cla, *args, **kwargs):
        self.__session.add(cla(*args, **kwargs))
        return self.__session.query(cla).all()[-1].id

    def visit_errors(self, elem, execution_id):
        for item in elem.findall('msg'):
            self.add_object(
                ExecutionError,
                execution_id=execution_id,
                level=item.attrib['level'],
                timestamp=item.attrib['timestamp'],
                text=item.text
            )

    def visit_statistics(self, elem, execution_id):
        for item in elem.iter():
            if item.tag == 'total':
                for test_stat in item.findall('stat'):
                    self.add_object(
                        TestStatistics,
                        execution_id=execution_id,
                        _pass=test_stat.attrib['pass'],
                        _fail=test_stat.attrib['fail'],
                        text=test_stat.text
                    )
            elif item.tag == 'suite':
                for suite_stat in item.findall('stat'):
                    self.add_object(
                        SuiteStatistics,
                        execution_id=execution_id,
                        key=suite_stat.attrib['id'],
                        _pass=suite_stat.attrib['pass'],
                        _fail=suite_stat.attrib['fail'],
                        name=suite_stat.attrib['name'],
                        text=suite_stat.text
                    )
            elif item.tag == 'tag':
                for tag_stat in item.findall('stat'):
                    self.add_object(
                        TagStatistics,
                        execution_id=execution_id,
                        _pass=tag_stat.attrib['pass'],
                        _fail=tag_stat.attrib['fail'],
                        text=tag_stat.text
                    )

    def visit_suite(self, suite, execution_id=None, parent_id=None):
        suite_args = {
            'execution_id': execution_id,
            'parent_id': parent_id,
            'key': suite.attrib['id'],
            'name': suite.attrib['name']
        }
        if 'source' in suite.attrib.keys():
            suite_args['source'] = suite.attrib['source']
        suite_doc = suite.find('doc')
        if suite_doc:
            suite_args['doc'] = suite_doc.text
        suite_status = suite.find('status')
        suite_args['status'] = suite_status.attrib['status']
        suite_args['starttime'] = suite_status.attrib['starttime']
        suite_args['endtime'] = suite_status.attrib['endtime']
        suite_id = self.add_object(Suite, **suite_args)
        for suite_kw in suite.findall('kw'):
            self.visit_kw(suite_kw, suite_id)
        for suite_test in suite.findall('test'):
            self.visit_test(suite_test, suite_id)
        for sub_suite in suite.findall('suite'):
            self.visit_suite(sub_suite, None, suite_id)

    def visit_test(self, test, suite_id):
        test_args = {
            'suite_id': suite_id,
            'key': test.attrib['id'],
            'name': test.attrib['name']
        }
        test_doc = test.find('doc')
        if test_doc:
            test_args['doc'] = test_doc.text
        test_status = test.find('status')
        test_args['status'] = test_status.attrib['status']
        test_args['starttime'] = test_status.attrib['starttime']
        test_args['endtime'] = test_status.attrib['endtime']
        test_args['critical'] = test_status.attrib['critical']
        test_id = self.add_object(Test, **test_args)
        test_tags = test.find('tags')
        if test_tags:
            for test_tag in test_tags.findall('tag'):
                self.add_object(
                    TestTag,
                    test_id=test_id,
                    tag=test_tag.text
                )
        for test_kw in test.findall('kw'):
            self.visit_kw(test_kw, None, test_id)

    def visit_kw(self, kw, suite_id=None, test_id=None, parent_id=None):
        kw_args = {
            'suite_id': suite_id,
            'test_id': test_id,
            'parent_id': parent_id,
            'name': kw.attrib['name']
        }
        if 'library' in kw.attrib.keys():
            kw_args['library'] = kw.attrib['library']
        if 'type' in kw.attrib.keys():
            kw_args['type'] = kw.attrib['type']
        kw_doc = kw.find('doc')
        if kw_doc:
            kw_args['doc'] = kw_doc.text
        kw_status = kw.find('status')
        kw_args['status'] = kw_status.attrib['status']
        kw_args['starttime'] = kw_status.attrib['starttime']
        kw_args['endtime'] = kw_status.attrib['endtime']
        kw_id = self.add_object(Keyword, **kw_args)
        kw_arguments = kw.find('arguments')
        if kw_arguments:
            for kw_argument in kw_arguments.findall('arg'):
                self.add_object(
                    Argument,
                    keyword_id=kw_id,
                    arg=kw_argument.text
                )
        kw_assigns = kw.find('assign')
        if kw_assigns:
            for kw_assign in kw_assigns.findall('var'):
                self.add_object(
                    Assign,
                    keyword_id=kw_id,
                    var=kw_assign.text
                )
        kw_message = kw.find('msg')
        if kw_message:
            self.add_object(
                Message,
                keyword_id=kw_id,
                timestamp=kw_message.timestamp,
                level=kw_message.level,
                text=kw_message.text
            )
        for sub_kw in kw.findall('kw'):
            self.visit_kw(sub_kw, None, None, kw_id)

    def commit_to_db(self):
        self.__session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    root = None
    task_id = uuid1()
    db_results = RobotResult('/home/transwarp/Projects/python/robot/out/Demo/output.xml', session)
    db_results.parse_results_into_db(task_id)
    db_results.commit_to_db()
    # myerrors = session.query(Error).all()
    # for err in myerrors:
    #     err.to_xml_element()
    # ET.ElementTree(Error.__xml_element__).write('/home/transwarp/Projects/python/robot/out/Demo/test.xml', xml_declaration=True, encoding='UTF-8')
