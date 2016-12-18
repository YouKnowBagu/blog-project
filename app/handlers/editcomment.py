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
    @does_user_own_comment
    @does_comment_exist
    @does_post_exist
    @is_user
    def get(self, user, post_id, post, comment_id, comment):
#####Find the comment ID to be updated.
            self.render("editcomment.html", comment=comment)

    @does_user_own_comment
    @does_comment_exist
    @does_post_exist
    @is_user
    def post(self, user, post_id, post, comment_id, comment):
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