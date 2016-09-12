import webapp2
import jinja2
import os
import cgi
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Newpost(Handler):
    def render_newpost(self, title="", post="", error=""):
        self.render("newpost.html", title=title, post=post, error=error,)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            a = Post(title = title, post = post)
            a.put()

            self.redirect("/blog")
        else:
            error = "Please enter both a title and some content to post."
            self.render_newpost(title, post, error)

class Blog(Handler):
    def render_blog(self, title="", post="", error=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, post=post, error=error, posts=posts)

    def get(self):
        title = self.request.get("title")
        post = self.request.get("post")
        self.render_blog(title, post)

class ViewPostHandler(Handler):
    def get(self, id):
        desiredPost = Post.get_by_id(int(id))
        if desiredPost:
            title = desiredPost.title
            post = desiredPost.post
            self.render("indPost.html", title=title, post=post)
        else:
            error = "Invalid post id.  Please use a valid id."
            self.render("indPost.html", error=error)

app = webapp2.WSGIApplication([
    ('/blog', Blog),
    ('/newpost', Newpost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
