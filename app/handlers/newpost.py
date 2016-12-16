import app.helpers.basehandler as basehandler
import app.helpers.decorators as decorator
import app.models.user as dbuser
import app.models.post as dbpost
import app.keys.postkey as postkey

User = dbuser.User
postkey = postkey.post_key

class NewPost(basehandler.BlogHandler):
    @decorator.is_user
    def get(self):
            self.render('newpost.html')

    @decorator.is_user
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        user_id = User.by_name(self.user.name)

        if subject and content:
            p = dbpost.Post(
                parent=postkey(),
                subject=subject,
                content=content,
                user=user_id)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            post_error = "All fields required"
            self.render(
                "newpost.html",
                subject=subject,
                content=content,
                post_error=post_error)