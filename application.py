from werkzeug.contrib.cache import SimpleCache
from functools import wraps
from flask import *
from os import path
import re
import config

app = Flask(__name__)
app.debug = config.APP_DEBUG
app.secret_key = config.APP_SECRET
cache = SimpleCache()

@app.errorhandler(404)
def page_not_found(error):
	return render_template('errors/404.html'), 404

@app.errorhandler(500)
def page_not_found(error):
	return render_template('errors/500.html'), 500

def require_login(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if g.user is None:
			return redirect(url_for('user_login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function

def require_admin(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if g.user is None:
			return redirect(url_for('user_login', next=request.url))
		if not g.user.is_admin:
			return abort(404)
		return f(*args, **kwargs)
	return decorated_function

filename_sanitizer_0 = re.compile(r'[^a-z0-9\.\(\)\-\ ]+', re.I)

def sendfile(file_path, file_name, redirect_base=None, speed_limit=None):
	file_name = filename_sanitizer_0.sub(' ', file_name) # sanitize
	if request.environ['SERVER_PORT'] == '5000':
		return send_file(file_path, as_attachment=True, attachment_filename=file_name)
	else:
		if redirect_base:
			file_path = '/%s/%s' % (redirect_base, path.split(file_path)[1])
		else:
			file_path = '/%s' % path.relpath(file_path)
		r = make_response()
		r.headers.add('Content-Type', 'application/oct-stream')
		r.headers.add('Content-Disposition', 'attachment', filename=file_name)
		r.headers.add('X-Accel-Redirect', file_path)
		if speed_limit:
			r.headers.add('X-Accel-Limit-Rate', speed_limit)
		return r

def paginate(query):
	
	return obj