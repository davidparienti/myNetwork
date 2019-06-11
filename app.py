import os
from flask import render_template,request, redirect, url_for,flash,session , send_from_directory , json , Flask
from database import app, db, User, Post, Jaime, Comment, Followerfollowing
from utils import validate_password, validate_username , validate_email, redirect_is_logged , allowed_file , redirect_is_not_logged
import datetime
from sqlalchemy import desc
from werkzeug.utils import secure_filename



app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'static/avatar/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/index')
def index():

  if session:
    page_name = "Home"
    user = User.query.filter_by(username=session['username']).first()

    posts = db.session.execute('SELECT post.* , user.full_name , user.username ,  user.profil_media, count(DISTINCT jaime.id) as nb_like , count(DISTINCT jaime2.id) as liked , count(DISTINCT comment.id) as nb_comment , strftime(\'%d/%m/%Y %H:%M\', datetime(post.created)) as created FROM post LEFT JOIN comment ON comment.post_id = post.id  LEFT JOIN jaime ON jaime.post_id = post.id LEFT JOIN jaime as jaime2 ON jaime2.post_id = post.id AND jaime2.user_id = :myid JOIN user ON user.id = post.user_id LEFT JOIN Followerfollowing ON Followerfollowing.user_id = :myid WHERE post.user_id = :myid  OR post.user_id = Followerfollowing.user_id_2 GROUP BY post.id ORDER BY post.created DESC', {'myid': session['id']}) 

    user = db.session.execute('SELECT user.id, user.full_name , user.username , user.email , user.profil_media , count(DISTINCT `following`.id) as nb_following , count(DISTINCT Followerfollowing.id) as followed , count(DISTINCT follower.id) as nb_follower FROM user LEFT JOIN Followerfollowing as `following` ON following.user_id = user.id LEFT JOIN Followerfollowing as follower ON follower.user_id_2 = user.id  LEFT JOIN Followerfollowing ON Followerfollowing.user_id = :myid AND Followerfollowing.user_id_2 = user.id WHERE user.username = :username', {'myid': session['id'] ,  'username': session['username']}).first()

    suggestions = db.session.execute('SELECT user.* FROM user LEFT JOIN Followerfollowing ON Followerfollowing.user_id= :myid AND Followerfollowing.user_id_2 = user.id WHERE Followerfollowing.id IS NULL AND user.id <> :myid GROUP BY user.id LIMIT 5 ', {'myid': session['id'] ,'uid': user.id})

    return render_template('index.html',session=session,page_name=page_name,posts=posts,datetime=datetime,suggestions=suggestions,user=user)
  else:
    page_name = "Login"
    return render_template('login.html',page_name=page_name)

@app.route('/sign_up',methods = ['GET', 'POST'])
def sign_up():
    if redirect_is_logged(session) != True:
        return redirect_is_logged(session)
    page_name = "login - sign up"
    valid = True
    error_array = {}
    if request.method == 'POST':

        fullname = request.form.get('fullname', None)
        username = request.form.get('username', None)
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        repeat_password = request.form.get('repeat_password', None)

        if validate_password(password) == False :
            error_array['password'] = 'password is not valid'
            valid = False

        if password != repeat_password:
            error_array['password_repeat'] = 'password does\'nt match'
            valid = False

        if len(fullname) < 2:
            error_array['fullname'] = 'fullname too short'
            valid = False

        if validate_username(username) == False:
            error_array['username'] = 'username is not valid'
            valid = False

        if User.query.filter_by(username=username).first() is not None:
            error_array['username'] = 'username is already taken'
            valid = False

        if validate_email(email) == False:
            error_array['email'] = 'email is not valid'
            valid = False

        if User.query.filter_by(email=email).first() is not None:
            error_array['email'] = 'email is already taken'
            valid = False

        if valid == True :
            user = User(username=username,full_name=fullname, email = email, password=password)
            db.session.add(user)
            db.session.commit()

            if user == False:
                error_array['system'] = 'error insert db'
            else:
                session['id'] = user.id
                session['username'] = username
                session['full_name'] = fullname
                session['email'] = email
                # return render_template('index.html', page_name='Home', session=session)
                return redirect(url_for('index'))


    return render_template('login.html', page_name=page_name, error_array=error_array)
    


