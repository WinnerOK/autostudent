INSERT INTO autostudent.courses(
  id,
  name,
  lms_url
) VALUES (
  1,
  'Algorithms and data structures. Semester 2',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/45/groups/53'
), (
  2,
  'Parallel and high-performance computing',
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
  'Lesson 1',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/45/groups/53/lessons/195'
), (
  2,
  1,
  'Lesson 2',
  'https://mhs.academy.yandex.ru/student/semesters/13/courses/45/groups/53/lessons/196'
), (
  3,
  2,
  'Lesson 1',
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
