import os
import gc
import datetime
from typing import Union
from models.task import Task, Status
from models.declarative_base import session
from utils.video_util import process_video

if os.environ.get('QUEUE_CLOUD_PROVIDER', 'true') == 'true':
    from pubsub import run_pubsub
else:
    from worker import run_worker


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


def process(input_data):
    gc.collect()
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
    gc.collect()


if __name__ == '__main__':
    if os.environ.get('QUEUE_CLOUD_PROVIDER', 'true') == 'true':
        run_pubsub(process)
    else:
        run_worker(process)
