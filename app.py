from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://aj:password@localhost/civilchatterdb'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    content = db.Column(db.Text, unique=False)
    auther = db.Column(db.String(80), unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow )
    db.relationship('Reply', backref='post', lazy=True)

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

class PostSchema(ma.Schema):
    class Meta:
        fields = ('title', 'content', 'author' )

post_schema = PostSchema()
posts_schema = PostSchema(many=True)


# Endpoint to create a post
@app.route('/post', methods=['POST'])
def create_post():
    title = request.json['title']
    content = request.json['content']
    author = request.json['author']

    new_post = Post(title, content, author)

    db.session.add(new_post)
    db.session.commit()

    post = Post.query.get(new_post.id)

    return post_schema.jsonify(post)


# Endpoint to query all posts
@app.route('/posts', methods=['GET'])
def get_posts():
    all_posts = Post.query.all()
    result = posts_schema.dump(all_posts)
    return jsonify(result)


# Endpoint to query a single post
@app.route('/post/<id>', methods=['GET'])
def get_post(id):
    post = Post.query.get(id)
    return post_schema.jsonify(post)


# Endpoint to edit a post
@app.route('/post/<id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get(id)
    title = request.json['title']
    content = request.json['content']

    post.title = title
    post.content = content

    db.session.commit()
    return post_schema.jsonify(post)


# Endpoint to delete a post
@app.route('/post/<id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get(id)
    title = request.json['title']

    post.title = title

    db.session.delete(post)
    db.session.commit()

    return post_schema.jsonify(post)


class Reply(db.Model):
    __tablename__ = 'replies'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text())
    author = db.Column(db.String(80))
    replied_at = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, text, author):
        self.text = text
        self.author = author

class ReplySchema(ma.Schema):
    class Meta:
        field = ('text')

reply_schema = ReplySchema()
replies_schema = ReplySchema(many=True)




if __name__ == '__main__':
    app.run(debug=True)
