import datetime
from typing import Union
from worker import run_worker
from models.task import Task, Status
from models.declarative_base import session
from utils.video_util import process_video


def __get_task__(task_id: int) -> Union[Task, None]:
    try:
        task = session.query(Task).filter(Task.id == task_id).one_or_none()

        return task
    except Exception as ex:
        print('[Process][get_task] error {}'.format(str(ex)))
        return None


def __update_task__(task: Task, status: Status, path_processed: Union[str, None]) -> Union[Task, None]:
    try:
        task.status = status
        task.path_processed = path_processed
        task.updated_at = datetime.datetime.now()
        session.commit()

        return task
    except Exception as ex:
        print('[Process][__update_task__] taskId: {}, error {}'.format(str(task.id), str(ex)))
        return None


def __process_and_update__(task: Task) -> Union[Task, None]:
    result_process_video = process_video(task.path_origin)
    result_is_correct = True if result_process_video['path_processed'] is not None else False

    status = Status.ERROR if not result_is_correct else Status.PROCESSED
    path_processed = None if not result_is_correct else result_process_video['path_processed']

    task_updated = __update_task__(task, status, path_processed)
    print('[Process][__process_and_update__] result: {}'.format(str({
        "task_id": task.id,
        "status": status.value,
        "path_processed": path_processed,
    })))

    return task_updated


def process(input_data):
    print('[Process] New event: {}'.format(str(input_data)))
    task_id = input_data["id"]

    if task_id is None or type(task_id) is not int:
        print('[Process] event is incorrect, input: {}'.format(str(input_data)))
        return

    task = __get_task__(task_id)

    if task is None:
        print('[Process] task {} is not exists'.format(str(task_id)))
        return

    __process_and_update__(task)


if __name__ == '__main__':
    run_worker(process)
