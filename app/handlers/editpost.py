import app.helpers.decorators as decorators
import app.helpers.basehandler as basehandler
import permalink
import app.models.post
import time


class EditPost(basehandler.BlogHandler):
    @decorators.does_user_own_post
    def get(self, post_id, post):
#####If the user is logged in, take them to the editpost.html page.  otherwise
#####direct user to login page.
        self.render("editpost.html", post=post)

    @decorators.does_user_own_post
    def post(self, post_id, post):
#####Grab the post ID to be sure the proper post is updated/edited.

#####If the user clicks update, first check that the form is completely filled out.
#####If it is, update the database entry for the post.  Otherwise render error.
        if self.request.get("update"):

            subject = self.request.get("subject")
            content = self.request.get("content").replace('\n', '<br>')

            if subject and content:
                post.subject = subject
                post.content = content
                post.put()
                time.sleep(0.1)
                self.redirect('/blog/%s' % str(post_id))
            else:
                post_error = "All fields required."
                self.render(
                    "editpost.html",
                    post=post,
                    subject=subject,
                    content=content,
                    post_error=post_error)
#####Return user to the permalink if they hit cancel
        elif self.request.get("cancel"):
            self.redirect('/blog/%s' % str(post_id))
