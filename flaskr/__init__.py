import datetime
import os
from flask import Flask, json, request, jsonify
from flask.helpers import make_response
from .db import CommentsSchema, db, migrate, ma, UsersSchema, Users, Blogs, BlogsSchema, Podcasts, PodcastsSchema, Models, ModelsSchema, Comments
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from flask_cors import CORS, cross_origin


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'IaMwILLY@10780'
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:pass@localhost/thedatajournalist"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    cors = CORS(app)
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    user_schema = UsersSchema()
    users_schema = UsersSchema(many=True)
    blog_schema = BlogsSchema()
    blogs_schema = BlogsSchema(many=True)
    podcast_schema = PodcastsSchema()
    podcasts_schema = PodcastsSchema(many=True)
    model_schema = ModelsSchema()
    models_schema = ModelsSchema(many=True)
    comment_schema = CommentsSchema()
    comments_schema = CommentsSchema(many=True)

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']

            if not token:
                return jsonify({'message':"Token is missing"}), 401

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], "HS256")
                current_user = Users.query.filter_by(public_id=data['public_id']).first()

            except:
                return jsonify({'message', 'Token is invalid!'}), 401

            return f(current_user, *args, **kwargs)

        return decorated

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/api/users', methods=["POST"])
    @cross_origin()
    def addUser():
        username = request.json['username']
        first_name = request.json['first_name']
        second_name = request.json['second_name']
        last_name = request.json['last_name']
        dob = request.json['dob']
        email = request.json['email']
        password = request.json['password']
        #joined = request.json['joined']
        category = 2
        hashed_password = generate_password_hash(password, method='sha256')
        joined = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        public_id = str(uuid.uuid4())
        new_user = Users(public_id, username, first_name, second_name, last_name, dob, email, hashed_password, joined, category)
        db.session.add(new_user)
        db.session.commit()
        token = jwt.encode({'public_id':public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'],"HS256")
        return jsonify({'message':'User added successfully', 'token':token})

    @app.route('/api/users', methods=["GET"])
    @token_required
    @cross_origin()
    def getUsers(current_user):
        if current_user.category != 1:
            return jsonify({'message':'Permissions Denied'})
            
        all_users = Users.query.all()
        result = users_schema.dump(all_users)
        return jsonify(result)

    @app.route('/api/users/<username>', methods=["GET"])
    @token_required
    def getUser(current_user, username):
        user = Users.query.filter_by(username=username).first()
        result = user_schema.dump(user)
        return jsonify(result)
        

    @app.route('/api/users/<username>', methods=["PUT"])
    @token_required
    def update_user(current_user, username):
        user = Users.query.filter_by(username=username).first()
        if not user:
            return jsonify({'message':'User not found'})
        user.username = request.json['username']
        user.first_name = request.json['first_name']
        user.second_name = request.json['second_name']
        user.last_name = request.json['last_name']
        user.dob = request.json['dob']
        user.email = request.json['email']
        user.password = request.json['password']
        user.joined = request.json['joined']
        user.category = request.json['category']
        db.session.commit()
        return jsonify({'mesage':'User Profile Updated.'})

    @app.route('/api/users/<username>', methods=["DELETE"])
    @token_required
    def delete_user(current_user, username):
        user = Users.query.filter_by(username=username).first()
        if not user:
            return jsonify({'message':'User does not exist'})
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message':'User deleted succesfully'})

    @app.route('/api/blogs', methods=["POST"])
    @token_required
    def add_blog(current_user):
        blog_title = request.json['blog_title']
        blog_body = request.json['blog_body']
        posted = request.json['posted']
        dropped = request.json['dropped']
        likes = request.json['likes']
        hidden = request.json['hidden']
        authored_by = request.json['authored_by']
        new_blog = Blogs(str(uuid.uuid4()), blog_title, blog_body, posted, dropped, likes, hidden, authored_by)
        db.session.add(new_blog)
        db.session.commit()
        return jsonify({'message':'Blog added successfully'})

    @app.route('/api/blogs', methods=["GET"])
    def retrieve_blogs():
        all_blogs = Blogs.query.all()
        result = blogs_schema.dump(all_blogs)
        return jsonify(result)

    @app.route('/api/blogs/<public_id>', methods=["GET"])
    def retrieve_blog(current_user, public_id):
        blog = Blogs.query.filter_by(public_id=public_id).first()
        result = blog_schema.dump(blog)
        return jsonify(result)
        

    @app.route('/api/blog/<public_id>', methods=["PUT"])
    @token_required
    def update_blog(current_user, public_id):
        blog = Blogs.query.filter_by(public_id=public_id).first()
        if not blog:
            return jsonify({'message':"Blog doesn't exist."})
        blog.blog_title = request.json['blog_title']
        blog.blog_body = request.json['blog_body']
        blog.posted = request.json['posted']
        blog.dropped = request.json['dropped']
        blog.likes = request.json['likes']
        blog.hidden = request.json['hidden']
        blog.authored_by = request.json['authored_by']
        db.session.commit()

        return jsonify({'message':'Blog modified successfully'})

        


    @app.route('/api/blogs/<public_id>', methods=["DELETE"])
    @token_required
    def drop_blog(current_user, public_id):
        blog = Blogs.query.filter_by(public_id=public_id).first()
        if not blog:
            return jsonify({'message':'Blog does not exist'})
        db.session.delete(blog)
        db.session.commit()
        return jsonify({'message':'Blog deleted succesfully'})


    @app.route('/api/podcasts', methods=["POST"])
    @token_required
    def add_podcast(current_user):
        podcast_title = request.json['podcast_title']
        podcast_thumbnail = request.json['podcast_thumbnail']
        podcast_url = request.json['podcast_url']
        listens = request.json['listens']
        posted = request.json['posted']
        dropped = request.json['dropped']
        hidden = request.json['hidden']
        posted_by = request.json['posted_by']
        new_podcast = Podcasts(str(uuid.uuid4()), podcast_title, podcast_thumbnail, podcast_url, listens, posted, dropped, hidden, posted_by)
        db.session.add(new_podcast)
        db.session.commit()
        return jsonify({'message':'Podcast added successfully.'})

    @app.route('/api/podcasts', methods=["GET"])
    def retrive_podcasts():
        all_podcasts = Podcasts.query.all()
        result = podcasts_schema.dump(all_podcasts)
        return jsonify(result)

    @app.route('/api/podcasts/<public_id>', methods=["GET"])
    def retrive_podcast(public_id):
        podcast = Podcasts.query.filter_by(public_id=public_id).first()
        result = podcast_schema.dump(podcast)
        return jsonify(result)

    @app.route('/api/podcasts/<public_id>', methods=["PUT"])
    @token_required
    def update_podcast(current_user, public_id):
        podcast = Podcasts.query.filter_by(public_id=public_id).first()
        if not podcast:
            return jsonify({'message':'Podcast does not exist.'})
        podcast.podcast_title = request.json['podcast_title']
        podcast.podcast_thumbnail = request.json['podcast_thumbnail']
        podcast.podcast_url = request.json['podcast_url']
        podcast.listens = request.json['listens']
        podcast.posted = request.json['posted']
        podcast.dropped = request.json['dropped']
        podcast.hidden = request.json['hidden']
        podcast.posted_by = request.json['posted_by']
        return jsonify({'message':'Podcast information updated successsfully'})


    @app.route('/api/podcasts/<public_id>', methods=["DELETE"])
    @token_required
    def drop_podcast(current_user, public_id):
        podcast = Podcasts.query.filter_by(public_id=public_id).first()
        if not podcast:
            return jsonify({'message':'Podcast does not exist'})
        db.session.delete(podcast)
        db.session.commit()
        return jsonify({'message':'Podcast deleted succesfully'})

    @app.route('/api/models', methods=["POST"])
    @token_required
    def add_model(current_user):
        model_title = request.json['model_title']
        model_description = request.json['model_description']
        posted = request.json['posted']
        dropped = request.json['dropped']
        hidden = request.json['hidden']
        modelled_by = request.json['modelled_by']
        new_model = Models(str(uuid.uuid4()), model_title, model_description, posted, dropped, hidden, modelled_by)
        db.session.add(new_model)
        db.session.commit()
        return jsonify({'message':'Model added successfully'})

    @app.route('/api/models', methods=["GET"])
    def retrieve_models():
        all_models = Models.query.all()
        result = models_schema.dump(all_models)
        return jsonify(result)

    @app.route('/api/models/<public_id>', methods=["GET"])
    def retrieve_model(current_user, public_id):
        model = Models.query.filter_by(public_id=public_id).first()
        result = model_schema.dump(model)
        return jsonify(result)

    @app.route('/api/models/<public_id>', methods=["PUT"])
    @token_required
    def update_model(current_user, public_id):
        model = Models.query.filter_by(public_id=public_id).first()
        if not model:
            return jsonify({'message':'The model does not exist.'})
        model.model_title = request.json['model_title']
        model.model_description = request.json['model_description']
        model.posted = request.json['posted']
        model.dropped = request.json['dropped']
        model.hidden = request.json['hidden']
        model.modelled_by = request.json['modelled_by']
        db.session.commit()
        return jsonify({'message':'Model indormation successfully updated'})

    @app.route('/api/models/<public_id>', methods=["DELETE"])
    @token_required
    def drop_model(current_user, public_id):
        model = Models.query.filter_by(public_id=public_id).first()
        if not model:
            return jsonify({'message':'Model does not exist'})
        db.session.delete(model)
        db.session.commit()
        return jsonify({'message':'Model deleted succesfully'})

    @app.route('/api/comments/', methods=["POST"])
    @token_required
    def add_comment(current_user):
        comment = request.json['comment']
        posted = request.json['posted']
        comment_modified = request.json['modified']
        commented_by = request.json['commented_by']
        commented_on_blog = request.json['commented_on_blog']
        commented_on_podcast = request.json['commented_on_podcast']
        commented_on_model = request.json['commented_on_model']
        new_comment = Comments(str(uuid.uuid4()), comment, posted, comment_modified, commented_by, commented_on_blog, commented_on_podcast, commented_on_model)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'message':'Comment added successfully.'})

    @app.route('/api/comments', methods=["GET"])
    def retrieve_comments():
        all_comments = Comments.query.all()
        result = comments_schema.dump(all_comments)
        return jsonify(result)

    @app.route('/api/comments/<public_id>', methods=["GET"])
    @token_required
    def retrieve_comment(current_user, public_id):
        comment = Comments.query.filter_by(public_id=public_id)
        result = comment_schema.dump(comment)
        return jsonify(result)

    @app.route('/api/comments/<public_id>', methods=["PUT"])
    @token_required
    def update_coment(current_user, public_id):
        comment = Comments.query.filter_by(public_id=public_id).first()
        if not comment:
            return jsonify({'message':'Comment does not exist.'})
        comment.comment = request.json['comment']
        comment.posted = request.json['posted']
        comment.comment_modified = request.json['modified']
        comment.commented_by = request.json['commented_by']
        comment.commented_on_blog = request.json['commented_on_blog']
        comment.commented_on_podcast = request.json['commented_on_podcast']
        comment.commented_on_model = request.json['commented_on_model']
        db.session.commit()
        return jsonify({'message':'Comment updated successfully'})

    @app.route('/api/comments/<public_id>', methods=["DELETE"])
    @token_required
    def drop_comment(current_user, public_id):
        comment = Comments.query.filter_by(public_id=public_id).first()
        if not comment:
            return jsonify({'message':'Comment does not exist'})
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message':'Comment deleted succesfully'})

    @app.route('/api/login', methods=["POST"])
    @cross_origin()
    def login():
        auth_username = request.json['username']
        auth_password = request.json['password']
        if not auth_username or not auth_password:
            return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required"'})
        user = Users.query.filter_by(username=auth_username).first()
        if not user:
            return jsonify({'message':'Invalid username'})

        if check_password_hash(user.password, auth_password):
            token = jwt.encode({'public_id':user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'],"HS256")
            #d_token = jwt.decode(token, app.config['SECRET_KEY'])
            return jsonify({'token':token})

        return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Wrong Credentials provided!"'})

    return app