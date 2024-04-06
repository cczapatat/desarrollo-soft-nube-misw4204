import os
from datetime import datetime
from faker import Faker
from moviepy.editor import VideoFileClip
from moviepy.video.fx.resize import resize

# Videos Results configuration
video_ext = os.environ.get('OUT_EXT_VIDEOS', 'mp4')
video_max_duration = int(os.environ.get('MAX_DIRECTION_VIDEOS', 20))
out_result_file = os.environ.get('OUT_FILE_VIDEOS', 'videos/outs')

faker = Faker()


def process_video(path):
    video = get_video_buffer(path)

    if type(video) is str:
        return {"end": False, "status": "error", "message": video}

    width_original = video.w
    height_original = video.h
    print('[VideoUtil] Video size original: path: {}, W: {}, H: {}'.format(
        path,
        str(width_original),
        str(height_original)),
    )

    new_video = resize_video(video)

    if type(video) is str:
        return {"end": False, "status": "error", "message": new_video}

    response_save = save_new_video(new_video)

    if type(video) is str:
        return {"end": False, "status": "error", "message": response_save}

    return {"path_processed": response_save["path_processed"]}


def save_new_video(new_video):
    try:
        date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        uuid = faker.unique.iban()
        path = '{}/{}_{}.{}'.format(out_result_file, date, uuid, video_ext)
        new_video.write_videofile(path)

        return {"path_processed": path}
    except Exception as ex:
        print('[VideoUtil][save_new_video] error {}'.format(str(ex)))
        return str(ex)


def resize_video(video):
    try:
        new_video = resize(video, width=1980, height=1080)

        width_new = new_video.w
        height_new = new_video.h
        print('[VideoUtil][resize_video] New Video size: W: {}, H: {}'.format(str(width_new), str(height_new)))

        return new_video
    except Exception as ex:
        print('[VideoUtil][resize_video] error {}'.format(str(ex)))
        return str(ex)


def get_video_buffer(path: str):
    try:
        video = VideoFileClip(path)
        duration_current = video.duration
        max_duration = video_max_duration if duration_current > video_max_duration else duration_current

        return video.subclip(0, max_duration)
    except Exception as ex:
        print('[VideoUtil][get_video_buffer] error {}'.format(str(ex)))
        return str(ex)
