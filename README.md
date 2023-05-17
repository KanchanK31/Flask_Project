## Online Discussion Forum
Here people can signup/login. Then They can post questions. Other users can comment on that post.
There also functionality of deleting the post.

database schema = {
    users = {
        user_id,user_name,user_email,user_password
    }

    category = {
        category_id, category_name
    }

    post = {
        post_id,post_title,post_content,post_date,category_id,user_id
    }

    comment = {
        comment_id,comment_content,comment_date,post_id,user_id
    }

}

toSet the database parameters before running Application -
the commands you can use-
export DATABASE_NAME='YOUR DATABASE NAME';
export DATABASE_USER='YOUR DATABASE USERNAME';
export DATABASE_PASSWORD='YOUR PASSWORD';
