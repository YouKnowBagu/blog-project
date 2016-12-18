import app.helpers.basehandler as basehandler
import app.helpers.decorators as decorators
import app.models.user as dbuser
import app.models.post as dbpost
import app.keys.postkey as postkey

is_user = decorators.is_user
User = dbuser.User
postkey = postkey.post_key

class NewPost(basehandler.BlogHandler):
    @is_user
    def get(self, user):
            self.render('newpost.html')

    @is_user
    def post(self, user):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = dbpost.Post(
                parent=postkey(),
                subject=subject,
                content=content,
                user=user)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            post_error = "All fields required"
            self.render(
                "newpost.html",
                subject=subject,
                content=content,
                post_error=post_error)