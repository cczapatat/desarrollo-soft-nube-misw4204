import os
from datetime import datetime
from faker import Faker
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.fx.all import crop

# Videos Results configuration
video_ext = os.environ.get('OUT_EXT_VIDEOS', 'mp4')
video_max_duration = int(os.environ.get('MAX_DIRECTION_VIDEOS', 20))

dirname = os.path.dirname(__file__)
dir_frames = '{}/../frames'.format(dirname)

out_result_path = os.environ.get('OUT_FILE_VIDEOS', '')
is_out_result_path_filled = len(out_result_path) > 0

if is_out_result_path_filled:
    out_result_file = out_result_path
else:
    out_result_file = '{}/../../videos/outs'.format(dirname)

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

    if type(new_video) is str:
        return {"end": False, "status": "error", "message": new_video}

    video_frames = add_frames(new_video)

    if type(video_frames) is str:
        return {"end": False, "status": "error", "message": video_frames}

    response_save = save_new_video(video_frames)

    if type(response_save) is str:
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


def add_frames(new_video):
    try:
        start_frame = (ImageClip("{}/start_frame.jpg".format(dir_frames))
                       .set_start(0).set_duration(1)
                       .set_pos(("center", "center"))
                       .resize(height=new_video.h, width=new_video.w))
        end_frame = (ImageClip("{}/end_frame.jpeg".format(dir_frames))
                     .set_start(new_video.duration + 1).set_duration(1)
                     .set_pos(("center", "center"))
                     .resize(height=new_video.h, width=new_video.w))
        video_frame = (new_video.set_start(1).set_pos(("center", "center")))
        video_frames = CompositeVideoClip([start_frame, video_frame, end_frame])

        return video_frames
    except Exception as ex:
        print('[VideoUtil][resize_video] error {}'.format(str(ex)))
        return str(ex)


def resize_video(video):
    try:
        (w, h) = video.size
        crop_width = h * (16 / 9)
        x1, x2 = (w - crop_width) // 2, (w + crop_width) // 2
        y1, y2 = 0, h
        new_video = crop(video, x1=x1, y1=y1, x2=x2, y2=y2)
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
