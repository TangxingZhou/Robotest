# Define the listeners for robotframework
# http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

__author__ = 'Tangxing Zhou'

from robot.api import SuiteVisitor


class Modifier(SuiteVisitor):

    def __init__(self, x=None):
        try:
            self.x = int(x)
        except TypeError:
            self.x = x

    def start_suite(self, suite):
        """Remove tests that match the given pattern."""
        if isinstance(self.x, int):
            suite.tests = [suite.tests[self.x]]

    def end_suite(self, suite):
        """Remove suites that are empty after removing tests."""
        pass

    def start_test(self, test):
        """Remove tests that match the given pattern."""
        pass

    def end_test(self, test):
        """Remove suites that are empty after removing tests."""
        pass

    def start_keyword(self, keyword):
        """Called when keyword starts. Default implementation does nothing.

        Can return explicit ``False`` to stop visiting.
        """
        pass

    def end_keyword(self, keyword):
        """Called when keyword ends. Default implementation does nothing."""
        pass
