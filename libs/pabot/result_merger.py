from __future__ import absolute_import, print_function

from robot.api import ExecutionResult
from robot.conf import RebotSettings
from robot.result.executionresult import CombinedResult
import re

try:
    from robot.result import TestSuite
except ImportError:
    from robot.result.testsuite import TestSuite

from robot.model import SuiteVisitor


class ResultMerger(SuiteVisitor):

    def __init__(self, result, tests_root_name):
        self.root = result.suite
        self.errors = result.errors
        self.current = None
        self._skip_until = None
        self._tests_root_name = tests_root_name

    def merge(self, merged):
        try:
            merged.suite.visit(self)
            if self.errors!=merged.errors: self.errors.add(merged.errors)
        except:
            print('Error while merging result %s' % merged.source)
            raise

    def start_suite(self, suite):
        if self._skip_until and self._skip_until != suite:
            return
        if not self.current:
            self.current = self._find_root(suite)
            assert(self.current)
        else:
            next = self._find(self.current.suites, suite.name)
            if next is None:
                self.current.suites.append(suite)
                suite.parent = self.current
                self._skip_until = suite
            else:
                self.current = next
                if self.current is not suite:
                    for keyword in suite.keywords:
                        self.current.keywords.append(keyword)

    def _find_root(self, suite):
        if self.root.name != suite.name:
            raise ValueError('self.root.name "%s" != suite.name "%s"' %
                             (self.root.name, suite.name))
        return self.root

    def _find(self, items, name):
        for item in items:
            if item.name == name:
                return item
        return None

    def end_suite(self, suite):
        if self._skip_until and self._skip_until != suite:
            return
        if self._skip_until == suite:
            self._skip_until = None
            return
        self.merge_missing_tests(suite)
        self.merge_time(suite)
        self.current = self.current.parent

    def merge_missing_tests(self, suite):
        cur = self.current
        for test in suite.tests:
            if not any(t.longname == test.longname for t in cur.tests):
                test.parent = cur
                cur.tests.append(test)

    def merge_time(self, suite):
        cur = self.current
        cur.endtime = max([cur.endtime, suite.endtime])
        cur.starttime = min([cur.starttime, suite.starttime])

    def visit_message(self, msg):
        if msg.html and re.search(r'src="([^"]+\.png)"', msg.message):
            parent = msg.parent
            while not isinstance(parent, TestSuite):
                parent = parent.parent
            suites_names = parent.longname.split('.')
            if self._tests_root_name:
                suites_names[0] = self._tests_root_name
            prefix = '.'.join(suites_names)
            msg.message = re.sub(r'"([^"]+\.png)"',
                                 r'"%s-\1"' % prefix, msg.message)


class ResultsCombiner(CombinedResult):

    def add_result(self, other):
        for suite in other.suite.suites:
            self.suite.suites.append(suite)
        self.errors.add(other.errors)


def group_by_root(results, critical_tags, non_critical_tags):
    groups = {}
    for src in results:
        res = ExecutionResult(src)
        res.suite.set_criticality(critical_tags, non_critical_tags)
        groups[res.suite.name] = groups.get(res.suite.name, []) + [res]
    return groups


def merge_groups(results, critical_tags, non_critical_tags, tests_root_name):
    merged = []
    for group in group_by_root(results, critical_tags,
                               non_critical_tags).values():
        base = group[0]
        merger = ResultMerger(base, tests_root_name)
        for out in group:
            merger.merge(out)
        merged.append(base)
    return merged


def merge(result_files, rebot_options, tests_root_name):
    assert(len(result_files) > 0)
    settings = RebotSettings(rebot_options)
    merged = merge_groups(result_files, settings.critical_tags,
                          settings.non_critical_tags, tests_root_name)
    if len(merged) == 1:
        return merged[0]
    else:
        return ResultsCombiner(merged)
