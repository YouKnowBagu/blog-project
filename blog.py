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

def users_key(group = 'default'):
    return db.Key.from_path('users', group)


# REVIEW: Database model to store users
class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


#Set root key for posts to keep posts organized by specific blog, if multiple blogs are made.
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

def post_key(name = 'default'):
    return db.Key.from_path('Post', name)


# REVIEW: Placeholder in case I decide to add user groups later

# def group_key(name = 'default'):
#     return db.Key.from_path('Group', name)

# def user_key(name = 'default'):
#     return db.Key.from_path('User', name)



# REVIEW: Database model to store posts
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    user = db.ReferenceProperty(User, collection_name = 'user_posts')

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("permalink.html", post = self)


class Like(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)

    # get number of likes for a blog id
    @classmethod
    def by_post_id(cls, post_id):
        l = Like.all().filter('post =', post_id)
        return l.count()

    # get number of likes for a blog and user id
    @classmethod
    def check_like(cls, post_id, user_id):
        cl = Like.all().filter(
            'post =', post_id).filter(
            'user =', user_id)
        return cl.count()


#=UNLIKES====================================================

# create a database to store all unlikes
class Unlike(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)

    # get number of unlikes for a post id
    @classmethod
    def by_post_id(cls, post_id):
        ul = Unlike.all().filter('post =', post_id)
        return ul.count()

    # get number of unlikes for a post and user id
    @classmethod
    def check_unlike(cls, post_id, user_id):
        cul = Unlike.all().filter(
            'post =', post_id).filter(
            'user =', user_id)
        return cul.count()

class Comment(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    text = db.TextProperty(required=True)

    # get number of comments for a post id
    @classmethod
    def count_by_post_id(cls, post_id):
        c = Comment.all().filter('post =', post_id)
        return c.count()

    # get all comments for a specific post id
    @classmethod
    def all_by_post_id(cls, post_id):
        c = Comment.all().filter('post =', post_id).order('created')
        return c

class BlogFront(BlogHandler):
    def get(self):
        # get all blog posts
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        # if there are any existing blog posts render the page with those posts
        if posts:
            self.render("post.html", posts=posts)

class NewPost(BlogHandler):
    def get(self):
        # if user is logged in take us to newpost page
        if self.user:
            self.render('newpost.html')
        # otherwise take us to login page
        else:
            self.redirect("/login")
    def post(self):
        if not self.user:
            self.redirect('/blog')
        # get the subject, content of the post and username of the user
        subject = self.request.get("subject")
        content = self.request.get("content")
        user_id = User.by_name(self.user.name)

        # if we have a subject and content of the post add it to the database
        # and redirect us to the post page
        if subject and content:
            p = Post(
                parent=post_key(),
                subject=subject,
                content=content,
                user=user_id)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        # othersie throw and error to let the user know that both subject and
        # content are required
        else:
            post_error = "Please enter a subject and the blog content"
            self.render(
                "newpost.html",
                subject=subject,
                content=content,
                post_error=post_error)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id),
        parent = post_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        likes = Like.by_post_id(post)
        unlikes = Unlike.by_post_id(post)
        post_comments = Comment.all_by_post_id(post)
        comments_count = Comment.count_by_post_id(post)

        self.render(
            "permalink.html",
            post=post,
            likes=likes,
            unlikes=unlikes,
            post_comments=post_comments,
            comments_count=comments_count)

    def post(self, post_id):
        key = db.Key.from_path("Post", int(post_id), parent=post_key())
        post = db.get(key)
        user_id = User.by_name(self.user.name)
        comments_count = Comment.count_by_post_id(post)
        post_comments = Comment.all_by_post_id(post)
        likes = Like.by_post_id(post)
        unlikes = Unlike.by_post_id(post)
        previously_liked = Like.check_like(post, user_id)
        previously_unliked = Unlike.check_unlike(post, user_id)
        # check if the user is logged in
        if self.user:
            # if the user clicks on like
            if self.request.get("like"):
                if previously_liked == 0:
                    # add like to the likes database and refresh the page
                    l = Like(
                        post=post, user=User.by_name(
                            self.user.name))
                    l.put()
                    time.sleep(0.1)
                    self.redirect('/blog/%s' % str(post.key().id()))
                    # otherwise if the user has liked this post before throw
                    # and error
                else:
                    error = "You have already liked this post"
                    self.render(
                        "permalink.html",
                        post=post,
                        likes=likes,
                        unlikes=unlikes,
                        error=error,
                        comments_count=comments_count,
                        post_comments=post_comments)
            # if the user clicks on unlike
            elif self.request.get("unlike"):
                # first check if the user is trying to unlike his own post
                    # then check if the user has unliked this post before
                if previously_unliked == 0:
                    # add unlike to the unlikes database and refresh the
                    # page
                    ul = Unlike(
                        post=post, user=User.by_name(
                            self.user.name))
                    ul.put()
                    time.sleep(0.1)
                    self.redirect('/blog/%s' % str(post.key().id()))
                # otherwise if the user has unliked this post before throw
                # and error
                else:
                    error = "You have already unliked this post"
                    self.render(
                        "permalink.html",
                        post=post,
                        likes=likes,
                        unlikes=unlikes,
                        error=error,
                        comments_count=comments_count,
                        post_comments=post_comments)

            # if the user clicks on add comment get the comment text first
            elif self.request.get("add_comment"):
                comment_text = self.request.get("comment_text")
                # check if there is anything entered in the comment text area
                if comment_text:
                    # add comment to the comments database and refresh page
                    c = Comment(
                        post=post, user=User.by_name(
                            self.user.name), text=comment_text)
                    c.put()
                    time.sleep(0.1)
                    self.redirect('/blog/%s' % str(post.key().id()))
                # otherwise if nothing has been entered in the text area throw
                # an error
                else:
                    comment_error = "Please enter a comment in the text area to post"
                    self.render(
                        "permalink.html",
                        post=post,
                        likes=likes,
                        unlikes=unlikes,
                        comments_count=comments_count,
                        post_comments=post_comments,
                        comment_error=comment_error)
            # if the user clicks on edit post
            elif self.request.get("edit"):
                # take the user to edit post page
                self.redirect('/blog/editpost/%s' % str(post.key().id()))
            # if the user clicks on delete
            elif self.request.get("delete"):
                # delete the post and redirect to the main page
                db.delete(key)
                time.sleep(0.1)
                self.redirect('/')
        # otherwise if the user is not logged in take them to the login page
        else:
            self.redirect("/login")

