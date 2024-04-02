CREATE TABLE IF NOT EXISTS autostudent.courses (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS autostudent.lessons (
  id BIGSERIAL PRIMARY KEY,
  course_id BIGSERIAL REFERENCES autostudent.courses (id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS autostudent.youtube_summarization (
  youtube_video_url VARCHAR(100) PRIMARY KEY,
  lesson_id BIGSERIAL REFERENCES autostudent.lessons (id) ON DELETE CASCADE NOT NULL,
  summarization TEXT
);

CREATE INDEX youtube_summarization_lesson_id_index ON autostudent.youtube_summarization(lesson_id);
