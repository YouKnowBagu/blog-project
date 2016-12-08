import os
import re
import random
import hashlib
import hmac
from string import letters
import time

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

secret = '130fkjU772ifha096%#$72jl7nnuajv987w3nklsgloayvnervqi'

# REVIEW: *a and **kw were confusing concepts.  I learned more at https://docs.python.org/2/tutorial/controlflow.html

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return "%s|%s" % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

# REVIEW: Self was a difficult concept for me to grasp, but this answer at stack overflow epxlains it well: http://stackoverflow.com/a/2709832

#Class and functions to make commonly repeated tasks easier to execute
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
        'Set-Cookie',
        '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie',
        'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

#Redirect, in case I want the base URL to do something else later.
class Landing(BlogHandler):
  def get(self):
      self.redirect('/blog')

##### Password security
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)
##### blog_key is a placeholder in case the site is expanded to include more than one blog.
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

def user_key(name = 'default'):
    return db.Key.from_path('User', name)

def post_key(name = 'default'):
    return db.Key.from_path('Post', name)

#To highlight current active page
def check_path(self):
    return self.request.path

# REVIEW: Database model to store users
class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = user_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = user_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

##### Database model to store posts with reference to User.
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    user = db.ReferenceProperty(User, collection_name = 'user_posts')

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("permalink.html", post = self)

##### Database model to store likes, referencing the post and user.
class Like(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)

    @classmethod
    def by_post_id(cls, post_id):
        like = Like.all().filter('post =', post_id)
        return like.count()

    @classmethod
    def check_like(cls, post_id, user_id):
        liked = Like.all().filter(
            'post =', post_id).filter(
            'user =', user_id)
        return liked.count()

#####Same as above but for unlikes
class Unlike(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)

    @classmethod
    def by_post_id(cls, post_id):
        unlike = Unlike.all().filter('post =', post_id)
        return unlike.count()

    @classmethod
    def check_unlike(cls, post_id, user_id):
        unliked = Unlike.all().filter(
            'post =', post_id).filter(
            'user =', user_id)
        return unliked.count()

