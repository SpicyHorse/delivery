from application import *
from models import *
from forms import *

# Public area
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
	f = UserLoginForm(request.form)
	if request.method == 'POST' and f.validate():
		u = User.find_by_email(f.email.data)
		print u
		if u == None or not u.check_password(f.password.data):
			flash('Wrong! Try one more time.', 'error')
			return render_template("form.html", title="Login", form=f)
		else:
			# remember for 30 days
			if f.remember.data:
				session.permanent = True
			# save id and shadow to session
			session['u'] = u.id
			session['p'] = u.password
			# set context
			g.user = u
			flash('Ok computer, nice to see you again!','success')
			# insure that we do not redirect user outside.
			if f.next.data.startswith(request.host_url):
				return redirect(f.next.data)
			else:
				return redirect('/')
	else:
		if request.args.has_key('next'):
			f.next.data = request.args['next']
		return render_template("form.html", title="Login", form=f)

@app.route('/user/logout')
@require_login
def user_logout():
	session.clear()
	flash('Sessions wiped, bye-bye!', 'success')
	return redirect('/')

@app.route('/user/registration/<string(32):guid>/', methods=['GET', 'POST'])
def user_registration(guid):
	i = Invite.find_by_guid(guid)
	if not i:
		return abort(404)
	f = UserRegistrationForm(request.form)
	if request.method == 'POST' and f.validate():
		u = User()
		f.populate_obj(u)
		g.db.add(u)
		g.db.commit()
		flash('Ok computer','success')
		return redirect('/')
	return render_template("form.html", title="Change Profile Data", form=f)

# internal area
@app.route('/user/profile')
@require_login
def user_profile():
	return render_template("user/profile.html")

@app.route('/user/password', methods=['GET', 'POST'])
@require_login
def user_password():
	f = UserPasswordForm(request.form)
	if request.method == 'POST' and f.validate():
		f.populate_obj(g.user)
		g.db.add(g.user)
		g.db.commit()
		flash('OK, password changed.','success')
		return redirect(url_for('user_profile'))
	else:
		f.process(obj=g.user)
	return render_template("form.html", title="Change Profile Data", form=f)

@app.route('/user/email', methods=['GET', 'POST'])
@require_login
def user_email():
	f = UserEmailForm(request.form)
	if request.method == 'POST' and f.validate():
		f.populate_obj(g.user)
		g.db.add(g.user)
		g.db.commit()
		flash('OK, email changed.','success')
		return redirect(url_for('user_profile'))
	else:
		f.process(obj=g.user)
	return render_template("form.html", title="Change Profile Data", form=f)
