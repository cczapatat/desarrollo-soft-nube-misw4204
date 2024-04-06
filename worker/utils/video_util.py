from moviepy.editor import VideoFileClip


def process_video(path):
    video = get_video_buffer(path)

    if type(video) is str:
        return {"end": False, "status": "error", "message": video}

    width_original = video.w
    height_original = video.h
    print('[VideoUtil] Video size original: W: {}, H: {}'.format(str(width_original), str(height_original)))

    new_video = resize_video(video)

    if type(video) is str:
        return {"end": False, "status": "error", "message": new_video}

    return new_video


def resize_video(video):
    try:
        new_video = video.resize((1920, 1080))

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

        return video
    except Exception as ex:
        print('[VideoUtil][get_video_buffer] error {}'.format(str(ex)))
        return str(ex)