#### To store comments on individual posts, referencing Post and User.
class Comment(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    text = db.TextProperty(required=True)

    @classmethod
    def count_by_post_id(cls, post_id):
        comments = Comment.all().filter('post =', post_id)
        return comments.count()

    @classmethod
    def all_by_post_id(cls, post_id):
        comments = Comment.all().filter('post =', post_id).order('created')
        return comments

class BlogFront(BlogHandler):
    def get(self):
        path_check = check_path(self)
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        if posts:
            self.render("blog.html", posts=posts, path_check=path_check)

#####: Functions using regular expressions to determine validity of input
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
        path_check = check_path(self)
        self.render('signup-form.html', path_check=path_check)

    def post(self):
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

        if not valid_email(self.email):
            params['error_email'] = "Invalid email"
            have_error = True

        if have_error:
            self.render('signup-form.html', path_check=path_check, **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        path_check = check_path(self)
        user = User.by_name(self.username)
        if user:
            error = 'That user already exists.'
            self.render('signup-form.html', error_username = error, path_check = path_check)
        else:
            user = User.register(self.username, self.password, self.email)
            user.put()

            self.login(user)
            self.redirect('/blog/')

class Login(BlogHandler):
    def get(self):
        path_check = check_path(self)
        self.render('login-form.html', path_check=path_check)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        path_check = check_path(self)
        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect('/blog/')
        else:
            error = 'Invalid login'
            self.render('login-form.html', error = error, path_check=path_check)

class NewPost(BlogHandler):
    def get(self):
        path_check = check_path(self)
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect("/login")
    def post(self):
        if not self.user:
            self.redirect('/blog')
        subject = self.request.get("subject")
        content = self.request.get("content")
        user_id = User.by_name(self.user.name)

        if subject and content:
            post = Post(
                parent=post_key(),
                subject=subject,
                content=content,
                user=user_id)
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            post_error = "All fields required"
            self.render(
                "newpost.html",
                subject=subject,
                content=content,
                post_error=post_error)

class PostPage(BlogHandler):
    def get(self, post_id):
        path_check = check_path(self)
        key = db.Key.from_path('Post', int(post_id),
        parent = post_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        likes = Like.by_post_id(post)
        unlikes = Unlike.by_post_id(post)
        comments = Comment.all_by_post_id(post)
        comment_count = Comment.count_by_post_id(post)

        self.render(
            "permalink.html",
            post=post,
            likes=likes,
            unlikes=unlikes,
            comments=comments,
            comment_count=comment_count)

    def post(self, post_id):
#####Getting the information we will need to update the database depending on the users
#####input
        key = db.Key.from_path("Post", int(post_id), parent=post_key())
        post = db.get(key)
        user_id = User.by_name(self.user.name)
        comment_count = Comment.count_by_post_id(post)
        comments = Comment.all_by_post_id(post)
        likes = Like.by_post_id(post)
        unlikes = Unlike.by_post_id(post)
        liked = Like.check_like(post, user_id)
        unliked = Unlike.check_unlike(post, user_id)

#####Due to a python check in the HTML, "Like" and "Unlike" will only appear on
#####other user's posts.  Likewise, "Edit" and "Delete" will only appear on your own posts

#####If the user is logged in and clicks the like button, first check to see if
#####the user has liked the post before, if not, add one like, otherwise output error.
        if self.user:
            if self.request.get("like"):
                if liked == 0:
                    like = Like(
                        post=post, user=user_id)
                    like.put()
                    time.sleep(0.1)
                    self.redirect('/blog/%s' % str(post.key().id()))
                else:
                    error = "You can only like a post one time."
                    self.render(
                        "permalink.html",
                        post=post,
                        likes=likes,
                        unlikes=unlikes,
                        error=error,
                        comment_count=comment_count,
                        comments=comments)
#####If the user is logged in and clicks the unlike button, first check to see if
#####the user has unliked the post before, if not, add one like, otherwise output error.
            elif self.request.get("unlike"):
                if unliked == 0:
                    ul = Unlike(
                        post=post, user=user_id)
                    ul.put()
                    time.sleep(0.1)
                    self.redirect('/blog/%s' % str(post.key().id()))
                else:
                    error = "You can only unlike a post one time."
                    self.render(
                        "permalink.html",
                        post=post,
                        likes=likes,
                        unlikes=unlikes,
                        error=error,
                        comment_count=comment_count,
                        comments=comments)
#####If the user is logged in and clicks the comment button, first check that the user
#####has filled ou the form.  If so, post the comment to the database and update the
#####post's permalink.  If not, render error.
            elif self.request.get("add_comment"):
                comment_text = self.request.get("comment_text")
                if comment_text:
                    comment = Comment(
                        post=post, user=user_id, text=comment_text)
                    comment.put()
                    time.sleep(0.1)
                    self.redirect('/blog/%s' % str(post.key().id()))
                else:
                    comment_error = "All fields required."
                    self.render(
                        "permalink.html",
                        post=post,
                        likes=likes,
                        unlikes=unlikes,
                        comment_count=comment_count,
                        comments=comments,
                        comment_error=comment_error)
#####If the user is logged in and clicks the edit button, take them to editpost.html

            elif self.request.get("edit"):
                self.redirect('/blog/editpost/%s' % str(post.key().id()))
#####If the user is logged in and clicks the delete button, delete the post entry from
#####the database.  NOTE:  This also deletes all comments associated with that post.
            elif self.request.get("delete"):
                db.delete(key)
                time.sleep(0.1)
                self.redirect('/')
        else:
            self.redirect("/login")





class EditPost(BlogHandler):
    def get(self, post_id):
#####Grab the posts id.
        key = db.Key.from_path("Post", int(post_id), parent=post_key())
        post = db.get(key)
#####If the user is logged in, take them to the editpost.html page.  otherwise
#####direct user to login page.
        if self.user:
            self.render("editpost.html", post=post)
        else:
            self.redirect("/login")

    def post(self, post_id):
#####Grab the post ID to be sure the proper post is updated/edited.
        key = db.Key.from_path("Post", int(post_id), parent=post_key())
        post = db.get(key)
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
                self.redirect('/blog/%s' % str(post.key().id()))
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
            self.redirect('/blog/%s' % str(post.key().id()))
class EditComment(BlogHandler):
    def get(self, post_id, comment_id):
#####Find the comment ID to be updated.
        key = db.Key.from_path("Comment", int(comment_id))
        comment = db.get(key)
        if comment:
                self.render("editcomment.html", comment=comment)
        else:
            error = "This comment no longer exists"
            self.render("editcomment.html", edit_error=error)

    def post(self, post_id, comment_id):
        pkey = db.Key.from_path("Post", int(post_id), parent=post_key())
        post = db.get(pkey)
        key = db.Key.from_path("Comment", int(comment_id))
        comment = db.get(key)

        if self.request.get("update"):
            content = self.request.get("comment")

            if content:
                comment.text = content
                comment.put()
                time.sleep(0.1)
                self.redirect('/blog/%s' % str(post.key().id()))
            else:
                edit_error="All fields required."
                self.render(
                'editcomment.html',
                comment=comment,
                edit_error = edit_error)

        elif self.request.get("cancel"):
            self.redirect('/blog/%s' % str(post.key().id()))

#####Delete user cookies.
class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

#####From the homework, not used in final product.
# class Welcome(BlogHandler):
#     def get(self):
#         if self.user:
#             self.render('blog.html', username = self.user.name, path_check=path_check)
#         else:
#             self.redirect('/signup')

app = webapp2.WSGIApplication([('/', Landing),
                            ('/blog/?', BlogFront),
                            ('/blog/newpost', NewPost),
                            ('/login', Login),
                            ('/blog/([0-9]+)', PostPage),
                            ('/blog/editpost/([0-9]+)', EditPost),
                            ('/blog/([0-9]+)/editcomment/([0-9]+)', EditComment),
                            ('/logout', Logout),
                            ('/signup', Register),
                            ],
                            debug=True)
