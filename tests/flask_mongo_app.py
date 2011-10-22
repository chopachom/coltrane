__author__ = 'qweqwe'

from flask import Flask
from extensions import db
import datetime

app = Flask(__name__)
db.init_app(app)

@app.route('/')
def hello():
    posts = db.connection.test_db.posts
    post = {"author": "Pasha Skitin",
         "text": "My first blog post!",
         "tags": ["mongodb", "python", "pymongo"],
         "date": datetime.datetime.utcnow()}
    posts.insert(post)
    all_posts = list(posts.find())
    return "<pre>"+str(all_posts)+"</pre>"


if __name__ == '__main__':
    app.run(debug=True)
      
#    posts = db.connection.test_db.posts
#    all_posts = list(posts.find())
#    print all_posts