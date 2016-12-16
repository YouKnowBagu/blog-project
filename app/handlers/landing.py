import app.helpers.basehandler as basehandler
class Landing(basehandler.BlogHandler):
  def get(self):
      self.redirect('/blog')