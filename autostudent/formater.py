import json


def json_to_markdown(json_data, video_url):
    data = json.loads(json_data)

    output = ""
    for lecture in data:
        start_time_link = f"{video_url}?t={lecture['start_time']}"
        output += f"[{lecture['content']}]({start_time_link})\n"
        for thesis in lecture["theses"]:
            output += f"- **Thesis {thesis['id']}:** {thesis['content']}\n"
        output += "\n"

    return output


def prepare_makdown_summary(summary, lesson_url, video_url, course_name):
    md_summary = f"Вышла новая лекция на курсе {course_name}\n\n"
    md_summary += f"[Ссылка на лекцию]({lesson_url})\n"
    md_summary += f"[Ссылка на видео]({video_url})\n\n"
    md_summary += json_to_markdown(summary, video_url)

    return md_summary
