import logging

import autostudent.scraper as scraper
import autostudent.repository.course as course_repo
import autostudent.repository.lesson as lesson_repo
import autostudent.summarize as summarize
import asyncpg
import meilisearch

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(processName)s %(threadName)s | %(message)s',
)


async def process_courses_and_lessons(db_pool: asyncpg.Pool, meilisearch_client: meilisearch.Client):
    for semester in reversed(scraper.terms):  # Проходимся по семестрам с конца
        logging.info(f"Processing semester: {semester}")
        courses = scraper.get_courses(semester)
        logging.info(f"Courses in semester: {courses}")

        for course in courses:
            conn: asyncpg.Connection
            async with db_pool.acquire() as conn:
                async with conn.transaction():
                    try:
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
                                    # TODO: вызов jobы которая делает рассылку
                                    await summarize.add_summary_to_meilisearch(summary, lesson_id, meilisearch_client)
                    except Exception:
                        logging.exception(f"An error occured while parsing course {course}")