@app.route('/login',methods = ['GET', 'POST'])
def login():
    if redirect_is_logged(session) != True:
        return redirect_is_logged(session)

    page_name = "login - sign up"
    error_array = {}

    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        get_user = User.query.filter_by(username=username,password=password).first()
        if get_user is None :
            error_array['login'] = "error connection"
        else:
            session['username'] = get_user.username
            session['full_name'] = get_user.full_name
            session['id'] = get_user.id
            session['profil_media'] = get_user.profil_media
            # return render_template('index.html', page_name='Home', session=session)
            return redirect(url_for('index'))


    return render_template('login.html', page_name=page_name, error_array=error_array)



@app.route('/logout')
def logout():
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Login"
    if session :
        session.clear()

    # return render_template('login.html', page_name=page_name, session=session)
    return redirect(url_for('login'))

@app.route('/postmessage',methods = ['GET', 'POST'])
def postmessage():
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    new_post = {}

    if 'username' in session:
        if request.method == 'POST':
            message = request.form.get('message', None)
            title = request.form.get('title', None)
            redirection = request.form.get('redirection', None)
            if title:
               
                post = Post(title=title,message=message,user_id=session['id'],created = datetime.datetime.now())
                db.session.add(post)
                db.session.commit()

            if redirection is not None:
                 user = db.session.execute('SELECT user.* FROM user WHERE user.username = :username', { 'username': redirection}).first()
                 print(redirection)
                 if user is not None:

                    return redirect(url_for('profile',username=user.username))
                # new_post['title'] = title
                # new_post['message'] = message
        
                # return render_template('index.html', page_name="Home", new_post=new_post , session=session)
    return redirect(url_for('index'))


@app.route('/post/<int:post_id>',methods = ['GET','POST'])
def getpost(post_id):
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    post_exist = Post.query.filter_by(id=post_id).first() 
    if post_exist is not None:
        page_name = post_exist.title
        if request.method == 'POST':
            message = request.form.get('message', None)
            if message:
                comment = Comment(message=message,user_id=session['id'],post_id=post_id, created = datetime.datetime.now())
                db.session.add(comment)
                db.session.commit()

        get_post = db.session.execute('SELECT post.* , user.full_name ,  user.profil_media , user.username , count(DISTINCT jaime.id) as nb_like , count(DISTINCT jaime2.id) as liked, count(DISTINCT comment.id) as nb_comment , strftime(\'%d/%m/%Y %H:%M\', datetime(post.created)) as created  FROM post LEFT JOIN comment ON comment.post_id = post.id LEFT JOIN jaime ON jaime.post_id = post.id LEFT JOIN jaime as jaime2 ON jaime2.post_id = post.id AND jaime2.user_id = :myid JOIN user ON user.id = post.user_id LEFT JOIN Followerfollowing ON Followerfollowing.user_id = :myid  LEFT JOIN Followerfollowing as Followerfollowing_2 ON Followerfollowing_2.user_id_2 = :myid WHERE post.id = :post_id', {'myid': session['id'] , 'post_id': post_id}).first()
        get_comments = db.session.execute('SELECT comment.* , user.profil_media , user.full_name , user.username , strftime(\'%d/%m/%Y %H:%M\', datetime(comment.created)) as created  FROM comment JOIN user ON user.id = comment.user_id  WHERE comment.post_id = :post_id ORDER BY created DESC', {'post_id': post_id})
        return render_template('post.html', page_name=page_name,Post=get_post,Comments=get_comments)
    else:
        return redirect(url_for('index'))

