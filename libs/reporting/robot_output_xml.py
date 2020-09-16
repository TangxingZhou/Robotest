import sys
import os
from uuid import uuid1
from datetime import datetime
from robot import rebot
from robot.api import ExecutionResult
import xml.etree.ElementTree as ET
# https://www.osgeo.cn/sqlalchemy/core/tutorial.html
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Text, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from libs.databases import Base


class Execution(Base):
    __tablename__ = 'executions'

    id = Column(Integer, primary_key=True)
    taskid = Column(String(50), unique=True)
    generator = Column(String(100), nullable=False)
    generated = Column(String(21), nullable=False)
    rpa = Column(String(5), nullable=False)

    suites = relationship("Suite", back_populates="execution")
    errors = relationship("ExecutionError", back_populates="execution")
    suite_statistics = relationship("SuiteStatistics", back_populates="execution")
    test_statistics = relationship("TestStatistics", back_populates="execution")
    tag_statistics = relationship("TagStatistics", back_populates="execution")

    def to_xml_element(self):
        root = ET.Element('robot')
        root.attrib = {'generator': self.generator, 'generated': self.generated, 'rpa': self.rpa}
        for suite in self.suites:
            root.append(suite.to_xml_element())
        statistics = ET.Element('statistics')
        _statistics = ET.Element('total')
        for test_statistic in self.test_statistics:
            _statistics.append(test_statistic.to_xml_element())
        statistics.append(_statistics)
        _statistics = ET.Element('tag')
        for tag_statistic in self.tag_statistics:
            _statistics.append(tag_statistic.to_xml_element())
        statistics.append(_statistics)
        _statistics = ET.Element('suite')
        for suite_statistic in self.suite_statistics:
            _statistics.append(suite_statistic.to_xml_element())
        statistics.append(_statistics)
        root.append(statistics)
        errors = ET.Element('errors')
        if self.errors:
            for error in self.errors:
                errors.append(error.to_xml_element())
        root.append(errors)
        return root


class ExecutionError(Base):
    __tablename__ = 'execution_errors'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    level = Column(String(10), nullable=False)
    timestamp = Column(String(21), nullable=False)
    text = Column(Text, nullable=False)

    execution = relationship("Execution", back_populates="errors")

    def to_xml_element(self):
        msg = ET.Element('msg', {'timestamp': self.timestamp, 'level': self.level})
        msg.text = self.text
        return msg


class SuiteStatistics(Base):
    __tablename__ = 'suite_statistics'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    key = Column(String(50), nullable=False)
    _pass = Column(String(10), nullable=False)
    _fail = Column(String(10), nullable=False)
    name = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    elapsed = Column(Integer)

    execution = relationship("Execution", back_populates="suite_statistics")

    def to_xml_element(self):
        stat = ET.Element('stat', {'pass': self._pass, 'fail': self._fail, 'id': self.key, 'name': self.name})
        stat.text = self.text
        return stat


class TestStatistics(Base):
    __tablename__ = 'test_statistics'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    _pass = Column(String(10), nullable=False)
    _fail = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    elapsed = Column(Integer)

    execution = relationship("Execution", back_populates="test_statistics")

    def to_xml_element(self):
        stat = ET.Element('stat', {'pass': self._pass, 'fail': self._fail})
        stat.text = self.text
        return stat


class TagStatistics(Base):
    __tablename__ = 'tag_statistics'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    _pass = Column(String(10), nullable=False)
    _fail = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    elapsed = Column(Integer)

    execution = relationship("Execution", back_populates="tag_statistics")

    def to_xml_element(self):
        stat = ET.Element('stat', {'pass': self._pass, 'fail': self._fail})
        stat.text = self.text
        return stat


