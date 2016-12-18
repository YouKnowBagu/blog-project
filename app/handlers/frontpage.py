from google.appengine.ext import db
import app.helpers.basehandler as basehandler
import app.models.post as post


class BlogFront(basehandler.BlogHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("blog.html", posts=posts)