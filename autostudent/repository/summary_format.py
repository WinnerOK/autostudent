import json
import telebot.formatting as fmt


def format_sec(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def markdown_keypoints(video_url, keypoints_lst) -> str:
    keypoints = keypoints_lst
    if not isinstance(keypoints, list):
        keypoints = json.loads(keypoints_lst)
    timed_url_prefix = video_url.split('?')[0].replace('embed/', 'watch?v=') + "&t="
    md_content_str = ""
    for kp in keypoints:
        md_content_str += fmt.mlink(format_sec(kp['start_time']),
                                    timed_url_prefix + str(kp['start_time'])) + " " + fmt.mbold(
            fmt.escape_markdown(kp['content'] + '\n'))

        for thesis in kp['theses']:
            md_content_str += f"\\- {fmt.escape_markdown(thesis['content'])}\n"
        md_content_str += "\n"

    return md_content_str.strip()
