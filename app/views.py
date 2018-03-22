# -*- coding: utf-8 -*-
from .decorators import async
from .forms import EditForm
from .forms import LoginForm
from .forms import PostingForm
from .forms import RegisterForm
from .forms import SearchForm
from .models import User
from .models import Post
from .oauth import OAuthSignIn
from app import app
from app import db
from app import lm
from app import oid
from config import MAX_SEARCH_RESULTS
from config import USERS_PER_PAGE
from datetime import datetime
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.security import generate_password_hash, check_password_hash

def handlePosting(form):
	if form.validate_on_submit():
		post=Post(body=form.text.data,
			author=current_user,
			timestamp=datetime.utcnow()
		)
		db.session.add(post)
		db.session.commit()
		flash("Post sent to your followers!")
		return True

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen=datetime.utcnow()
		db.session.add(current_user)
		db.session.commit()

@app.route('/')
@app.route('/index', methods=["GET","POST"])
@login_required
def index():
	user=current_user
	form=PostingForm()
	if handlePosting(form):
		print 'post sent!'
		return redirect(url_for('index'))
	posts=current_user.followed_posts().all()
	return render_template('index.html',title='Home',posts=posts,form=form)

@app.route('/user/<nickname>',methods=['GET','POST'])
@login_required
def user(nickname):
	user=User.query.filter_by(nickname=nickname).first()
	form=PostingForm()
	if handlePosting(form):
		return redirect(url_for('user',nickname=nickname))
	if user==None:
		flash('User %s not found.' % nickname)
		return redirect(url_for('index'))
	posts=[
		{'author':user,'body':'test01'},
		{'author':user,'body':'test02'}
	]
	posts=Post.query.filter_by(author=user).order_by(Post.timestamp.desc())
	return render_template('user.html',user=user,posts=posts,title=user.nickname+" : User Profile",form=form)

@app.route('/remove_post/<post_id>')
@login_required
def remove_post(post_id):
	post=Post.query.filter_by(id=post_id).first()
	if post.author==current_user:
		db.session.delete(post)
		db.session.commit()
		flash('Post removed')
	return redirect(url_for('index'))

@app.route('/edit',methods=['GET','POST'])
@login_required
def edit():
	form=EditForm()
	if form.validate_on_submit():
		current_user.nickname=form.nickname.data
		current_user.about_me=form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash("Your changes have been saved!")
		return redirect(url_for('edit'))
	else:
		form.nickname.data=current_user.nickname
		form.about_me.data=current_user.about_me
	return render_template('edit.html',title='Edit',form=form)

@app.route('/register',methods=['GET','POST'])
def register():
	form=RegisterForm()
	if form.validate_on_submit():
		new_user=User(
			nickname=form.nickname.data,
			email=form.email.data,
			password=generate_password_hash(form.password.data),
			social_id='nosocialid$'+form.nickname.data+'$'+form.email.data
		)
		db.session.add(new_user)
		db.session.commit()
		db.session.add(new_user.follow(new_user))
		db.session.commit()
		flash("User registred! Please log in to continue to your new account!")
		return redirect(url_for('login'))
	return render_template('register.html',title='Register',form=form)

@app.route('/remove',methods=['GET','POST'])
@login_required
def remove():
	form=LoginForm()
	if form.validate_on_submit():
		deleting_user=User.query.filter_by(nickname=form.nickname.data).first()
		if current_user==deleting_user and check_password_hash(current_user.password,form.password.data):
			logout_user()
			db.session.delete(deleting_user)
			db.session.commit()
			flash('User removed... We appologize for everything :(')
			return redirect(url_for('login'))
		else:
			flash("Wrong credentials!")
	return render_template('remove_user.html',title='Remove %s account'%current_user.nickname,form=form)

