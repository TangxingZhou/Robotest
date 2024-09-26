
class Workbook:

    def __init__(self, **kwargs):
        self.workbook_id = kwargs.get('workbook_id')
        self.name = kwargs.get('name')


class WorkbookVersion:

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.status = kwargs.get('status')


class WorkbookVersionDetail:

    def __init__(self, **kwargs):
        self.created_at = kwargs.get('created_at')
        self.sql_content = kwargs.get('sql_content')
        self.updated_at = kwargs.get('updated_at')


class TableColumnSchema:

    def __init__(self, **kwargs):
        self.data_type = kwargs.get('data_type')
        self.default_value = kwargs.get('default_value')
        self.key_type = kwargs.get('key_type')
        self.name = kwargs.get('name')
        self.nullable = kwargs.get('nullable')


class QueryResult:
    
    def __init__(self, **kwargs):
        self.err_msg = kwargs.get('err_msg')
        self.query_id = kwargs.get('query_id')
        self.statement_id = kwargs.get('statement_id')
        self.db_name = kwargs.get('db_name')
        self.status = kwargs.get('status')
        self.total: int = kwargs.get('total')
        self.limit: int = kwargs.get('limit')
        self.columns = kwargs.get('columns', [])
        self.empty_set = kwargs.get('empty_set')
        self.msg = kwargs.get('empty_set', {}).get('msg')
        self.rows = []
        for i, r in enumerate(kwargs.get('result', [])):
            row = {}
            if len(r) == len(self.columns):
                for j, c in enumerate(r):
                    if c.get('Valid') is True:
                        row[self.columns[j]['name']] = c.get('String')
                    else:
                        raise ValueError(f"Value of column[{j}] '{self.columns[j]['name']}' in row[{i}] '{r}' is not valid.")
            else:
                raise ValueError(f"Column values in row[{i}] '{r}' do not match columns schema '{self.columns}'.")
            self.rows.append(row)

    def get_column_type(self, column_name=''):
        _types = {}
        for c in self.columns:
            _types[c['name']] = c['type']
        if column_name:
            return _types.get(column_name)
        else:
            return _types
