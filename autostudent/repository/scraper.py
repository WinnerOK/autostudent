import requests
from bs4 import BeautifulSoup
import os

base_url = "https://mhs.academy.yandex.ru"
terms = ["12", "13"]


def get_page(url, params=None) -> requests.Response:
    session_id = os.getenv("YANDEX_SESSION_ID")
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36"
        }
    )
    session.cookies.update({"Session_id": session_id})
    return session.get(url=url, params=params)


def get_courses(semester=terms[-1]):
    response = get_page(f"{base_url}/student", params={"semester": semester})
    soup = BeautifulSoup(response.content, "html.parser")
    courses = []

    for link in soup.find_all("a", class_=lambda x: x and "course-card" in x):
        course_url = link.get("href")
        course_title = link.find(
            "h6", class_=lambda x: x and "t-title-s" in x
        ).text.strip()

        full_course_url = (
            f"{base_url}{course_url}"
            if not course_url.startswith(("http:", "https:"))
            else course_url
        )

        courses.append({"title": course_title, "url": full_course_url})

    return courses


def get_lessons(url):
    response = get_page(url)
    soup = BeautifulSoup(response.content, "html.parser")
    lectures = []

    for lesson in soup.find_all(class_=lambda x: x and "styles_lesson-row__" in x):
        lectures.append(
            {"title": lesson.text.strip(), "url": f"{base_url}{lesson.get('href')}"}
        )
        pass
    return lectures


def get_youtube_videos(url):
    response = get_page(url)
    soup = BeautifulSoup(response.content, "html.parser")
    lectures = []

    for lesson in soup.find_all("iframe"):
        if "youtube" not in lesson.get("src", ""):
            continue
        src = lesson.get("src")
        video_url = src if src.startswith("http") else f"https:{src}"
        lectures.append({"url": video_url})
    return lectures


def get_youtube_and_yandex_videos(url):
    response = get_page(url)
    soup = BeautifulSoup(response.content, "html.parser")
    resources = []

    # Поиск YouTube видео
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if "youtube" in src:
            video_url = src if src.startswith("http") else f"https:{src}"
            resources.append({"type": "YouTube", "url": video_url})

    # Поиск ссылок на Yandex Disk
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if "disk.yandex.ru" in href:
            resources.append({"type": "Yandex Disk", "url": href})

    return resources


def get_lessons_with_videos(course_url):
    lessons = get_lessons(course_url)
    courses_and_videos = []

    for lesson in lessons:
        lesson_url = lesson["url"]

        videos = get_youtube_videos(lesson_url)

        courses_and_videos.append(
            {"title": lesson["title"], "url": lesson_url, "youtube": videos}
        )

    return courses_and_videos
