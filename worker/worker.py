import os
import json
import stomp
import time
import threading

# ActiveMQ configuration
host = os.environ.get('HOST_QUEUE', 'localhost')
port = os.environ.get('PORT_QUEUE', 61613)
hosts = [(host, port)]
name_queue = os.environ.get('NAME_QUEUE', 'worker')
user_queue = os.environ.get('USER_QUEUE', 'admin')
password_queue = os.environ.get('PWD_QUEUE', 'admin')
cliente_queue = 'worker'


def _stomp_connect(_conn):
    print('[Queue] Staring Connection')
    _conn.connect(user_queue, password_queue, headers={'client-id': cliente_queue})
    print('[Queue] New Connection')
    _conn.subscribe(destination=name_queue, id='1', ack='auto')
    print('[Queue] New subscribed to {}'.format(name_queue))


class ConnectionListener(stomp.ConnectionListener):
    def __init__(self, _conn, callback):
        self._conn = _conn
        self._callback = callback

    @staticmethod
    def on_error(message):
        print('[Queue] received an error "%s"' % message)

    def on_disconnected(self):
        print('[Queue] Queue disconnected')
        _stomp_connect(self._conn)

    def on_message(self, frame):
        print('[Queue] new message: {}'.format(frame.body))
        try:
            body_parsed = json.loads(frame.body.replace("'", '"'))
            self._callback(body_parsed)
        except Exception as ex:
            print('[Queue] catch error: {}'.format(str(ex)))


def __start_worker(callback):
    print('[Worker] Staring to "{}"'.format(name_queue))
    conn = stomp.Connection(host_and_ports=hosts)
    conn.set_listener('', ConnectionListener(conn, callback))
    _stomp_connect(conn)

    while True:
        time.sleep(1)


def run_worker(callback):
    active_mq_thread = threading.Thread(target=__start_worker, kwargs={'callback': callback},
                                        daemon=False)
    active_mq_thread.start()
