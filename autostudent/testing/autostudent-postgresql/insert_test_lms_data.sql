INSERT INTO autostudent.courses(
  id,
  name,
  lms_url
) VALUES (
  1,
  'course1',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/45/groups/53'
), (
  2,
  'course2',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/48/groups/56'
);


INSERT INTO autostudent.lessons(
  id,
  course_id,
  name,
  lms_url
) VALUES (
  1,
  1,
  'lesson1',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/45/groups/53/lessons/195'
), (
  2,
  1,
  'lesson2',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/45/groups/53/lessons/196'
), (
  3,
  2,
  'lesson1',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/48/groups/56/lessons/225'
);


INSERT INTO autostudent.videos_summarization(
  video_url,
  lesson_id,
  summarization
) VALUES (
  'https://www.youtube.com/watch?v=T2JULoQAheE',
  3,
  '{"keypoints":"something1"}'
), (
  'https://www.youtube.com/watch?v=u0upeEjU5EQ',
  1,
  '{"keypoints":"something2"}'
), (
  'https://www.youtube.com/watch?v=l4DmZVHSh8o',
  2,
  NULL
)
ON CONFLICT (video_url) DO NOTHING;