class Suite(Base):
    __tablename__ = 'suites'

    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('executions.id'))
    key = Column(String(50), nullable=False)
    name = Column(Text, nullable=False)
    source = Column(Text)
    doc = Column(Text)
    msg = Column(Text)
    parent_id = Column(Integer)
    status = Column(String(10), nullable=False)
    starttime = Column(String(21), nullable=False)
    endtime = Column(String(21), nullable=False)
    elapsed = Column(Integer)

    execution = relationship("Execution", back_populates="suites")
    tests = relationship("Test", back_populates="suite")
    keywords = relationship("Keyword", back_populates="suite")

    def to_xml_element(self):
        elem = ET.Element('suite')
        elem.attrib = {'id': self.key, 'name': self.name}
        if self.source:
            elem.attrib['source'] = self.source
        RobotResult.retrieve(Suite, elem, self.id)
        for kw in self.keywords:
            elem.append(kw.to_xml_element())
        for test in self.tests:
            elem.append(test.to_xml_element())
        if self.doc:
            doc = ET.Element('doc')
            doc.text = self.doc
            elem.append(doc)
        status = ET.Element('status', {'status': self.status, 'starttime': self.starttime, 'endtime': self.endtime})
        if self.msg:
            status.text = self.msg
        elem.append(status)
        return elem


class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer, ForeignKey('suites.id'), nullable=False)
    key = Column(String(50), nullable=False)
    name = Column(Text, nullable=False)
    doc = Column(Text)
    msg = Column(Text)
    timeout=Column(Text)
    status = Column(String(10), nullable=False)
    starttime = Column(String(21), nullable=False)
    endtime = Column(String(21), nullable=False)
    elapsed = Column(Integer)
    critical = Column(String(5), nullable=False)

    suite = relationship("Suite", back_populates="tests")
    tags = relationship("TestTag", back_populates="test")
    keywords = relationship("Keyword", back_populates="test")

    def to_xml_element(self):
        elem = ET.Element('test')
        elem.attrib = {'id': self.key, 'name': self.name}
        for kw in self.keywords:
            elem.append(kw.to_xml_element())
        if self.doc:
            doc = ET.Element('doc')
            doc.text = self.doc
            elem.append(doc)
        if self.tags:
            test_tags = ET.Element('tags')
            for tag in self.tags:
                test_tags.append(tag.to_xml_element())
            elem.append(test_tags)
        if self.timeout:
            timeout = ET.Element('timeout', {'value': self.timeout})
            elem.append(timeout)
        status = ET.Element('status', {'status': self.status, 'starttime': self.starttime, 'endtime': self.endtime, 'critical': self.critical})
        if self.msg:
            status.text = self.msg
        elem.append(status)
        return elem


class TestTag(Base):
    __tablename__ = 'test_tags'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    tag = Column(Text, nullable=False)

    test = relationship("Test", back_populates="tags")

    def to_xml_element(self):
        tag = ET.Element('tag')
        tag.text = self.tag
        return tag


class Keyword(Base):
    __tablename__ = 'keywords'
    __xml_element__ = ET.Element('kw')

    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer, ForeignKey('suites.id'))
    test_id = Column(Integer, ForeignKey('tests.id'))
    name = Column(Text, nullable=False)
    library = Column(Text)
    type = Column(String(20))
    doc = Column(Text)
    parent_id = Column(Integer)
    timeout = Column(Text)
    status = Column(String(10), nullable=False)
    starttime = Column(String(21), nullable=False)
    endtime = Column(String(21), nullable=False)
    elapsed = Column(Integer)

    suite = relationship("Suite", back_populates="keywords")
    test = relationship("Test", back_populates="keywords")
    tags = relationship("KeywordTag", back_populates="keyword")
    arguments = relationship("Argument", back_populates="keyword")
    assigns = relationship("Assign", back_populates="keyword")
    messages = relationship("Message", back_populates="keyword")

    def to_xml_element(self):
        elem = ET.Element('kw')
        elem.attrib = {'name': self.name}
        if self.library:
            elem.attrib['library'] = self.library
        if self.type:
            elem.attrib['type'] = self.type
        if self.tags:
            kw_tags = ET.Element('tags')
            for tag in self.tags:
                kw_tags.append(tag.to_xml_element())
            elem.append(kw_tags)
        if self.doc:
            doc = ET.Element('doc')
            doc.text = self.doc
            elem.append(doc)
        if self.arguments:
            kw_arguments = ET.Element('arguments')
            for argument in self.arguments:
                kw_arguments.append(argument.to_xml_element())
            elem.append(kw_arguments)
        if self.assigns:
            kw_assigns = ET.Element('assign')
            for assign in self.assigns:
                kw_assigns.append(assign.to_xml_element())
            elem.append(kw_assigns)
        RobotResult.retrieve(Keyword, elem, self.id)
        for message in self.messages:
            elem.append(message.to_xml_element())
        if self.timeout:
            timeout = ET.Element('timeout', {'value': self.timeout})
            elem.append(timeout)
        status = ET.Element('status', {'status': self.status, 'starttime': self.starttime, 'endtime': self.endtime})
        elem.append(status)
        return elem


