from typing import Union
from worker import run_worker
from models.task import Task
from models.declarative_base import session
from utils.video_util import process_video


def __get_task__(task_id: int) -> Union[Task, None]:
    try:
        task = session.query(Task).filter(Task.id == task_id).one_or_none()

        return task
    except Exception as ex:
        print('[Process][get_task] error {}'.format(str(ex)))
        return None


def process(input):
    print('[Process] New event: {}'.format(str(input)))
    task_id = input["id"]

    if task_id is None or type(task_id) is not int:
        print('[Process] event is incorrect, input: {}'.format(str(input)))
        return

    task = __get_task__(task_id)

    if task is None:
        print('[Process] task {} is not exists'.format(str(task_id)))
        return

    video = process_video(task.path_origin)

    # TODO: Logica de actualizar la BD de acuerdo al resultado
    if type(video) is dict:
        print('[Process] mal procesamiento')
    else:
        print('[Process] buen procesamiento')


if __name__ == '__main__':
    run_worker(process)
