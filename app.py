from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Flask, render_template,request,redirect,session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["session_cookie_name"] = 'session'
Session(app)

# Connect to PostgreSQL database
def get_db_conn():
    conn = psycopg2.connect(
        host="localhost",
        database=os.environ['DATABASE_NAME'],
        user=os.environ['DATABASE_USERNAME'],
        password=os.environ['DATABASE_PASSWORD']
    )
    return conn

# Index route
@app.route('/')
def index():
    conn = get_db_conn()
    data = []
    try:
        cur = conn.cursor()
        cur.execute('SELECT p.post_title,p.post_content,p.post_date,u.user_name,p.post_id FROM posts as p,users as u where p.user_id = u.user_id')
        data = cur.fetchall()
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    finally:
            cur.close()
            conn.close()
    return render_template('index.html',data=data)

@app.route('/delete/<int:id>')
def deletePost(id):
    if not session.get('user_name'):
          return redirect('/')
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('delete from posts where post_id = %s',(id,))
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    finally:
            conn.commit()
            cur.close()
            conn.close()
    return redirect('/')
 

@app.route('/update_post/<int:id>',methods=['GET'])
def update_blog(id):
       # Check if user is logged in, if not go back to home page
    if not session.get('user_name'):
        return redirect('/')
    
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users WHERE user_name = %s', (session['user_name'],))
        user = cur.fetchone()
        if user:
                user_id = user[0]
                cur.execute('SELECT * FROM posts WHERE post_id = %s', (id,))
                post = cur.fetchone()
                if(user_id != post[5]):
                     return redirect('/')
                conn.commit()
                cur.close()
                conn.close()
                return render_template('update_post.html',data=post)
        else:
            return render_template('index.html', message={'error':'Something went wrong'})
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    return render_template('update_post.html')

@app.route('/update_post/<int:id>',methods=['POST'])
def update_blog2(id):
       # Check if user is logged in, if not go back to home page
    if not session.get('user_name'):
        return redirect('/')
    
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users WHERE user_name = %s', (session['user_name'],))
        user = cur.fetchone()
        if user:
                user_id = user[0]
                cur.execute('SELECT * FROM posts WHERE post_id = %s', (id,))
                post = cur.fetchone()
                if(user_id != post[5]):
                     return redirect('/')
                post_title = request.form['post_title'] 
                post_content = request.form['post_content']
                cur.execute('update posts set post_title = %s,post_content=%s where post_id = %s', (post_title,post_content,id,))
                conn.commit()
                cur.close()
                conn.close()
                return redirect('/')
        else:
            return render_template('index.html', message={'error':'Something went wrong'})
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    return redirect('/')



@app.route('/view_post/<int:id>')
def view_post(id):
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('select p.post_title,p.post_content,p.post_date,u.user_name,p.post_id from posts as p,users as u where p.post_id = %s and p.user_id = u.user_id',(id,))
        post_data = cur.fetchone()
        cur.execute('select c.comment_id,c.comment_content,c.comment_date,u.user_name from comments as c,users as u where c.post_id = %s and c.user_id = u.user_id',(id,))
        comment_data = cur.fetchall()
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    finally:
            cur.close()
            conn.close()
    return render_template('view_post.html',data=[post_data,comment_data])

@app.route('/add_comment',methods=['POST'])
def add_comment():
    comment_content = request.form['comment_content']
    post_id = request.form['post_id']
    now = datetime.now()
    date_string = now.strftime('%Y-%m-%d')
    user_id = 0 # By default we are keeping user_id as 0, will fetch and overwrite user_id from DB

    # Check if user is logged in, if not go back to home page
    if not session.get('user_name'):
        return redirect('/')
    
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users WHERE user_name = %s', (session['user_name'],))
        user = cur.fetchone()
        if user:
                user_id = user[0]
                cur.execute('INSERT INTO comments(comment_content,comment_date,post_id,user_id) VALUES(%s,%s,%s,%s)',(comment_content,date_string,post_id,user_id))
                conn.commit()
                return redirect('/')
        else:
            return render_template('index.html', message={'error':'Something went wrong'})
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    finally:
            conn.commit()
            cur.close()
            conn.close()
    return redirect('/')

@app.route('/register',methods=['POST'])
def register():
    user_name = request.form['user_name']
    user_email = request.form['user_email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if(password != confirm_password):
        return render_template('index.html',message={'error':'passwords dont match'})
    
    # hash password
    hashed = generate_password_hash(password)
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE user_email = %s', (user_email,))
        user = cur.fetchone()
        if user:
            # Redirect to register page with error message if email already exists
            return render_template('index.html', message={'error':'Email already exists'})
        else:
            hashed =  generate_password_hash(password)
            cur.execute('INSERT INTO users (user_name, user_email, user_password) VALUES (%s, %s, %s)', (user_name,user_email,hashed))
            conn.commit()
            return redirect('/')
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    finally:
            cur.close()
            conn.close()

@app.route('/login',methods=['POST'])
def login():
    user_email = request.form['user_email']
    user_password = request.form['user_password']

    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE user_email = %s', (user_email,))
        user = cur.fetchone()
        if user:
            # Redirect to register page with error message if email already exists
            if check_password_hash(user[3], user_password):
                session['user_name'] = user[1];
                return redirect('/')
            return render_template('index.html', message={'error':'Incorrect password'})
        else:
            return render_template('index.html', message={'error':'Email dont exists'})
        
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    finally:
            cur.close()
            conn.close()    

@app.route('/logout',methods=['GET'])
def logout():
    session['user_name'] = None
    return redirect('/')

@app.route('/add_post',methods=['POST'])
def add_post():
    post_title = request.form['post_title']
    post_content = request.form['post_content']
    category_id = request.form['category_id']
    now = datetime.now()
    date_string = now.strftime('%Y-%m-%d')
    user_id = 0 # By default we are keeping user_id as 0, will fetch and overwrite user_id from DB

    # Check if user is logged in, if not go back to home page
    if not session.get('user_name'):
        return redirect('/')
    
    conn = get_db_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users WHERE user_name = %s', (session['user_name'],))
        user = cur.fetchone()
        if user:
                user_id = user[0]
                cur.execute('INSERT INTO posts(post_title,post_content,post_date,category_id,user_id) values(%s,%s,%s,%s,%s)',(post_title,post_content,date_string,category_id,user_id))
                conn.commit()
                return redirect('/')
        else:
            return render_template('index.html', message={'error':'Something went wrong'})
    except psycopg2.IntegrityError:
        conn.rollback()
        return render_template('index.html',message={'error':'something went wrong'})
    finally:
            conn.commit()
            cur.close()
            conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True,port=4000)