class KeywordTag(Base):
    __tablename__ = 'keyword_tags'

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    tag = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="tags")

    def to_xml_element(self):
        tag = ET.Element('tag')
        tag.text = self.tag
        return tag


class Argument(Base):
    __tablename__ = 'keyword_arguments'

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    arg = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="arguments")

    def to_xml_element(self):
        arg = ET.Element('arg')
        arg.text = self.arg
        return arg


class Assign(Base):
    __tablename__ = 'keyword_assigns'

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    var = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="assigns")

    def to_xml_element(self):
        var = ET.Element('var')
        var.text = self.var
        return var


class Message(Base):
    __tablename__ = 'keyword_messages'

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    timestamp = Column(String(21), nullable=False)
    level = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="messages")

    def to_xml_element(self):
        msg = ET.Element('msg')
        msg.attrib = {'timestamp': self.timestamp, 'level': self.level}
        msg.text = self.text
        return msg


class RobotResult(object):
    __session = None

    def __init__(self, session=None):
        if RobotResult.__session is not None and RobotResult.__session is not session:
            sys.stderr.write('[WARN] Different session of database are specified.')
        RobotResult.__session = session

    @classmethod
    def parse_results_into_db(cls, output, task_id=str(uuid1())):
        root = ET.ElementTree(file=output).getroot()
        execution_id = cls.add_object(
            Execution,
            taskid=task_id,
            generator=root.attrib['generator'],
            generated=root.attrib['generated'],
            rpa=root.attrib['rpa']
        )
        for errors in root.findall('errors'):
            cls.visit_errors(errors, execution_id)
        for statistics in root.findall('statistics'):
            cls.visit_statistics(statistics, execution_id)
        for suite in root.findall('suite'):
            cls.visit_suite(suite, execution_id)
        return execution_id

    @classmethod
    def merge_results_into_db(cls, output, task_id=str(uuid1())):
        root = ET.ElementTree(file=output).getroot()
        execution_result = ExecutionResult(output, include_keywords=True)
        execution_id = cls.add_object(
            Execution,
            taskid=task_id,
            generator=root.attrib['generator'],
            generated=root.attrib['generated'],
            rpa=root.attrib['rpa']
        )
        cls.parse_errors(execution_result, execution_id)
        cls.parse_statistics(execution_result, execution_id)
        cls.parse_suite(execution_result.suite, execution_id)
        return execution_id

    @classmethod
    def retrieve_executions(cls, output_dir, name, *task_ids):
        project_output = []
        suites_starttime = []
        suites_endtime = []
        for task_id in task_ids:
            execution = cls.__session.query(Execution).filter(Execution.taskid == task_id).first()
            out_xml = os.path.join(output_dir, '{}.xml'.format(task_id))
            ET.ElementTree(execution.to_xml_element()).write(out_xml, xml_declaration=True, encoding='UTF-8')
            project_output.append(out_xml)
            for suite in execution.suites:
                suites_starttime.append(datetime.strptime(suite.starttime, '%Y%m%d %H:%M:%S.%f'))
                suites_endtime.append(datetime.strptime(suite.endtime, '%Y%m%d %H:%M:%S.%f'))
        rebot(
            *project_output, name=name, log='log', output='output', stdout=sys.stdout,
            outputdir=output_dir,
            starttime=min(suites_starttime).strftime('%Y%m%d %H:%M:%S.%f')[:-3],
            endtime=max(suites_endtime).strftime('%Y%m%d %H:%M:%S.%f')[:-3]
        )

    @classmethod
    def retrieve_results_into_output(cls, output_dir, task_id):
        execution = cls.__session.query(Execution).filter(Execution.taskid == task_id).first()
        out_xml = os.path.join(output_dir, '{}.xml'.format(task_id))
        ET.ElementTree(execution.to_xml_element()).write(out_xml, xml_declaration=True, encoding='UTF-8')

    @classmethod
    def retrieve(cls, table, parent, parent_id):
        for child in cls.__session.query(table).filter(table.parent_id.isnot(None), table.parent_id == parent_id).all():
            child_elem = child.to_xml_element()
            parent.append(child_elem)

    @classmethod
    def add_object(cls, cla, *args, **kwargs):
        cls.__session.add(cla(*args, **kwargs))
        cls.__session.commit()
        return cls.__session.query(cla).all()[-1].id

    @classmethod
    def visit_errors(cls, elem, execution_id):
        for item in elem.findall('msg'):
            cls.add_object(
                ExecutionError,
                execution_id=execution_id,
                level=item.attrib['level'],
                timestamp=item.attrib['timestamp'],
                text=item.text
            )

    @classmethod
    def visit_statistics(cls, elem, execution_id):
        for item in elem.iter():
            if item.tag == 'total':
                for test_stat in item.findall('stat'):
                    cls.add_object(
                        TestStatistics,
                        execution_id=execution_id,
                        _pass=test_stat.attrib['pass'],
                        _fail=test_stat.attrib['fail'],
                        text=test_stat.text
                    )
            elif item.tag == 'suite':
                for suite_stat in item.findall('stat'):
                    cls.add_object(
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
                    cls.add_object(
                        TagStatistics,
                        execution_id=execution_id,
                        _pass=tag_stat.attrib['pass'],
                        _fail=tag_stat.attrib['fail'],
                        text=tag_stat.text
                    )

    @classmethod
    def visit_suite(cls, suite, execution_id=None, parent_id=None):
        suite_args = {
            'execution_id': execution_id,
            'parent_id': parent_id,
            'key': suite.attrib['id'],
            'name': suite.attrib['name']
        }
        if 'source' in suite.attrib.keys():
            suite_args['source'] = suite.attrib['source']
        suite_doc = suite.find('doc')
        if suite_doc is not None:
            suite_args['doc'] = suite_doc.text
        suite_status = suite.find('status')
        suite_args['status'] = suite_status.attrib['status']
        suite_args['starttime'] = suite_status.attrib['starttime']
        suite_args['endtime'] = suite_status.attrib['endtime']
        suite_args['msg'] = suite_status.text
        suite_id = cls.add_object(Suite, **suite_args)
        for suite_kw in suite.findall('kw'):
            cls.visit_kw(suite_kw, suite_id)
        for suite_test in suite.findall('test'):
            cls.visit_test(suite_test, suite_id)
        for sub_suite in suite.findall('suite'):
            cls.visit_suite(sub_suite, None, suite_id)

    @classmethod
    def visit_test(cls, test, suite_id):
        test_args = {
            'suite_id': suite_id,
            'key': test.attrib['id'],
            'name': test.attrib['name']
        }
        test_doc = test.find('doc')
        if test_doc is not None:
            test_args['doc'] = test_doc.text
        test_timeout = test.find('timeout')
        if test_timeout is not None:
            test_args['timeout'] = test_timeout.attrib['value']
        test_status = test.find('status')
        test_args['status'] = test_status.attrib['status']
        test_args['starttime'] = test_status.attrib['starttime']
        test_args['endtime'] = test_status.attrib['endtime']
        test_args['critical'] = test_status.attrib['critical']
        test_args['msg'] = test_status.text
        test_id = cls.add_object(Test, **test_args)
        test_tags = test.find('tags')
        if test_tags is not None:
            for test_tag in test_tags.findall('tag'):
                cls.add_object(
                    TestTag,
                    test_id=test_id,
                    tag=test_tag.text
                )
        for test_kw in test.findall('kw'):
            cls.visit_kw(test_kw, None, test_id)

    @classmethod
    def visit_kw(cls, kw, suite_id=None, test_id=None, parent_id=None):
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
        if kw_doc is not None:
            kw_args['doc'] = kw_doc.text
        kw_timeout = kw.find('timeout')
        if kw_timeout is not None:
            kw_args['timeout'] = kw_timeout.attrib['value']
        kw_status = kw.find('status')
        kw_args['status'] = kw_status.attrib['status']
        kw_args['starttime'] = kw_status.attrib['starttime']
        kw_args['endtime'] = kw_status.attrib['endtime']
        kw_id = cls.add_object(Keyword, **kw_args)
        kw_arguments = kw.find('arguments')
        if kw_arguments is not None:
            for kw_argument in kw_arguments.findall('arg'):
                cls.add_object(
                    Argument,
                    keyword_id=kw_id,
                    arg=kw_argument.text
                )
        kw_assigns = kw.find('assign')
        if kw_assigns is not None:
            for kw_assign in kw_assigns.findall('var'):
                cls.add_object(
                    Assign,
                    keyword_id=kw_id,
                    var=kw_assign.text
                )
        for kw_message in kw.findall('msg'):
            cls.add_object(
                Message,
                keyword_id=kw_id,
                timestamp=kw_message.attrib['timestamp'],
                level=kw_message.attrib['level'],
                text=kw_message.text
            )
        kw_tags = kw.find('tags')
        if kw_tags is not None:
            for kw_tag in kw_tags.findall('tag'):
                cls.add_object(
                    KeywordTag,
                    keyword_id=kw_id,
                    tag=kw_tag.text
                )
        for sub_kw in kw.findall('kw'):
            cls.visit_kw(sub_kw, None, None, kw_id)

    @classmethod
    def parse_errors(cls, execution_result, execution_id):
        for msg in execution_result.errors.messages:
            cls.add_object(
                ExecutionError,
                execution_id=execution_id,
                level=msg.level,
                timestamp=msg.timestamp,
                text=msg.message
            )

    @classmethod
    def parse_statistics(cls, execution_result, execution_id):
        for stat in execution_result.statistics.total:
            cls.add_object(
                TestStatistics,
                execution_id=execution_id,
                _pass=str(stat.passed),
                _fail=str(stat.failed),
                text=stat.name,
                elapsed=stat.elapsed
            )
        for stat in execution_result.statistics.suite:
            cls.add_object(
                SuiteStatistics,
                execution_id=execution_id,
                key=stat.id,
                _pass=str(stat.passed),
                _fail=str(stat.failed),
                name=stat._name,
                text=stat.name,
                elapsed=stat.elapsed
            )
        for stat in execution_result.statistics.tags:
            cls.add_object(
                TagStatistics,
                execution_id=execution_id,
                _pass=str(stat.passed),
                _fail=str(stat.failed),
                text=stat.name,
                elapsed=stat.elapsed
            )

    @classmethod
    def parse_suite(cls, suite, execution_id=None, parent_id=None):
        suite_args = {
            'execution_id': execution_id,
            'parent_id': parent_id,
            'key': suite.id,
            'name': suite.name,
            'status': suite.status,
            'starttime': suite.starttime,
            'endtime': suite.endtime,
            'elapsed': suite.elapsedtime
        }
        if suite.source:
            suite_args['source'] = suite.source
        if suite.doc:
            suite_args['doc'] = suite.doc
        if suite.message:
            suite_args['msg'] = suite.message
        suite_id = cls.add_object(Suite, **suite_args)
        for suite_kw in suite.keywords:
            cls.parse_kw(suite_kw, suite_id)
        for suite_test in suite.tests:
            cls.parse_test(suite_test, suite_id)
        for sub_suite in suite.suites:
            cls.parse_suite(sub_suite, None, suite_id)

    @classmethod
    def parse_test(cls, test, suite_id):
        test_args = {
            'suite_id': suite_id,
            'key': test.id,
            'name': test.name,
            'status': test.status,
            'starttime': test.starttime,
            'endtime': test.endtime,
            'elapsed': test.elapsedtime
        }
        if test.doc:
            test_args['doc'] = test.doc
        if test.critical:
            test_args['critical'] = 'yes'
        else:
            test_args['critical'] = 'no'
        if test.message:
            test_args['msg'] = test.message
        if test.timeout:
            test_args['timeout'] = test.timeout
        test_id = cls.add_object(Test, **test_args)
        for test_tag in test.tags:
            cls.add_object(
                TestTag,
                test_id=test_id,
                tag=test_tag
            )
        for test_kw in test.keywords:
            cls.parse_kw(test_kw, None, test_id)

    @classmethod
    def parse_kw(cls, kw, suite_id=None, test_id=None, parent_id=None):
        kw_args = {
            'suite_id': suite_id,
            'test_id': test_id,
            'parent_id': parent_id,
            'name': kw.kwname,
            'status': kw.status,
            'starttime': kw.starttime,
            'endtime': kw.endtime,
            'elapsed': kw.elapsedtime
        }
        if kw.libname:
            kw_args['library'] = kw.libname
        if kw.type:
            kw_args['type'] = kw.type
        if kw.doc:
            kw_args['doc'] = kw.doc
        if kw.timeout:
            kw_args['timeout'] = kw.timeout
        kw_id = cls.add_object(Keyword, **kw_args)
        for kw_argument in kw.args:
            cls.add_object(
                Argument,
                keyword_id=kw_id,
                arg=kw_argument
            )
        for kw_assign in kw.assign:
            cls.add_object(
                Assign,
                keyword_id=kw_id,
                var=kw_assign
            )
        for kw_message in kw.messages:
            cls.add_object(
                Message,
                keyword_id=kw_id,
                timestamp=kw_message.timestamp,
                level=kw_message.level,
                text=kw_message.message
            )
        for kw_tag in kw.tags:
            cls.add_object(
                KeywordTag,
                keyword_id=kw_id,
                tag=kw_tag
            )
        for sub_kw in kw.keywords:
            cls.parse_kw(sub_kw, None, None, kw_id)

# __all__ = [
#     Execution,
#     ExecutionError,
#     SuiteStatistics,
#     TestStatistics,
#     TagStatistics,
#     Suite,
#     Test,
#     TestTag,
#     Keyword,
#     Argument,
#     Assign,
#     Message
# ]


if __name__ == '__main__':
    mysql_engine = create_engine('mysql+mysqldb://root:123456@172.26.0.13:3306/robot', echo=False)
    sqlite_engine = create_engine('sqlite:////home/transwarp/Projects/python/robot/test.db', echo=False)
    engine = sqlite_engine
    session = sessionmaker(bind=engine, autoflush=False)()
    Base.metadata.create_all(engine)
    db_results = RobotResult(session)
    db_results.merge_results_into_db('/home/transwarp/Projects/python/robot/out/Demo/output.xml')
    db_results.retrieve_results_into_output('/home/transwarp/Projects/python/robot/out', '5a1c9080-f19a-11ea-934d-8f994452f05e')
