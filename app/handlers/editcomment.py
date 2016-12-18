from app.helpers import  basehandler
from permalink import PostPage
from functools import wraps
from app.models import user, post, comment
import app.helpers.basehandler as basehandler
import app.helpers.decorators as decorators
import time

is_user = decorators.is_user
does_post_exist = decorators.does_post_exist
does_comment_exist = decorators.does_comment_exist
does_user_own_comment = decorators.does_user_own_comment


class EditComment(basehandler.BlogHandler):
    @does_post_exist
    @does_comment_exist
    @is_user
    @does_user_own_comment
    def get(self, post_id, comment_id, post, comment, user):
            self.render("editcomment.html", comment=comment)

    @does_post_exist
    @does_comment_exist
    @is_user
    @does_user_own_comment
    def post(self, post_id, comment_id, post, comment, user):
        if self.request.get("update"):
            content = self.request.get("comment")

            if content:
                comment.text = content
                comment.put()
                time.sleep(0.1)
                self.redirect('/blog/%s' % str(post_id))
            else:
                edit_error="All fields required."
                self.render(
                'editcomment.html',
                comment=comment,
                edit_error = edit_error)

        elif self.request.get("cancel"):
            self.redirect('/blog/%s' % str(post_id))