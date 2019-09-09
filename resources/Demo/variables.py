# Define the variables for the project.

__author__ = 'Tangxing Zhou'

project = 'Demo'

# Sqlite
SQLITE_HOST = 'localhost'
SQLITE_PORT = 8081
SQLITE_USER = 'admin'
SQLITE_PSW = 'admin'
SQLITE_DB = 'demo'

# Email Report
EMAIL_SERVER = 'smtp.126.com'
EMAIL_SENDER_ACCOUNT = 'xxx@126.com'
EMAIL_SENDER_PSW = 'xxxxxx'
EMAIL_RECEIVERS = 'xxx@126.com'
EMAIL_TEMPLATE = 'resources/reporting/templates/email_report.html'

# Timeout config
TIME_OUT = 300
TIME_INTERVAL = 5


# def get_variables():
#     return {
#         'EMAIL_SERVER': EMAIL_SERVER,
#         'EMAIL_SENDER_ACCOUNT': EMAIL_SENDER_ACCOUNT,
#         'EMAIL_SENDER_PSW': EMAIL_SENDER_PSW,
#         'EMAIL_RECEIVERS': EMAIL_RECEIVERS,
#         'EMAIL_TEMPLATE': EMAIL_TEMPLATE,
#         'TIME_OUT': TIME_OUT,
#         'TIME_INTERVAL': TIME_INTERVAL
#     }
