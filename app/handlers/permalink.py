from google.appengine.ext import db
from functools import wraps
import app.helpers.basehandler as basehandler
import app.helpers.decorators as decorators
import app.models.like as dblike
import app.models.unlike as dbunlike
import app.models.comment as dbcomment
import app.models.user as dbuser
import app.models.post as dbpost
import time

is_user = decorators.is_user
does_post_exist = decorators.does_post_exist
does_user_own_post = decorators.does_user_own_post

Like = dblike.Like
Unlike = dbunlike.Unlike
Comment = dbcomment.Comment
User = dbuser.User
Post = dbpost.Post

class PostPage(basehandler.BlogHandler):

    @does_post_exist
    def get(self, post_id, post):
        likes = Like.by_post_id(post)
        unlikes = Unlike.by_post_id(post)
        comments = Comment.all_by_post_id(post)
        comment_count = Comment.count_by_post_id(post)

        self.render ("permalink.html",
            post=post,
            likes=likes,
            unlikes=unlikes,
            comments=comments,
            comment_count=comment_count)

    @does_post_exist
    @is_user
    def post(self, post_id, post, user):


#####Getting the information we will need to update the database depending on the users
#####input
        comment_count = Comment.count_by_post_id(post)
        comments = Comment.all_by_post_id(post)
        likes = Like.by_post_id(post)
        unlikes = Unlike.by_post_id(post)
        liked = Like.check_like(post, user)
        unliked = Unlike.check_unlike(post, user)

#####Due to a python check in the HTML, "Like" and "Unlike" will only appear on
#####other user's posts.  Likewise, "Edit" and "Delete" will only appear on your own posts

#####If the user is logged in and clicks the like button, first check to see if
#####the user has liked the post before, if not, add one like, otherwise output error.
        if self.request.get("like"):
            if liked == 0:
                like = Like(
                    post=post, user=user)
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
                    post=post, user=user)
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
                    post=post, user=user, text=comment_text)
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
        # elif self.request.get("edit_comment"):
        #     comment = self.request.get('comment')
        #     self.redirect('/blog/%s/editcomment/%s' % (str(post_id),  int(comment.key().id())))
#####If the user is logged in and clicks the edit button, take them to editpost.html
        # elif self.request.get('comment_delete'):
        #     db.delete(comment.key().id())
        #     time.sleep(0.1)
        #     self.redirect('/')

        elif self.request.get("edit"):
            self.redirect('/blog/editpost/%s' % str(post.key().id()))

#####If the user is logged in and clicks the delete button, delete the post entry from
#####the database.  NOTE:  This also deletes all comments associated with that post.
        elif self.request.get("delete"):
            db.delete(post)
            time.sleep(0.1)
            self.redirect('/')