@app.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()
	if current_user is not None and current_user.is_authenticated:
		return redirect(url_for('index'))
	if form.validate_on_submit():
		entered_user=User.query.filter_by(
			nickname=form.nickname.data).first()
		if entered_user is None:
			flash('Password or Nickname is invalid')
			return redirect(url_for('login'))
		elif entered_user.deny_login is not None and (datetime.utcnow()-entered_user.deny_login).total_seconds()<(60*5):
			flash('Temporaly blocked, wait %d minutes to try again.'%(5-(int((datetime.utcnow()-entered_user.deny_login).total_seconds() )//60)))
			return redirect(url_for('login'))
		elif check_password_hash(entered_user.password,form.password.data):
			entered_user.deny_login=None
			entered_user.failed_to_login=0
			entered_user.online=True
			db.session.add(entered_user)
			db.session.commit()
			login_user(entered_user,True)
			return redirect(url_for('index'))
		else:
			try:
				entered_user.failed_to_login+=1
			except TypeError:
				entered_user.failed_to_login=1
			if entered_user.failed_to_login>=5:
				entered_user.deny_login=datetime.utcnow()
				entered_user.failed_to_login=0
				flash("This account is now temporaly blocked due to many login attempts.")
			db.session.add(entered_user)
			db.session.commit()
			flash('Password is invalid(%s)'%entered_user.failed_to_login)
			return redirect(url_for('login'))
	return render_template('login.html',title='Log In', form=form)


def get_users(users,title,base_route,nickname=None):
	return render_template('get_users.html',title=title,users=users,route=base_route,nickname=nickname)

@app.route('/allusers')
@app.route('/allusers/<int:page>')
@app.route('/allusers/<nickname>/<int:page>')
@login_required
def all_users(page=1,nickname=None):
	return get_users(User.query.paginate(page,USERS_PER_PAGE,False),"All Users","all_users")

@app.route('/following/<nickname>')
@app.route('/following/<nickname>/<int:page>')
@login_required
def following(nickname,page=1):
	return get_users(User.query.filter_by(nickname=nickname).first().followed.filter(User.nickname!=nickname).paginate(page,USERS_PER_PAGE,False),"Users followed by %s:"%nickname,"following",nickname)

@app.route('/followers/<nickname>')
@app.route('/followers/<nickname>/<int:page>')
@login_required
def followers(nickname,page=1):
        return get_users(User.query.filter_by(nickname=nickname).first().followers.filter(User.nickname!=nickname).paginate(page,USERS_PER_PAGE,False),"Users following %s:"%nickname,"followers",nickname)

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/logout')
def logout():
	current_user.online=False
	db.session.add(current_user)
	db.session.commit()
	logout_user()
	return redirect(url_for('login'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('login'))
	oauth=OAuthSignIn.get_provider(provider)
	print 'trying to get authorization'
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('login'))
	oauth=OAuthSignIn.get_provider(provider)
	social_id,username,email=oauth.callback()
	if social_id is None:
		print 'failed'
		flush('Authentication failed.')
		return redirect(url_for('login'))
	print social_id
	user=User.query.filter_by(social_id=social_id).first()
	if not user:
		user=User(social_id=social_id,nickname=username,email=email)
		db.session.add(user)
		db.session.commit()
		db.session.add(user.follow(user))
		db.session.commit()
	if "twitter" in social_id:
		user.twitter_nickname=username
	user.online=True
	db.session.add(user)
	db.session.commit()
	login_user(user,True)
	print 'loged!'
	return redirect(url_for('index'))

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	user=User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash('User %s not found'%nickname)
		return redirect(url_for('index'))
	if user == current_user:
		flash("Are you nuts?! You can't follow yourself, %s!"%nickname)
		return redirect(url_for('index'))
	follow_object=current_user.follow(user)
	if follow_object is None:
		flash("Sorry, but you can't follow %s."%nickname)
		return redirect(url_for('index'))
	db.session.add(follow_object)
	db.session.commit()
	flash('You are now following %s!'%nickname)
	return  redirect(url_for('user',nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
	user=User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash('User %s not found'%nickname)
		return redirect(url_for('index'))
	if user == current_user:
		flash("Why are you trying this? You can't unfollow yourself, %s!"%nickname)
		return redirect(url_for('index'))
	unfollow_object=current_user.unfollow(user)
	if unfollow_object is None:
		flash("Sorry, but you can't unfollow %s."%nickname)
		return redirect(url_for('index'))
	db.session.add(unfollow_object)
	db.session.commit()
	flash('You have stopped following %s.'%nickname)
	return  redirect(url_for('user',nickname=nickname))

@app.route('/search',methods=["GET","POST"])
#@app.route('/search/<query>',methods=["GET","POST"])
def search():
	form=SearchForm()
	query=None
	results=None
	if form.validate_on_submit():
		query=form.search.data
		results=Post.query.whoosh_search(query,MAX_SEARCH_RESULTS).all()
	return render_template('search.html',title="Search",
			form=form,
			query=query,results=results)
