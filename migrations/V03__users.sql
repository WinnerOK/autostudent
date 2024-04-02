create table if not exists autostudent.users (
    chat_id bigint primary key
);

create table if not exists autostudent.subscriptions (
    chat_id bigint references autostudent.users(chat_id) on delete cascade,
    course_id bigint references autostudent.courses(id) on delete cascade,

    primary key (chat_id, course_id)
);

create index idx_subscriptions_course_id on autostudent.subscriptions(course_id);
create index idx_subscriptions_chat_id on autostudent.subscriptions(chat_id);
