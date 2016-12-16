from google.appengine.ext import db
import app.helpers.basehandler as basehandler
import app.models.user as dbuser

class Login(basehandler.BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        if self.request.get('Register'):
            self.redirect('/signup')
        else:
            username = self.request.get('username')
            password = self.request.get('password')
            user = dbuser.User.login(username, password)
            if user:
                self.login(user)
                self.redirect('/blog/')
            else:
                error = 'Invalid login'
                self.render('login-form.html', error = error)