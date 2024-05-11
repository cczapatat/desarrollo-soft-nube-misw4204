import os
import gc
from datetime import datetime
from faker import Faker
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.fx.all import crop
from .storage import download_blob
from .storage import upload_file
from werkzeug.utils import secure_filename
import tempfile

pcd_threads = int(os.environ.get('TOTAL_THREADS', '2'))

# Videos Results configuration
video_ext = os.environ.get('OUT_EXT_VIDEOS', 'mp4')
video_max_duration = int(os.environ.get('MAX_DIRECTION_VIDEOS', 20))

dirname = os.path.dirname(__file__)
dir_frames = '{}/../frames'.format(dirname)

out_result_path = os.environ.get('OUT_FILE_VIDEOS', '')
out_result_path_gs = os.environ.get('OUT_GS_FILE_VIDEOS')
is_out_result_path_filled = len(out_result_path) > 0

if is_out_result_path_filled:
    out_result_file = out_result_path
else:
    out_result_file = '{}/../../videos/outs'.format(dirname)

faker = Faker()


# Helper function that computes the filepath to save files to
def get_file_path(filename):
    # Note: tempfile.gettempdir() points to an in-memory file system
    # on GCF. Thus, any files in it must fit in the instance's memory.
    file_name = secure_filename(filename)
    return os.path.join(tempfile.gettempdir(), file_name)


def process_video(path):
    gc.collect()
    if not os.path.exists('/backend/videos/gs/ins'):
        os.makedirs('/backend/videos/gs/ins')
    download_blob(path, '/backend/videos/gs/' + path)

    video = get_video_buffer('/backend/videos/gs/' + path)

    if type(video) is str:
        return {"end": False, "status": "error", "message": video}

    width_original = video.w
    height_original = video.h
    print('[VideoUtil] Video size original: path: {}, W: {}, H: {}'.format(
        path,
        str(width_original),
        str(height_original)),
    )

    video = resize_video(video)

    if type(video) is str:
        return {"end": False, "status": "error", "message": video}

    video = add_frames(video)

    if type(video) is str:
        return {"end": False, "status": "error", "message": video}

    response_save = save_new_video(video)

    if os.path.exists('/backend/videos/gs/' + path):
        os.remove('/backend/videos/gs/' + path)
    gc.collect()

    if type(response_save) is str:
        return {"end": False, "status": "error", "message": response_save}

    return {"path_processed": response_save["path_processed"]}


def save_new_video(video):
    try:
        date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        uuid = faker.unique.iban()
        path = '{}/{}_{}.{}'.format(out_result_path_gs, date, uuid, video_ext)
        path_temp = '/backend/videos/gs/' + path
        if not os.path.exists('/backend/videos/gs/outs'):
            os.makedirs('/backend/videos/gs/outs')
        print('[VideoUtil][save_new_video] Start new video, {}'.format(str(datetime.now())))
        print('[VideoUtil][save_new_video] Path temp, {}'.format(path_temp))
        print('[VideoUtil][save_new_video] Path GS, {}'.format(path))

        video.write_videofile(path_temp, logger=None, fps=25, threads=pcd_threads, preset='ultrafast')
        print('[VideoUtil][save_new_video] video saved')
        video.close()
        del video

        upload_file(path_temp, path)
        print("[VideoUtil][save_new_video] Uploaded new video, {}".format(path))
        if os.path.exists(path_temp):
            os.remove(path_temp)
        print('[VideoUtil][save_new_video] Finished new video, {}'.format(str(datetime.now())))

        return {"path_processed": path}
    except Exception as ex:
        print('[VideoUtil][save_new_video] error {}'.format(str(ex)))
        del video
        gc.collect()
        return str(ex)


def add_frames(video):
    try:
        start_frame = (ImageClip("{}/start_frame.jpg".format(dir_frames))
                       .set_start(0).set_duration(1)
                       .set_pos(("center", "center")))
        end_frame = (ImageClip("{}/end_frame.jpeg".format(dir_frames))
                     .set_start(video.duration + 1).set_duration(1)
                     .set_pos(("center", "center")))
        video = (video.set_start(1).set_pos(("center", "center")))
        video = CompositeVideoClip([start_frame, video, end_frame])
        start_frame.close()
        end_frame.close()
        del start_frame
        del end_frame
        print('[VideoUtil][add_frames] New Video')

        return video
    except Exception as ex:
        print('[VideoUtil][add_frames] error {}'.format(str(ex)))
        video.close()
        del video
        gc.collect()
        return str(ex)


def resize_video(video):
    try:
        (w, h) = video.size
        crop_width = h * (16 / 9)
        x1, x2 = (w - crop_width) // 2, (w + crop_width) // 2
        y1, y2 = 0, h
        video = crop(video, x1=x1, y1=y1, x2=x2, y2=y2)
        width_new = video.w
        height_new = video.h
        print('[VideoUtil][resize_video] New Video size: W: {}, H: {}'.format(str(width_new), str(height_new)))

        return video
    except Exception as ex:
        print('[VideoUtil][resize_video] error {}'.format(str(ex)))
        video.close()
        del video
        gc.collect()
        return str(ex)


def get_video_buffer(path: str):
    try:
        video = VideoFileClip(path)
        duration_current = video.duration
        max_duration = video_max_duration if duration_current > video_max_duration else duration_current

        video = video.subclip(0, max_duration)

        return video
    except Exception as ex:
        print('[VideoUtil][get_video_buffer] error {}'.format(str(ex)))
        gc.collect()
        return str(ex)
