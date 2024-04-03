import autostudent as scraper
import autostudent.repository.course as course_repo
import autostudent.repository.lesson as lesson_repo

import asyncpg


async def process_courses_and_lessons(conn: asyncpg.Connection):
    for semester in reversed(scraper.terms):  # Проходимся по семестрам с конца
        courses = scraper.get_courses(semester)
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

            lessons = scraper.get_lessons_with_videos(course["url"])
            for lesson in lessons:
                existing_lesson = await lesson_repo.check_exsisting_lesson(
                    lesson["title"], course_id
                )
                if not existing_lesson:
                    lesson_id = await lesson_repo.insert_lesson(
                        conn, course_id, lesson["title"], None, lesson["url"]
                    )
                    if lesson["type"] == "YouTube":
                        # TODO SUMMARY
                        pass