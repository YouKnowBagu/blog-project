from google.appengine.ext import db
import post
import user
import time

#### To store comments on individual posts, referencing Post and User.
class Comment(db.Model):
    post = db.ReferenceProperty(post.Post, required=True)
    user = db.ReferenceProperty(user.User, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    text = db.TextProperty(required=True)

    @classmethod
    def count_by_post_id(cls, post_id):
        comments = Comment.all().filter('post =', post_id)
        return comments.count()

    @classmethod
    def all_by_post_id(cls, post_id):
        comments = Comment.all().filter('post =', post_id).order('created')
        return comments