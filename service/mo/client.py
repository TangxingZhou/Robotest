import time
import logging
import pymysql
from pymysql.cursors import Cursor
from sqlalchemy import URL, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from service.mo.models import *

logger = logging.getLogger(__name__)


class MOClient:

    def __init__(self, connection: pymysql.Connection = None, **kwargs):
        if 'read_timeout' not in kwargs:
            kwargs['read_timeout'] = 2 * 60
        self.__connect_args = kwargs
        if connection is None:
            start = time.time()
            while True:
                try:
                    connection = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **kwargs)
                    break
                except Exception as e:
                    logger.warning(
                        f"Failed to connect to {kwargs.get('user')}@{kwargs.get('host')}:{kwargs.get('port')}. {e}")
                    time.sleep(60)
                    if time.time() - start >= 5 * 60:
                        raise e
                    else:
                        continue
        self.connection = connection
        self.engine: Engine = self.mo_engine()

    def __repr__(self):
        return f"{self.__connect_args.get('username', self.__connect_args.get('user', ''))}:{self.__connect_args.get('password', '')}\
    @{self.__connect_args.get('host')}:{self.__connect_args.get('port', 6001)}/{self.__connect_args.get('database', '')}"

    def mo_engine(self) -> Engine:
        mo_url = URL.create(
            'mysql+pymysql',
            host=self.__connect_args.get('host'),
            username=self.__connect_args.get('username', self.__connect_args.get('user')),
            password=self.__connect_args.get('password'),
            port=self.__connect_args.get('port', 6001),
            database=self.__connect_args.get('database')
        )
        engine = create_engine(mo_url, echo=True, echo_pool=True, connect_args={'read_timeout': 2 * 60})
    
        @event.listens_for(engine, "before_execute", named=True)
        def receive_before_execute(conn, clauseelement, multiparams, params, **kw):
            conn.info['start_time'] = time.time()
    
        @event.listens_for(engine, "after_execute", named=True)
        def receive_after_execute(conn, clauseelement, multiparams, params, result, **kw):
            elapsed_time = time.time() - conn.info['start_time']
            params = multiparams[0] if multiparams else params
            if params:
                sql_statement = clauseelement.compile().string
                for key, value in params.items():
                    sql_statement = sql_statement.replace(f":{key}", repr(value))
            else:
                sql_statement = clauseelement.compile(dialect=engine.dialect, compile_kwargs={"literal_binds": True}).string
            logger.debug(f"SQL Statement: '{sql_statement}' executed in {elapsed_time:.4f} seconds")
        return engine

    @property
    def mo_session(self) -> sessionmaker:
        return sessionmaker(self.engine)

    def execute(self, sql, fetch=True, args=None):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql, args)
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                logger.error(f"Failed to execute query: {sql}. {e}")
                raise e
        if fetch:
            return cursor.fetchall()
        return cursor
    
    def _execute(self, sql, fetch=True, args=None):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(sql, args)
        if fetch:
            return cursor.fetchall()
        return cursor
    
    def execute_sql_file(self, sql_file):
        with open(sql_file, 'r') as file:
            sql = file.read()
        self.connection.ping()
        with self.connection.cursor() as cursor:
            for q in sql.split(';'):
                if q.strip('\n'):
                    cursor.execute(q.strip('\n'))
        self.connection.commit()
        return cursor

    def show_backend_servers(self):
        return self._execute('show backend servers;')

    def get_storage_size(self):
        result = self._execute('show accounts;')
        logger.debug(f"There are {len(result)} accounts in MO cluster.")
        storage_size = {}
        for r in result:
            storage_size[r['account_name']] = r['size']
        return storage_size

    def insert_cu_record(self,
                         account_id,
                         start_time=None,
                         end_time=None,
                         cu=10 * 10000,
                         _type='external_sql',
                         network: float = float(0),
                         object_in_api: float = float(0),
                         object_out_api: float = float(0)
                         ):
        if not (start_time and end_time):
            end_time = datetime.now(timezone.utc)
            start_time = (end_time + relativedelta(minutes=-1)).strftime('%Y-%m-%d %H:%M:01')
            end_time = end_time.strftime('%Y-%m-%d %H:%M:01')
        # with self.mo_session().begin() as session:
        #     session.add(CU(
        #         account=account_id,
        #         type=_type,
        #         start_time=start_time,
        #         end_time=end_time,
        #         cu=cu,
        #         network=network,
        #         object_in_api=object_in_api,
        #         object_out_api=object_out_api))
        sql = f"insert into mo_cloud.cu values ('{account_id}', '{start_time}', '{end_time}', {cu}, '{_type}', {network}, {object_in_api}, {object_out_api});"
        self.execute(sql, False)
