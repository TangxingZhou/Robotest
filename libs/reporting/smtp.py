import smtplib
from email.mime.text import MIMEText
from email.header import Header

REPORT_STYLE = '''
<style>p {font-family:Calibri;} h3 {font-family:Calibri;} td {padding: 6px; border:1px solid #666666;} th
{border:collapse; padding: 6px; border:1px solid #666666; text-align: left !important; background:#008ce6; color: white;}
table {border:0; font-family:Calibri; font-size:14px; border-collapse: collapse;}</style>
'''
REPORT_TEMPLATE = '''
<h3>Summary</h3>
<p>The <strong>{tr_name}</strong> test has finished with a status of <strong>{status}</strong>.</p>
<p>Please check <a href="{report_dashboard_url}/testrun.aspx?trid={trid}">Results Dashboard</a> for further details.</p>
{test_run_result_table}
<p>To check TeamCity <a href="https://teamcity.com/viewLog.html?buildId={teamcity_build_id}&buildTypeId=
{teamcity_build_type_id}&tab={teamcity_build_results_tab}">Build {teamcity_build_number}</a> for detailed logs.</p>
<br/><hr>
<h3>Failed Tests</h3>
{tests_fail_result_table}
<h3>Passed Tests</h3>
{tests_pass_result_table}
'''


class EmailReport(object):

    def __init__(self, host, sender, receivers, port=25):
        self.__smtp = smtplib.SMTP(host, port)
        self.__sender = sender
        self.__receivers = receivers

    def send(self, db_client, tr_id, tr_name, **kwargs):
        message = EmailMessage(db_client)
        msg_body = message.generate_msg(tr_id, tr_name, **kwargs)
        email_msg = MIMEText(msg_body, _subtype='html', _charset='utf-8')
        email_msg['Subject'] = Header('{} - {}'.format(message.tr_status, tr_name), 'utf-8')
        email_msg['From'] = self.__sender
        email_msg['To'] = ','.join(self.__receivers)
        self.__smtp.sendmail(self.__sender, self.__receivers, email_msg.as_string())


class EmailMessage(object):

    def __init__(self, db_client, template=REPORT_TEMPLATE):
        self._template = template
        self.__tr_status = 'PASS'
        self.__db_client = db_client

    @property
    def tr_status(self):
        return self.__tr_status

    @tr_status.setter
    def tr_status(self, status_code):
        if status_code == 1:
            self.__tr_status = 'PASS'
        elif status_code == 2:
            self.__tr_status = 'FAIL'
        else:
            self.__tr_status = 'WARNING'

    def generate_msg(self, tr_id, tr_name, report_dashboard_url='http://xxx/results', **kwargs):
        test_run_table_template = \
            '<table>' \
            '  <thead>' \
            '    <tr>' \
            '      <th>#</th>' \
            '      <th>Test Set</th>' \
            '      <th>Start Time</th>' \
            '      <th>Duration</th>' \
            '      <th>Pass</th>' \
            '      <th>Fail</th>' \
            '      <th>Status</th>' \
            '    </tr>' \
            '  </thead>' \
            '  <tbody>' \
            '    {body}' \
            '  </tbody>' \
            '</table>'
        test_case_table_template = \
            '<table>' \
            '  <thead>' \
            '    <tr>' \
            '      <th>#</th>' \
            '      <th>Test Set</th>' \
            '      <th>Test Case</th>' \
            '      <th>Total Steps</th>' \
            '      <th>Passed Steps</th>' \
            '      <th>Failed Steps</th>' \
            '      <th>Status</th>' \
            '    </tr>' \
            '  </thead>' \
            '  <tbody>' \
            '    {body}' \
            '  </tbody>' \
            '</table>'
        test_run_body_row_template = \
            '<tr>' \
            '  <td style="text-align:center;">{ID}</td>' \
            '  <td><a href="{Report_Dashboard_URL}/testset.aspx?trid={TRID}&tsid={TSID}">{TSName}</a></td>' \
            '  <td>{StartTime}</td>' \
            '  <td>{Duration}</td>' \
            '  <td style="text-align:center;">{Pass}</td>' \
            '  <td style="text-align:center;">{Fail}</td>' \
            '  <td style="text-align:center;background:{Color}">{Status}</td>' \
            '</tr>'
        test_case_body_row_template = \
            '<tr>' \
            '  <td style="text-align:center;">{ID}</td>' \
            '  <td>{TSName}</td>' \
            '  <td><a href="{Report_Dashboard_URL}/testcase.aspx?trid={TRID}&tsid={TSID}&tcid={TCID}">{TCName}</a></td>' \
            '  <td style="text-align:center;">{Total}</td>' \
            '  <td style="text-align:center;">{Pass}</td>' \
            '  <td style="text-align:center;">{Fail}</td>' \
            '  <td style="text-align:center;background:{Color}">{Status}</td>' \
            '</tr>'
        test_run_result = tuple(self.__db_client.call_sp('getTestRunResults', (tr_id,)))
        tests_fail_result = tuple(self.__db_client.call_sp('getTestSetResultsFails', (tr_id,)))
        tests_pass_result = tuple(self.__db_client.call_sp('getTestSetResultsPass', (tr_id,)))
        test_run_table = EmailMessage.__generate_table(test_run_table_template, test_run_body_row_template, test_run_result)
        test_fail_table = EmailMessage.__generate_table(test_case_table_template, test_case_body_row_template, tests_fail_result)
        test_pass_table = EmailMessage.__generate_table(test_case_table_template, test_case_body_row_template, tests_pass_result)
        self.__tr_status = EmailMessage.__format_status(test_run_result[0]['TR_Status'])[1]
        return REPORT_STYLE + self._template.format(
            tr_name=tr_name,
            report_dashboard_url=report_dashboard_url,
            trid=tr_id,
            status=self.__tr_status,
            test_run_result_table=test_run_table,
            tests_fail_result_table=test_fail_table,
            tests_pass_result_table=test_pass_table,
            **kwargs
        )

    @staticmethod
    def __generate_table(table_template, row_template, rows_values=()):
        rows = []
        for i, row in enumerate(rows_values):
            row['ID'] = i + 1
            row['Report_Dashboard_URL'] = 'http://xxx/results'
            row['Color'], row['Status'] = EmailMessage.__format_status(row['TR_Status'])
            rows.append(row_template.format(**row))
        if len(rows) == 0:
            return ''
        else:
            return table_template.format(body='\n'.join(rows))

    @staticmethod
    def __format_status(status_code):
        if status_code == 1:
            return '#84bd00', 'PASS'
        elif status_code == 2:
            return '#ff2900', 'FAIL'
        else:
            return '#ed8800', 'WARNING'

    def __get_test_run_result(self, tr_id):
        return self.__db_client.call_sp('getTestRunResults', (tr_id,))
