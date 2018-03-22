from app import db
from app import app
from hashlib import md5
from sys import version_info

if version_info>=(3,0):
	enable_search=False
else:
	enable_search=True
	from flask_whooshalchemy import whoosh_index

followers=db.Table('followers',
        db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
        db.Column('followed_id',db.Integer,db.ForeignKey('user.id')),
)

class User(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	social_id=db.Column(db.String(64),nullable=False,unique=True)
	nickname=db.Column(db.String(64),nullable=False,unique=True)
	email=db.Column(db.String(120),nullable=True )
	posts=db.relationship('Post',backref='author',lazy='dynamic')
	about_me=db.Column(db.String(140))
	last_seen=db.Column(db.DateTime)
	followed=db.relationship('User',
                secondary=followers,
                primaryjoin=(followers.c.follower_id==id),
                secondaryjoin=(followers.c.followed_id==id),
                backref=db.backref('followers',lazy='dynamic'),
                lazy='dynamic')
	password=db.Column(db.String(64))
	failed_to_login=db.Column(db.Integer)
	deny_login=db.Column(db.DateTime)
	online=db.Column(db.Boolean)
	twitter_nickname=db.Column(db.String(64),nullable=True)

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)

	def __repr__(self):
		return '<User %r>' % (self.nickname)

	def avatar(self,size,twitter_size):
		if "twitter" in self.social_id:
			return 'https://twitter.com/%s/profile_image?size=%s'%(self.twitter_nickname,twitter_size)
		if "facebook" in self.social_id:
			return 'http://graph.facebook.com/%s/picture?width=%d&height=%d'%(self.social_id.split('$')[1],size,size)
		try:
			return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)
		except:
			return 'http://en.gravatar.com/avatar/?d=mm&s='+str(size)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self,user):
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self,user):
		return self.followed.filter(followers.c.followed_id==user.id).count()>0

	def followed_posts(self):
		return Post.query.join(
			followers,
			(followers.c.followed_id==Post.user_id)
		).filter(
			followers.c.follower_id == self.id
		).order_by(
			Post.timestamp.desc()
		)

class Post(db.Model):
	__searchable__=['body']

	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.String(140))
	timestamp=db.Column(db.DateTime)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
	def __repr__(self):
		return '<Post %r>' % (self.body)
	def copy(self):
		return Post(id=self.id,body=self.body,timestamp=self.timestamp,user_id=self.user_id)

if enable_search:
	whoosh_index(app,Post)
