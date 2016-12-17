from google.appengine.ext import db
import re
import app.helpers.basehandler as basehandler
import app.models.user as dbuser

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Signup(basehandler.BlogHandler):
    def get(self):
        self.render('signup-form.html')

    def post(self):
        if self.request.get('Login'):
            self.redirect('/login')
        else:
            have_error = False
            self.username = self.request.get('username')
            self.password = self.request.get('password')
            self.verify = self.request.get('verify')
            self.email = self.request.get('email')

            params = dict(username = self.username,
                          email = self.email)

            if not valid_username(self.username):
                params['error_username'] = "Invalid username."
                have_error = True

            if not valid_password(self.password):
                params['error_password'] = "Invalid password."
                have_error = True

            elif self.password != self.verify:
                params['error_verify'] = "Passwords do not match"
                have_error = True

            if have_error:
                self.render('signup-form.html', **params)
            else:
                self.done(**params)

    def done(self, **params):
        user = dbuser.User.by_name(self.username)
        if user:
            error = 'That user already exists.'
            self.render('signup-form.html', **params)
        else:
            user = dbuser.User.register(self.username, self.password, self.email)
            user.put()

            self.login(user)
            self.redirect('/blog')