@app.route('/like/<int:post_id>',methods = ['GET','POST'])
def like(post_id):
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    get_post = Post.query.filter_by(id=post_id).first()
    
    if get_post is None:
        return redirect(url_for('index'))
    
    get_jaime = Jaime.query.filter_by(post_id=post_id, user_id=session['id']).first()
 
    if get_jaime is None:
        insertJ = Jaime(post_id=post_id, user_id=session['id'])
        db.session.add(insertJ)
        db.session.commit()
    else:
        db.session.delete(get_jaime)
        db.session.commit()
    
    count_like = db.session.execute('SELECT count(`Jaime`.id) as nb_like FROM `Jaime` WHERE `Jaime`.post_id = :postid  ', {'postid': post_id }).first() 
   
    return_json = {}
    return_json['nb_like'] = count_like.nb_like
    response = app.response_class(
        response=json.dumps(return_json),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/setting',methods = ['GET','POST'])
def setting():
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Setting"
    valid = True
    success_message_p = ''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            valid = False
        
        if valid:

            file = request.files['file']

            if file.filename == '':
                 valid = False
            if file and allowed_file(file.filename,ALLOWED_EXTENSIONS):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user = User.query.filter_by(id=session['id']).first()
                user.profil_media = filename
                db.session.commit()
                success_message_p = "Profile Updated"
                session['profil_media'] = filename

    return render_template('settings.html', page_name=page_name, session=session,success_message_p=success_message_p)



@app.route('/newpass',methods = ['GET','POST'])
def newpass():
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Setting"
    error_array = {}
    success_message = ''
    valid = True
    if request.method == 'POST':

            old_password=request.form.get('old_password', None)
            new_password=request.form.get('new_password', None)
            repeat_password=request.form.get('repeat_password', None)
            user = User.query.filter_by(id=session['id'], password=old_password).first()

            if user is None:
                error_array['old_password'] = "Wrong old password"
                valid = False

            if new_password != repeat_password:
                error_array['repeat_password'] = "Repeat password doesnt match"
                valid = False

            if validate_password(new_password) == False :
                error_array['password'] = 'password is not valid'
                valid = False

            if valid == True : 
                user.password = new_password
                db.session.commit()
                success_message = "Password Updated"



    return render_template('settings.html', page_name=page_name, session=session,error_array=error_array,success_message = success_message)
    

@app.route('/profile/<username>',methods = ['GET','POST'])
def profile(username):
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Profile"
    if username is None:
        return redirect(url_for('index'))
    user = db.session.execute('SELECT user.id, user.full_name , user.username , user.email , user.profil_media , count(DISTINCT `following`.id) as nb_following , count(DISTINCT Followerfollowing.id) as followed , count(DISTINCT follower.id) as nb_follower FROM user LEFT JOIN Followerfollowing as `following` ON following.user_id = user.id LEFT JOIN Followerfollowing as follower ON follower.user_id_2 = user.id  LEFT JOIN Followerfollowing ON Followerfollowing.user_id = :myid AND Followerfollowing.user_id_2 = user.id WHERE user.username = :username', {'myid': session['id'] ,  'username': username}).first()

    if user.username is None:
        return redirect(url_for('index'))


    posts = db.session.execute('SELECT post.* , user.full_name , user.username ,  user.profil_media, count(DISTINCT jaime.id) as nb_like , count(DISTINCT jaime2.id) as liked , count(DISTINCT comment.id) as nb_comment, strftime(\'%d/%m/%Y %H:%M\', datetime(post.created)) as created FROM post LEFT JOIN comment ON comment.post_id = post.id  LEFT JOIN jaime ON jaime.post_id = post.id LEFT JOIN jaime as jaime2 ON jaime2.post_id = post.id AND jaime2.user_id = :myid LEFT JOIN user ON user.id = post.user_id WHERE user.username = :username  OR LOWER(post.title) LIKE LOWER(:usernamea)  GROUP BY post.id ORDER BY post.created DESC', {'myid': session['id'] ,  'username': user.username , 'usernamea': "%@"  + username +"%"  })


    followings = db.session.execute('SELECT * FROM user JOIN Followerfollowing ON Followerfollowing.user_id = :uid AND Followerfollowing.user_id_2 = user.id GROUP BY user.id LIMIT 6 ', {'uid': user.id})

    return render_template('user-profile.html', page_name=page_name, session=session,user=user , posts=posts,followings=followings)

@app.route('/follow/<username>',methods = ['GET','POST'])
def follow(username):
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    user2 = User.query.filter_by(username=username).first()

    if user2 is None:
        return redirect(url_for('index'))

    if user2.id == session['id']:
        return redirect(url_for('index'))

    get_follow = Followerfollowing.query.filter_by(user_id=session['id'],user_id_2=user2.id).first()

    #unfollow
    if get_follow is not None:

        db.session.delete(get_follow)
        db.session.commit()
        db.session.close()
        return "unfollow"

    #follow
    else:
        follow = Followerfollowing(user_id=session['id'],user_id_2=user2.id)
        db.session.add(follow)
        db.session.commit()
        db.session.close()
        return "follow"

@app.route('/followings/<username>',methods = ['GET','POST'])
def getfollowing(username):
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Followings"
    user = db.session.execute('SELECT user.id, user.full_name , user.username , user.email , user.profil_media , count(DISTINCT `following`.id) as nb_following , count(DISTINCT Followerfollowing.id) as followed , count(DISTINCT follower.id) as nb_follower FROM user LEFT JOIN Followerfollowing as `following` ON following.user_id = user.id LEFT JOIN Followerfollowing as follower ON follower.user_id_2 = user.id  LEFT JOIN Followerfollowing ON Followerfollowing.user_id = :myid WHERE user.username = :username', {'myid': session['id'] ,  'username': username}).first()
    if user is None:
        return redirect(url_for('index'))



    followings = db.session.execute('SELECT user.* , count(DISTINCT followed.id) as followed FROM user JOIN Followerfollowing ON Followerfollowing.user_id = :uid AND Followerfollowing.user_id_2 = user.id LEFT JOIN Followerfollowing as followed ON followed.user_id = :myid AND followed.user_id_2 = user.id GROUP BY user.id ', {'myid': session['id'] ,'uid': user.id})

    return render_template('followings.html', page_name=page_name, session=session,user=user ,followings=followings)

@app.route('/followers/<username>',methods = ['GET','POST'])
def getfollowers(username):
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Followers"
    user = db.session.execute('SELECT user.id, user.full_name , user.username , user.email , user.profil_media , count(DISTINCT `following`.id) as nb_following , count(DISTINCT Followerfollowing.id) as followed , count(DISTINCT follower.id) as nb_follower FROM user LEFT JOIN Followerfollowing as `following` ON following.user_id = user.id LEFT JOIN Followerfollowing as follower ON follower.user_id_2 = user.id  LEFT JOIN Followerfollowing ON Followerfollowing.user_id = :myid WHERE user.username = :username', {'myid': session['id'] ,  'username': username}).first()
    if user is None:
        return redirect(url_for('index'))



    followers = db.session.execute('SELECT user.* , count(DISTINCT followed.id) as followed FROM user JOIN Followerfollowing ON Followerfollowing.user_id_2 = :uid AND Followerfollowing.user_id = user.id LEFT JOIN Followerfollowing as followed ON followed.user_id = :myid AND followed.user_id_2 = user.id GROUP BY user.id ', {'myid': session['id'] ,'uid': user.id})

    return render_template('followers.html', page_name=page_name, session=session,user=user ,followers=followers)

@app.route('/suggestions',methods = ['GET','POST'])
def getsuggestions():
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Suggestions"

    suggestions = db.session.execute('SELECT user.* FROM user LEFT JOIN Followerfollowing ON Followerfollowing.user_id= :myid AND Followerfollowing.user_id_2 = user.id WHERE Followerfollowing.id IS NULL AND user.id <> :myid GROUP BY user.id ', {'myid': session['id']})

    return render_template('suggestions.html', page_name=page_name, session=session , suggestions=suggestions)

@app.route('/search',methods = ['GET','POST'])
def getsearch():
    if redirect_is_not_logged(session) != True:
        return redirect_is_not_logged(session)
    page_name = "Search"
    if request.method == 'POST':
        query=request.form.get('query', None)
        if query is not None:
            users = db.session.execute('SELECT user.* , count(DISTINCT followed.id) as followed FROM user LEFT JOIN Followerfollowing as followed ON followed.user_id = :myid AND followed.user_id_2 = user.id WHERE LOWER(user.full_name) LIKE  LOWER(:query) OR LOWER(user.username) LIKE  LOWER(:query) OR LOWER(user.email) LIKE  LOWER(:query) GROUP BY user.id ', {'myid': session['id'] ,'query': '%'+query+'%'})
            return render_template('search.html', page_name=page_name, session=session,users=users,query=query)
    return redirect(url_for('index'))

      





