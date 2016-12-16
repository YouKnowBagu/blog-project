from google.appengine.ext import db
import post
import user
##### Database model to store likes, referencing the post and user.
class Like(db.Model):
    post = db.ReferenceProperty(post.Post, required=True)
    user = db.ReferenceProperty(user.User, required=True)

    @classmethod
    def by_post_id(cls, post_id):
        like = Like.all().filter('post =', post_id)
        return like.count()

    @classmethod
    def check_like(cls, post_id, user_id):
        liked = Like.all().filter(
            'post =', post_id).filter(
            'user =', user_id)
        return liked.count()