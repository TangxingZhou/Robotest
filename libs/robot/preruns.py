# Define the listeners for robotframework
# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

__author__ = 'Tangxing Zhou'

import os
from datetime import datetime
from robot.libraries.BuiltIn import BuiltIn
from robot.api import SuiteVisitor
from robot.utils import Matcher


class PreRun(SuiteVisitor):

    def __init__(self, pattern):
         self.matcher = Matcher(pattern)

    def _is_excluded(self, test):
        return self.matcher.match(test.name) or self.matcher.match(test.longname)

    def start_suite(self, suite):
        """Remove tests that match the given pattern."""
        # suite.tests = [t for t in suite.tests if not self._is_excluded(t)]
        #print(suite.tests)
        #suite.tests = [t for t in suite.tests if t.name == 'Test Modifier Two']
        #suite.tests.remove('Test Modifier Two')
        tags = {}
        for t in suite.tests:
            for tag in t.tags:
                if tag in tags:
                    tags[tag].append(t.name)
                else:
                    tags[tag] = [t.name]
        #print(tags)
        keys = [x for x in tags]
        keys.sort()
        #print((keys))

    def end_suite(self, suite):
        """Remove suites that are empty after removing tests."""
        # suite.suites = [s for s in suite.suites if s.test_count > 0]
        #print('End')
        #print(suite.tests)

    def start_test(self, test):
        """Remove tests that match the given pattern."""
        print(test.tags)
        #print(dir(test))
        #print(test.parent.tests)

    def end_test(self, test):
        """Remove suites that are empty after removing tests."""
        #print(test)

    def start_keyword(self, keyword):
        """Called when keyword starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_keyword(self, keyword):
        """Called when keyword ends. Default implementation does nothing."""
        print(keyword.tags)
        pass
