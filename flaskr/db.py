from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    second_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.Integer, nullable=False, default=2)
    #status
    blogs = db.relationship('Blogs',backref='users', lazy=True)
    podcasts = db.relationship('Podcasts',backref='users', lazy=True)
    models = db.relationship('Models',backref='users', lazy=True)
    comments = db.relationship('Comments',backref='users', lazy=True)

    def __repr__(self):
        return '<User %r>'%self.username

    def __init__(self, uid, username, fname, mname, lname, dob, email, password, joined, category):
        self.public_id = uid
        self.username = username
        self.first_name = fname
        self.second_name = mname
        self.last_name = lname
        self.dob = dob
        self.email = email
        self.password = password
        self.joined = joined
        self.category = category

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    blog_title = db.Column(db.String(255), nullable = False)
    blog_body = db.Column(db.String(10000), nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    dropped = db.Column(db.DateTime, nullable=True)
    likes = db.Column(db.Integer, nullable=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    authored_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comments', backref='blogs', lazy=True)

    def __repr__(self):
        return '<Blog %r>'%self.blog_title

    def __init__(self, uid, title, body, posted, dropped, likes, hidden, author):
        self.public_id = uid
        self.blog_title = title
        self.blog_body = body
        self.posted = posted
        self.dropped = dropped
        self.likes = likes
        self.hidden = hidden
        self.authored_by = author

class Podcasts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    podcast_title = db.Column(db.String(255), nullable=False)
    podcast_thumbnail = db.Column(db.String(255), nullable=False)
    podcast_url = db.Column(db.String(255), nullable=False)
    listens = db.Column(db.Integer, nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    dropped = db.Column(db.DateTime, nullable=True)
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.relationship('Comments', backref='podcasts', lazy=True)

    def __repr__(self):
        return '<Podcast %r>'%self.podcast_title

    def __init__(self, uid, title, thumnail_url, url, listens, posted, dropped, hidden, by):
        self.public_id = uid
        self.podcast_title = title
        self.podcast_thumbnail = thumnail_url
        self.podcast_url = url
        self.listens = listens
        self.posted = posted
        self.dropped = dropped
        self.hidden = hidden
        self.posted_by = by

class Models(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    model_title = db.Column(db.String(255), nullable=False)
    model_description = db.Column(db.String(1500), nullable=True)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    dropped = db.Column(db.DateTime, nullable=True)
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    modelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.relationship('Comments', backref='models', lazy=True)

    def __repr__(self):
        return '<Model %r>'%self.model_title

    def __init__(self, uid, title, desc, posted, dropped, hidden, by):
        self.public_id = uid
        self.model_title = title
        self.model_description = desc
        self.posted = posted
        self.dropped = dropped
        self.hidden = hidden
        self.modelled_by = by

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    comment = db.Column(db.String(1500), nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment_modified = db.Column(db.DateTime, nullable=True)
    commented_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    commented_on_blog = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=True)
    commented_on_podcast = db.Column(db.Integer, db.ForeignKey('podcasts.id'), nullable=True)
    commented_on_model = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=True)

    def __repr__(self):
        return '<Comment %r>'%self.id

    def __init__(self, uid, comment, posted, modified, by, blog, podcast, model):
        self.public_id = uid
        self.comment = comment
        self.posted = posted
        self.comment_modified = modified
        self.commented_by = by
        self.commented_on_blog = blog
        self.commented_on_podcast = podcast
        self.commented_on_model = model

class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users

class BlogsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blogs
        include_fk = True

class PodcastsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Podcasts
        include_fk = True

class ModelsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Models
        include_fk = True

class CommentsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comments
        include_fk = True
