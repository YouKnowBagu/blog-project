from app.helpers import  basehandler
from google.appengine.ext import db
from permalink import PostPage
from functools import wraps
import app.models.post as dbpost
import app.helpers.basehandler as basehandler
import app.helpers.decorators as decorators
import app.models.comment as dbcomment
import time
Comment = dbcomment.Comment
Post = dbpost.Post

class DeleteComment(basehandler.BlogHandler):
    def get(self, post_id, comment_id):
        comm = Comment.get_by_id(int(comment_id))
        if comm:
            db.delete(comm)
            self.redirect('/blog/%s' % str(post_id))
            time.sleep(0.1)
        else:
            self.redirect('/blog')
    def post(self, post_id, comment_id):
        if comment_id:
            comm=Comment.get_by_id(int(comment_id))
            db.delete(comm)
            self.redirect('/blog')