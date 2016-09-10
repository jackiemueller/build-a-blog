import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):

	subject = db.StringProperty(required=True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

	def render(self):
		self._render_text = self.content.replace('\n', '<br>')
		return render_str('post.html', p = self)


class Blog(BlogHandler):

	def write_Blog (self):
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
		error_message = self.error
		template = jinja_env.get_template('blog.html')
		template_values = {
		'posts': posts
        }

		self.response.write(template.render(template_values))

	def get(self):
		self.write_Blog()

class ViewPostHandler(BlogHandler):

	def get(self, post_id):
		post = Post.get_by_id(int(post_id))

		if not post:
			self.error(404)
			return

		self.render('permalink.html', post = post)


class NewPost(BlogHandler):

    def write_newPost(self, entryName="", entry="", error=""):
        error_message = self.error
        template = jinja_env.get_template('newPost.html')
        template_values = {
        'entryName': entryName,
		'entry': entry,
		'error': error
        }

        self.response.write(template.render(template_values))

    def get(self):
        self.write_newPost()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(subject = subject, content = content)
            key = post.put()
            self.redirect("/blog/%s" % key.id())
        else:
            error = "Oops! You forgot to enter a subject and some text"
            self.write_newPost(entryName=subject, entry=content, error=error)


app = webapp2.WSGIApplication([
    ('/', Blog),
	('/newpost', NewPost),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)
], debug=True)
