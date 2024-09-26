import logging
import json
import threading
import queue
import time
import websocket
from service.base import BaseAPI
from service.api import moc_api_request

logger = logging.getLogger(__name__)


class EditorAPI(BaseAPI):
    _default = {}

    def __init__(self, key=None, api_client=None):
        super().__init__(key, api_client)
        # websocket.enableTrace(True)
        self.ws_msg_queue = queue.Queue(2)
        self.ws = websocket.WebSocketApp(
            f"wss:{self.api_client.configuration.host.split(':')[1]}/ws/query?token={self.api_client.default_headers.get('Access-Token')}",
            on_reconnect=lambda ws: logger.debug('[WebSocket] Reconnect to WS server.'),
            on_close=lambda ws, code, msg: logging.debug(f"[WebSocket] Connection closed with status code: {code}, message: {msg}"),
            on_error=lambda ws, err: logger.error(f'[WebSocket] {err}'),
            on_pong=lambda ws, data: logger.debug(f"[WebSocket] Receive pong message"),
            on_message=self.on_message
        )
        threading.Thread(target=self.ws.run_forever, kwargs={'ping_interval': 30, 'ping_timeout': 10, 'reconnect': 5}, daemon=True).start()
        start = time.time()
        while not self.ws.sock.sock:
            time.sleep(1)
            if time.time() - start >= 60:
                raise websocket.WebSocketConnectionClosedException("socket is already closed.")

    def on_message(self, ws, message):
        msg = json.loads(message)
        logger.debug(f"[WebSocket] Receive message: {msg}")
        if msg.get('message_type') == 'query_id':
            if not self.ws_msg_queue.empty():
                with self.ws_msg_queue.mutex:
                    self.ws_msg_queue.queue.clear()
            self.ws_msg_queue.put(msg)
        elif msg.get('message_type') == 'query_result':
            self.ws_msg_queue.put(msg)
        else:
            logger.debug(f"[WebSocket] Receive message not recognized.")

    @moc_api_request('/workbook/list', 'POST')
    def get_workbooks(self, offset=0, limit=100):
        return {"offset": offset, "limit": limit}

    @moc_api_request('/workbook/version/list', 'POST')
    def get_workbook_versions(self, _id, offset=0, limit=25):
        return {"workbook_id": _id, "offset": offset, "limit": limit}

    @moc_api_request('/workbook/create', 'POST')
    def create_workbook(self):
        return {}

    @moc_api_request('/workbook/update', 'POST')
    def update_workbook(self, _id, name):
        return {"name": name, "workbook_id": _id}

    @moc_api_request('/workbook/delete', 'POST')
    def delete_workbook(self, _id):
        return {"workbook_id": _id}

    @moc_api_request('/workbook/detail', 'POST')
    def get_workbook_details(self, _id, version_id):
        return {"workbook_id": _id, "version_id": version_id}

    @moc_api_request('/meta/table/info', 'POST')
    def get_table_info(self, _id, db, table):
        return {"db_name": db, "table_name": table}

    @moc_api_request('/workbook/version/create', 'POST')
    def create_workbook_version(self, _id, sql):
        return {"workbook_id": _id, "sql_content": sql}

    @moc_api_request('/workbook/version/update', 'POST')
    def update_workbook_version(self, _id, version_id, sql):
        return {"workbook_id": _id, "version_id": version_id, "sql_content": sql}

    @moc_api_request('/workbook/version/save', 'POST')
    def save_workbook_version(self, _id, version_id, sql):
        return {"workbook_id": _id, "version_id": version_id, "sql_content": sql}

    @moc_api_request('/query/result/download', 'POST')
    def download_query_result(self, statement_id):
        return {"statement_id": statement_id}

    @moc_api_request('/subscribe/tpchsample', 'POST')
    def load_tpch_sample_data(self):
        return {}

    def execute_sql(self, _id, sql, db='', sql_type='', offset=0, limit=1000, timeout=10 * 60):
        payload = {
            "id": _id,
            "message_type": "query_execute",
            "data": {
                "query": f'/* cloud_user */{sql}',
                "offset": offset,
                "limit": limit
            }
        }
        if db:
            payload['data']['db_name'] = f'`{db}`'
        if sql_type:
            payload['data']['sql_type'] = sql_type
        payload = json.dumps(payload)
        logger.debug(f"[WebSocket] Send and execute SQL: {payload}")
        self.ws.send_text(payload)
        message = self.ws_msg_queue.get(True, timeout)
        assert message['data']['code'] == 'OK' and message['data']['msg'] == 'OK' and message['id'] == _id and message[
            'message_type'] == 'query_id', message
        query_id = message['data']['data']['query_id']
        message = self.ws_msg_queue.get(True, timeout)
        assert message['data']['code'] == 'OK' and message['data']['msg'] == 'OK' and message['id'] == _id and message[
            'message_type'] == 'query_result' and message['data']['data']['query_id'] == query_id, message
        return message['data']['data']
