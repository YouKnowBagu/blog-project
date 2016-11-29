import os
import re
from string import letters

import webapp2
import jinja2

# REVIEW: Using NDB instead of DB per googles recommendation
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


# REVIEW: *a and **kw are confusing concepts.  I learned more at https://docs.python.org/2/tutorial/controlflow.html to read more information.

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# REVIEW: This is a quality of life class that lets you avoid some typing.  Self was a difficult concept for me to grasp, but this answer at stack overflow epxlains it well: http://stackoverflow.com/a/2709832

class BlogHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

#Set root key for posts to keep posts organized by specific blog, if multiple blogs are made.
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class BlogMain(BlogHandler):
    def get(self):
        self.render('blog.html')

class NewPost(BlogHandler):
    def get(self):
        self.render('newpost.html')

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render('signup-form.html')

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username,
                      email = email)

        if not valid_username(username):
            params['error_username'] = "Invalid username"
            have_error = True

        if not valid_password(password):
            params['error_password'] = "Invalid password"
            have_error = True
        elif password != verify:
            params['error_verify'] = "Passwords do not match"

        if not valid_email(email):
            params['error_email'] = "Invalid email"
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.redirect('/welcome')

class Welcome(BlogHandler):
    def get(self):
        self.render('welcome.html')

# REVIEW: add individual post pages
app = webapp2.WSGIApplication([('/', BlogMain),
                            ('/newpost', NewPost),
                            ('/welcome', Welcome),
                            ('/signup', Signup)],
                            debug=True)
