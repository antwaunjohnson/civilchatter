from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

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

    def __init__(self, title, content):
        self.title = title
        self.content = content

class BlogSchema(ma.Schema):
    class Meta:
        fields = ('title', 'content')

blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


# Endpoint to create a blog
@app.route('/blog', methods=['POST'])
def create_blog():
    title = request.json['title']
    content = request.json['content']

    new_blog = Blog(title, content)

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





if __name__ == '__main__':
    app.run(debug=True)
