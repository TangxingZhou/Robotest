import sys
import requests


class JiraService(object):

    def __init__(self, host='https://xxx', project_key=''):
        self._host = host
        self._project_key = project_key
        self.__session = requests.Session()
        requests.packages.urllib3.disable_warnings()
        self.log_in = False

    def login(self, user, password):
        res = self.__session.post('{host}/jira/rest/auth/1/session'.format(host=self._host),
                                  json={'username': user, 'password': password}, verify=False)
        if res.status_code == 200:
            self.log_in = True

    def update_test_status_in_cycle(self, version_name, cycle_name, issue_key, status):
        if self._get_issue_type(issue_key) == 'Test':
            executions = self._get_executions_in_cycle(version_name, cycle_name)
            if status == 'PASS':
                status_code = 1
            elif status == 'FAIL':
                status_code = 2
            else:
                return
            if issue_key in executions:
                execution_id = executions[issue_key]
                self._update_execution_status(execution_id, status_code)
            else:
                res = self._add_test_into_cycle(version_name, cycle_name, issue_key)
                if res.status_code == 200:
                    sys.stdout.write('[JIRA INFO]: Success to add {} into version of {} and cycle of {}.'
                                     .format(issue_key, version_name, cycle_name))
                    execution_id = tuple(res.json().keys())[0]
                    self._update_execution_status(execution_id, status_code)
                else:
                    sys.stdout.write('[JIRA ERROR]: Fail to add {} into version of {} and cycle of {}.'
                                     .format(issue_key, version_name, cycle_name))
        else:
            sys.stdout.write('[JIRA WARN]: {} is not Test, ignore it.'.format(issue_key))

    def _get_project_id(self):
        project_id = self._get_value_from_response(self.__get('/jira/rest/api/2/project/{projectIdOrKey}'
                                                              .format(projectIdOrKey=self._project_key)), 'id')
        if project_id is None:
            sys.stdout.write('[JIRA ERROR]: Fail to get project id by key of {}.'.format(self._project_key))
        return project_id

    def _get_fix_version_id(self, version_name):
        res = self.__get('/jira/rest/api/2/project/{projectIdOrKey}/versions'.format(projectIdOrKey=self._project_key))
        if res is None:
            return
        try:
            return next(filter(lambda item: item['name'] == version_name, res))['id']
        except StopIteration:
            sys.stdout.write('[JIRA ERROR]: Fail to get version id by name of {}.'.format(version_name))

    def _get_test_cycle_id(self, version_name, cycle_name):
        project_id = self._get_project_id()
        version_id = self._get_fix_version_id(version_name)
        if project_id is None or version_id is None:
            return
        else:
            res = self.__get('/jira/rest/zapi/latest/cycle', params={'projectId': project_id, 'versionId': version_id})
            if res is None:
                return
            for k, v in res.items():
                if k == 'recordsCount':
                    continue
                if v['name'] == cycle_name:
                    return k
            sys.stdout.write('[JIRA ERROR]: Fail to get cycle id by name of {}.'.format(cycle_name))

    def _get_executions_in_cycle(self, version_name, cycle_name):
        executions = {}
        project_id = self._get_project_id()
        version_id = self._get_fix_version_id(version_name)
        cycle_id = self._get_test_cycle_id(version_name, cycle_name)
        if project_id is not None and version_id is not None and cycle_id is not None:
            values = self._get_value_from_response(
                self.__get('/jira/rest/zapi/latest/execution',
                           params={'projectId': project_id, 'versionId': version_id, 'cycleId': cycle_id}), 'executions')
            if values is not None:
                for execution in values:
                    executions[execution['issueKey']] = execution['id']
        return executions

    def _get_execution_status(self, execution_id):
        status = self._get_value_from_response(self.__get('/jira/rest/zapi/latest/execution/{id}'
                                                          .format(id=execution_id)), 'execution.executionStatus')
        if status is None:
            sys.stdout.write('[JIRA ERROR]: Fail to get status of execution by id of {}.'.format(execution_id))
        return status

    def _update_execution_status(self, execution_id, status_code):
        self.__put('/jira/rest/zapi/latest/execution/{id}/execute'.format(id=execution_id), json={'status': status_code})

    def _add_test_into_cycle(self, version_name, cycle_name, issue_key):
        project_id = self._get_project_id()
        version_id = self._get_fix_version_id(version_name)
        cycle_id = self._get_test_cycle_id(version_name, cycle_name)
        issue_id = self._get_issue_field(issue_key, 'id')
        if project_id is not None and version_id is not None and cycle_id is not None and issue_id is not None:
            return self.__session.post('{host}/jira/rest/zapi/latest/execution'.format(host=self._host),
                                       json={'projectId': project_id, 'versionId': version_id, 'cycleId': cycle_id, 'issueId': issue_id})

    def _get_issue_field(self, issue_key, field_path):
        value = self._get_value_from_response(self.__get('/jira/rest/api/2/issue/{issueIdOrKey}'
                                                         .format(issueIdOrKey=issue_key)), field_path)
        if value is None:
            sys.stdout.write('[JIRA ERROR]: Fail to get field of issue {} by path of {}.'.format(issue_key, field_path))
        return value

    def _get_issue_type(self, issue_key):
        return self._get_issue_field(issue_key, 'fields.issuetype.name')

    @classmethod
    def _get_value_from_response(cls, response, field_path=''):
        if response is not None:
            value = response
            for path in field_path.split('.'):
                if path in value:
                    value = value[path]
                else:
                    return
            return value

    def __get(self, path, status_code=200, **kwargs):
        res = self.__session.get('{host}{path}'.format(host=self._host, path=path), **kwargs)
        if res.status_code == status_code:
            return res.json()
        else:
            sys.stdout.write('[JIRA ERROR]({}): {}.'.format(res.status_code, res.text))

    def __post(self, path, status_code=200, **kwargs):
        res = self.__session.post('{host}{path}'.format(host=self._host, path=path), **kwargs)
        if res.status_code != status_code:
            sys.stdout.write('[JIRA ERROR]({}): {}.'.format(res.status_code, res.text))

    def __put(self, path, status_code=200, **kwargs):
        res = self.__session.put('{host}{path}'.format(host=self._host, path=path), **kwargs)
        if res.status_code != status_code:
            sys.stdout.write('[JIRA ERROR]({}): {}.'.format(res.status_code, res.text))
