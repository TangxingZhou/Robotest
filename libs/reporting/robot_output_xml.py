import xml.etree.ElementTree as ET
# https://docs.sqlalchemy.org/en/13/dialects/index.html
# https://www.osgeo.cn/sqlalchemy/core/tutorial.html
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
# from libs.databases import Base
from sqlalchemy.orm import relationship

from datetime import datetime
from hashlib import sha1
from robot.api import ExecutionResult
from sqlite3 import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
mysql_engine = create_engine('mysql+mysqldb://root:123456@172.26.0.13:3306/robot', echo=False)
sqlite_engine = create_engine('sqlite:///database.db', echo=True)
engine = mysql_engine
session = sessionmaker(bind=engine)()


class TestRun(Base):
    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True)
    hash = Column(Text, nullable=False, unique=True)
    # uuid = Column(Text, nullable=False, unique=True)
    imported_at = Column(DateTime, nullable=False)
    source_file = Column(Text)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    status = relationship("TestRunStatus", uselist=False, back_populates="test_run")
    errors = relationship("TestRunError", back_populates="test_run")
    tag_status = relationship("TestTagStatus", back_populates="test_run")
    suite_status = relationship("SuiteStatus", back_populates="test_run")
    test_status = relationship("TestStatus", back_populates="test_run")
    keyword_status = relationship("KeywordStatus", back_populates="test_run")


class TestRunStatus(Base):
    __tablename__ = 'test_run_status'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    name = Column(Text, nullable=False)
    elapsed = Column(Integer)
    failed = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)

    # __table_args__ = (
    #     UniqueConstraint('test_run_id', 'name')
    # )

    test_run = relationship("TestRun", back_populates="status")


class TestRunError(Base):
    __tablename__ = 'test_run_errors'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    level = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

    test_run = relationship("TestRun", back_populates="errors")


class TestTagStatus(Base):
    __tablename__ = 'test_tag_status'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    name = Column(Text, nullable=False)
    critical = Column(Integer, nullable=False)
    elapsed = Column(Integer)
    failed = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)

    test_run = relationship("TestRun", back_populates="tag_status")


class Suite(Base):
    __tablename__ = 'suites'

    id = Column(Integer, primary_key=True)
    suite_key = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('suites.id'))
    parent_suite = Column(Text, nullable=False)
    name = Column(DateTime, nullable=False, unique=True)
    source = Column(Text)
    doc = Column(Text)

    parent = relationship("Suite", back_populates="parent")
    status = relationship("SuiteStatus", uselist=False, back_populates="suite")
    tests = relationship("Test", back_populates="suite")
    keywords = relationship("Keyword", back_populates="suite")


class SuiteStatus(Base):
    __tablename__ = 'suite_status'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    suite_id = Column(Integer, ForeignKey('suites.id'), nullable=False)
    elapsed = Column(Integer, nullable=False)
    failed = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    status = Column(Text, nullable=False)

    test_run = relationship("TestRun", back_populates="suite_status")
    suite = relationship("Suite", back_populates="status")


class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer, ForeignKey('suites.id'), nullable=False)
    test_key = Column(Text, nullable=False)
    name = Column(Text, nullable=False, unique=True)
    timeout = Column(Text)
    doc = Column(Text)

    suite = relationship("Suite", back_populates="tests")
    status = relationship("TestStatus", uselist=False, back_populates="test")
    tags = relationship("TestTag", back_populates="test")


class TestStatus(Base):
    __tablename__ = 'test_status'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    status = Column(Text, nullable=False)
    elapsed = Column(Integer, nullable=False)

    test_run = relationship("TestRun", back_populates="test_status")
    test = relationship("Test", back_populates="status")


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    suite_id = Column(Integer, ForeignKey('suites.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    keyword_key = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('keywords.id'))
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    library = Column(Text)
    timeout = Column(Text)
    doc = Column(Text)

    suite = relationship("Suite", back_populates="keywords")
    status = relationship("KeywordStatus", uselist=False, back_populates="keyword")
    parent = relationship("Keyword", back_populates="parent")
    messages = relationship("Message", back_populates="keyword")
    tags = relationship("KeywordTag", back_populates="keyword")
    arguments = relationship("Argument", back_populates="keyword")


class KeywordStatus(Base):
    __tablename__ = 'keyword_status'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    status = Column(Text, nullable=False)
    elapsed = Column(Text, nullable=False)
    starttime = Column(Text, nullable=False)
    endtime = Column(Integer, nullable=False)

    test_run = relationship("TestRun", back_populates="keyword_status")
    keyword = relationship("Keyword", back_populates="status")


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    level = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="messages")


class TestTag(Base):
    __tablename__ = 'test_tags'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    name = Column(Text, nullable=False)

    test = relationship("Test", back_populates="tags")


class KeywordTag(Base):
    __tablename__ = 'keyword_tags'

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    tag = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="tags")


class Argument(Base):
    __tablename__ = 'arguments'

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords.id'), nullable=False)
    content = Column(Text, nullable=False)

    keyword = relationship("Keyword", back_populates="arguments")


class Error(Base):
    __tablename__ = 'errors'
    __xml_element__ = ET.Element(__tablename__)

    id = Column(Integer, primary_key=True)
    level = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)

    def to_xml_element(self):
        return ET.Element(self.__tablename__)



if __name__ == '__main__':
    Base.metadata.create_all(engine)
    root = None
    for event, elem in ET.iterparse('/home/transwarp/Projects/python/robot/out/Demo/output.xml'):
        if elem.tag == 'robot':
            root = elem
        elif elem.tag == 'suite':
            pass
        elif elem.tag == 'test':
            pass
        elif elem.tag == 'kw':
            pass
        elif elem.tag == 'arguments':
            pass
        elif elem.tag == 'arg':
            pass
        elif elem.tag == 'assign':
            pass
        elif elem.tag == 'var':
            pass
        elif elem.tag == 'doc':
            pass
        elif elem.tag == 'status':
            pass
        elif elem.tag == 'tags':
            pass
        elif elem.tag == 'tag':
            pass
        elif elem.tag == 'msg':
            pass
        elif elem.tag == 'statistics':
            pass
        elif elem.tag == 'total':
            pass
        elif elem.tag == 'stat':
            pass
        elif elem.tag == 'errors':
            for child in elem.iter():
                if child.tag == 'msg':
                    msg1 = Message(
                        timestamp=child.attrib['timestamp'],
                        level=child.attrib['level'],
                        text=child.text
                    )
                    session.add(msg1)
                    session.commit()
        else:
            print(elem.tag)
        # elem.clear()
    # ET.ElementTree(root).write('/home/transwarp/Projects/python/robot/out/Demo/test.xml', xml_declaration=True, encoding='UTF-8')
