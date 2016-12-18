from app.helpers import  basehandler
from google.appengine.ext import db
from permalink import PostPage
from functools import wraps
import app.models.post as dbpost
import app.helpers.basehandler as basehandler
import app.helpers.decorators as decorators
import app.models.comment as dbcomment
import time

is_user = decorators.is_user
does_post_exist = decorators.does_post_exist
does_comment_exist = decorators.does_comment_exist
does_user_own_comment = decorators.does_user_own_comment
Comment = dbcomment.Comment
Post = dbpost.Post

class DeleteComment(basehandler.BlogHandler):
    @does_post_exist
    @does_comment_exist
    @is_user
    @does_user_own_comment
    def get(self, post_id, comment_id, post, comment, user):
        if comment:
            db.delete(comment)
            self.redirect('/blog/%s' % str(post_id))
            time.sleep(0.1)
        else:
            self.redirect('/blog')

    @does_post_exist
    @does_comment_exist
    @is_user
    @does_user_own_comment
    def post(self, post_id, comment_id, post, comment, user):
            db.delete(comment)
            self.redirect('/blog')