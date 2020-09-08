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

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    content = db.Column(db.Text, unique=False)
    auther = db.Column(db.String(80), unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.now, )

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

class BlogSchema(ma.Schema):
    class Meta:
        fields = ('title', 'content', 'author' )

blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


# Endpoint to create a blog
@app.route('/blog', methods=['POST'])
def create_blog():
    title = request.json['title']
    content = request.json['content']
    author = request.json['author']

    new_blog = Blog(title, content, author)

    db.session.add(new_blog)
    db.session.commit()

    blog = Blog.query.get(new_blog.id)

    return blog_schema.jsonify(blog)


# Endpoint to query all blogs
@app.route('/blogs', methods=['GET'])
def get_blogs():
    all_blogs = Blog.query.all()
    result = blogs_schema.dump(all_blogs)
    return jsonify(result)


# Endpoint to query a single blog
@app.route('/blog/<id>', methods=['GET'])
def get_blog(id):
    blog = Blog.query.get(id)
    return blog_schema.jsonify(blog)


# Endpoint to edit a blog
@app.route('/blog/<id>', methods=['PUT'])
def update_blog(id):
    blog = Blog.query.get(id)
    title = request.json['title']
    content = request.json['content']

    blog.title = title
    blog.content = content

    db.session.commit()
    return blog_schema.jsonify(blog)


# Endpoint to delete a blog
@app.route('/blog/<id>', methods=['DELETE'])
def delete_blog(id):
    blog = Blog.query.get(id)
    title = request.json['title']

    blog.title = title

    db.session.delete(blog)
    db.session.commit()

    return blog_schema.jsonify(blog)


# class Comment(db.Model):
#     __tablename__ = 'comments'


if __name__ == '__main__':
    app.run(debug=True)
