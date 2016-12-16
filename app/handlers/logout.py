import app.helpers.basehandler as basehandler

#####Delete user cookies.
class Logout(basehandler.BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')