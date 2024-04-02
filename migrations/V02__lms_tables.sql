CREATE TABLE IF NOT EXISTS autostudent.courses (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS autostudent.lessons (
  id BIGSERIAL PRIMARY KEY,
  course_id BIGSERIAL REFERENCES autostudent.courses (id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS autostudent.videos_summarization (
  video_url VARCHAR(255) PRIMARY KEY,
  lesson_id BIGSERIAL REFERENCES autostudent.lessons (id) ON DELETE CASCADE NOT NULL,
  summarization TEXT
);

CREATE INDEX videos_summarization_lesson_id_index ON autostudent.videos_summarization(lesson_id);
