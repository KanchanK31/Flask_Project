create table users(user_id serial primary key,user_name varchar(30),user_email varchar(30),user_password text);
create table category(category_id serial primary key,category_name varchar(30));
create table posts(post_id serial primary key,post_title varchar(50),post_content text,post_date date,category_id integer references category(category_id) on delete set null,user_id integer references users(user_id) on delete cascade);
create table comments(comment_id serial primary key,comment_content text,comment_date date,post_id integer references posts(post_id) on delete cascade,user_id integer references users(user_id) on delete set null);