# REVIEW: Functions using regular expressions to determine validity of input
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
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

# class Unit2Signup(Signup):
#     def done(self):
#         self.redirect('/unit2/welcome?name=' + self.name)

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog/welcome')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog/welcome')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path("Post", int(post_id), parent=post_key())
        post = db.get(key)

        # check if the user is logged in
        if self.user:
            self.render("editpost.html", post=post)
        else:
            self.redirect("/login")

    def post(self, post_id):
        # get the key for this blog post
        key = db.Key.from_path("Post", int(post_id), parent=post_key())
        post = db.get(key)

        # if the user clicks on update comment
        if self.request.get("update"):

            # get the subject, content and user id when the form is submitted
            subject = self.request.get("subject")
            content = self.request.get("content").replace('\n', '<br>')

            if subject and content:
                # update the blog post and redirect to the post page
                post.subject = subject
                post.content = content
                post.put()
                time.sleep(0.1)
                self.redirect('/blog/%s' % str(post.key().id()))
                # otherwise if both subject and content are not filled throw an
                # error
            else:
                post_error = "Please enter a subject and the blog content"
                self.render(
                    "editpost.html",
                    subject=subject,
                    content=content,
                    post_error=post_error)
        # if the user clicks cancel take them to the post page
        elif self.request.get("cancel"):
            self.redirect('/blog/%s' % str(post.key().id()))


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

class Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('blog.html', username = self.user.name)
        else:
            self.redirect('/signup')

# REVIEW: add individual post pages
app = webapp2.WSGIApplication([('/', Landing),
                            ('/blog/?', BlogFront),
                            ('/blog/newpost', NewPost),
                            ('/blog/welcome', Welcome),
                            ('/login', Login),
                            ('/blog/([0-9]+)', PostPage),
                            ('/blog/editpost/([0-9]+)', EditPost),
                            ('/logout', Logout),
                            ('/signup', Register),
                            ],
                            debug=True)
