from google.appengine.ext import db
import app.models.user as dbuser

# from app.helpers import BlogHandler
##### Database model to store posts with reference to User.
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    user = db.ReferenceProperty(dbuser.User, collection_name = 'user_posts')

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return basehandler.render_str("permalink.html", post = self)