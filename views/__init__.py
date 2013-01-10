from application import app, g, session, request, redirect, url_for
from models import database_session, User

__all__ = [ "admin", "user", "channel" ]

@app.route('/')
def index():
	return redirect(url_for("channel_index"))

def is_active(name):
	if request.endpoint and request.endpoint.startswith(name):
		return 'active'
	else:
		return ''

@app.before_request
def before_request():
	g.is_active = is_active
	g.db = database_session()
	if session.has_key('u') and session.has_key('p'):
		u = User.find_by_id(session['u'])
		if u and u.password == session['p']:
			g.user = u
		else:
			g.user = None
	else:
		g.user = None

@app.teardown_request
def after_request(response):
	g.db.close()
	return response
