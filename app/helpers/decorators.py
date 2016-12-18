from functools import wraps
from google.appengine.ext import db
import app.keys.postkey as pkey

#####Decorators accept any number of *args.  Each wrapper then takes the args tuple and converts it to a list with the list(args) call.  Then pull relevant information from list, and append the results.  Finish by passing *arglist.  The * unpacks the list into individual arguments.  If another decorator is called, those individual arguments are accepted by the *args parameter and turned into a tuple, where the next decorator begins the same process.  It is important that decorators are run in the following order exist > is_user > does_user_own, and that parameters in get and post are written in the following order (self, post_id, comment_id, post, comment, user)


def does_post_exist(function):
    @wraps(function)
    def wrapper(self, *args):
        arglist = list(args)
        post_id = arglist[0]
        key = db.Key.from_path('Post', int(post_id), parent=pkey.post_key())
        post = db.get(key)
        if post:
            arglist.append(post)
            return function(self, *arglist)
        else:
            self.error(404)
            return
    return wrapper

def does_comment_exist(function):
    @wraps(function)
    def wrapper(self, *args):
        arglist = list(args)
        post = arglist[2]
        comment_id = arglist[1]
        key = db.Key.from_path('Comment', int(comment_id))
        comment = db.get(key)
        if post and comment:
            arglist.append(comment)
            return function(self, *arglist)
        else:
            self.error(404)
            return
    return wrapper

def is_user(function):
    @wraps(function)
    def wrapper (self, *args):
        arglist = list(args)
        user = self.user
        if user:
            arglist.append(user)
            return function(self, *arglist)
        else:
            self.redirect('/login')
            return
    return wrapper

def does_user_own_post(function):
    @wraps(function)
    def wrapper (self, *args):
        arglist = list(args)
        post = arglist[1]
        if post and self.user.name == post.user.name:
            return function(self, *arglist)
        else:
            self.redirect('/blog/')
            return
    return wrapper

def does_user_own_comment(function):
    @wraps(function)
    def wrapper(self, *args):
        arglist = list(args)
        post = arglist[2]
        comment = arglist[3]
        if post and comment and self.user.name == comment.user.name:
            return function(self, *arglist)
        else:
            self.redirect('/login')
    return wrapper