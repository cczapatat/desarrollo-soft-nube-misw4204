import os
import gc
import json
import datetime
from typing import Union
from google.cloud import pubsub_v1
from models.task import Task, Status
from models.declarative_base import session
from utils.video_util import process_video

project_id = os.environ.get('GCLOUD_PROJECT')
subscription_id = os.environ.get('NAME_SUB', 'videos-sub')


def __update_task__(task_id, status: Status, path_processed: Union[str, None]) -> bool:
    try:
        session.query(Task).filter(Task.id == task_id).update({
            'status': status,
            'path_processed': path_processed,
            'updated_at': datetime.datetime.now(),
        })
        session.commit()

        return True
    except Exception as ex:
        print('[Process][__update_task__] taskId: {}, error {}'.format(str(task_id), str(ex)))
        return False


def __process_and_update__(task_id, path_origin) -> Union[Task, bool]:
    result_process_video = process_video(path_origin)

    if 'path_processed' in result_process_video:
        status = Status.PROCESSED
        path_processed = result_process_video['path_processed']
    else:
        status = Status.ERROR
        path_processed = None

    task_updated = __update_task__(task_id, status, path_processed)
    print('[Process][__process_and_update__] result: {}'.format(str({
        "task_id": task_id,
        "status": status.value,
    })))

    return task_updated


def process(message):
    print(f"Received on pubSub: {message}")
    gc.collect()
    try:
        msn = (str(message.data)
               .replace('b"', '')
               .replace('"', '')
               .replace("'", '"'))
        input_data = json.loads(msn)
        print('[Process] New event: {}'.format(str(input_data)))
        task_id = input_data["id"]
        path_origin = input_data["path_origin"]

        if task_id is None or type(task_id) is not int:
            print('[Process] event is incorrect, input: {}'.format(str(input_data)))
            return

        if path_origin is None:
            print('[Process] path_origin {} is not exists'.format(str(task_id)))
            return

        __process_and_update__(task_id, path_origin)
        print('[Process] task_id {} ended'.format(str(task_id)))
    except Exception as ex:
        print(f"Error Generate during PubSub, ${str(ex)}")

    message.ack()
    gc.collect()


if __name__ == '__main__':
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    flow_control = pubsub_v1.types.FlowControl(max_messages=1)

    streaming_pull_future = subscriber.subscribe(
        subscription_path,
        callback=process,
        flow_control=flow_control,
    )

    print(f"Process_Listening for messages on {subscription_path}..\n")

    with subscriber:
        try:
            streaming_pull_future.result()
        except Exception as ex:
            print(f"Listening generated an error: {str(ex)}")
            streaming_pull_future.cancel()
            streaming_pull_future.result()
