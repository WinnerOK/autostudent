import logging

import autostudent.scraper as scraper
import autostudent.repository.course as course_repo
import autostudent.repository.lesson as lesson_repo
import autostudent.summarize as summarize
import asyncpg

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(processName)s %(threadName)s | %(message)s',
)


async def process_courses_and_lessons(conn: asyncpg.Connection):
    for semester in reversed(scraper.terms):  # Проходимся по семестрам с конца
        logging.info(f"Processing semester: {semester}")
        courses = scraper.get_courses(semester)
        logging.info(f"Courses in semester: {courses}")
        for course in courses:
            existing_course = await course_repo.check_exsisting_course(
                conn, course["title"], course["url"]
            )

            if not existing_course:
                course_id = await course_repo.insert_course(
                    conn, course["title"], course["url"]
                )
            else:
                course_id = existing_course[0]["id"]

            logging.info(f"Scrapping lessons for course: {course}")
            lessons = scraper.get_lessons_with_videos(course["url"])
            logging.info(f"Lessons: {lessons}")
            for lesson in lessons:
                existing_lesson = await lesson_repo.check_exsisting_lesson(
                    conn, lesson["title"], course_id
                )
                if not existing_lesson:
                    lesson_id = await lesson_repo.insert_lesson(
                        conn, course_id, lesson["title"], None, lesson["url"]
                    )
                    if lesson["type"] == "YouTube":
                        logging.info(f"Getting summary for: {lesson}")
                        summary = await summarize.get_summarization(
                            video_url=lesson["video_url"],
                            lesson_id=lesson_id,
                            conn=conn,
                        )
                        print(summary)
                        logging.info(f"Summary done: {lesson}")
                        # TODO: вызов jobы которая делает рассылку
                        # TODO: Сохранение в бд для поиска по тексту
