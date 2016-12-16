import webapp2
import re
import random
from app.helpers import basehandler
from app.security import secret
import app.handlers.editcomment as editcommenthandler
import app.handlers.landing as landinghandler
import app.handlers.login as loginhandler
import app.handlers.logout as logouthandler
import app.handlers.frontpage as fronthandler
import app.handlers.editpost as editposthandler
import app.handlers.signup as signuphandler
import app.handlers.permalink as postpagehandler
import app.handlers.newpost as newposthandler
import app.handlers.deletecomment as deletecommenthandler




# def render_post(response,j post):
#     response.out.write('<b>' + post.subject + '</b><br>')
#     response.out.write(post.content)

app = webapp2.WSGIApplication([('/', landinghandler.Landing),
                            ('/blog/?', fronthandler.BlogFront),
                            ('/blog/newpost', newposthandler.NewPost),
                            ('/login', loginhandler.Login),
                            ('/blog/([0-9]+)/deletecomment/([0-9]+)', deletecommenthandler.DeleteComment),
                            (r'/blog/([0-9]+)', postpagehandler.PostPage),
                            ('/blog/editpost/([0-9]+)', editposthandler.EditPost),
                            ('/blog/([0-9]+)/editcomment/([0-9]+)', editcommenthandler.EditComment),
                            ('/logout', logouthandler.Logout),
                            ('/signup', signuphandler.Signup),
                            ],
                                 debug=True)