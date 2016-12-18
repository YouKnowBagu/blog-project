from google.appengine.ext import db
import post
import user

class Unlike(db.Model):
    post = db.ReferenceProperty(post.Post, required=True)
    user = db.ReferenceProperty(user.User, required=True)

    @classmethod
    def by_post_id(cls, post_id):
        unlike = Unlike.all().filter('post =', post_id)
        return unlike.count()

    @classmethod
    def check_unlike(cls, post_id, user_id):
        unliked = Unlike.all().filter(
            'post =', post_id).filter(
            'user =', user_id)
        return unliked.count()