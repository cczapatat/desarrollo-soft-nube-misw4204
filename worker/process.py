from flask import Flask
from flask_restful import Api
import stomp
import json
import threading
import time
import os

app = Flask(__name__)

# ActiveMQ configuration
host = os.environ.get('HOST_QUEUE', 'localhost')
port = os.environ.get('PORT_QUEUE', 61616)
hosts = [(host, port)]
queue_name_one = os.environ.get('QUEUE_NAME_ONE', 'one')
user_queue = os.environ.get('HOST_QUEUE_USER', 'admin')
password_queue = os.environ.get('HOST_QUEUE_PWD', 'admin')
api = Api(app)


# ActiveMQ Listener
class WorkerListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        with app.app_context():
            print('[on_message] Processing new messages: {}'.format(frame.body))
            message_translated = json.loads(frame.body.replace("'", '"'))
            print(message_translated)


def active_mq_listener():
    conn = stomp.Connection(host_and_ports=hosts)
    conn.set_listener('', WorkerListener())
    # conn.start()
    conn.connect(user_queue, password_queue, wait=True)
    conn.subscribe(destination=queue_name_one, id='1', ack='auto')
    print(f"Subscribed to ActiveMQ queue: {queue_name_one}")

    while True:
        time.sleep(1)  # Keep the thread alive


if __name__ == '__main__':
    active_mq_thread = threading.Thread(target=active_mq_listener, daemon=True)
    active_mq_thread.start()

    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=False)
