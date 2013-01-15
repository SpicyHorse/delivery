from application import *
from models import *
from forms import *
from storage import *

@app.route("/channel/")
@require_login
def channel_index():
	c = g.db.query(Channel).options(joinedload(Channel.games, innerjoin=False)).all()
	return render_template('channel/list.html', channels = c)

@app.route("/channel/add", methods=['GET', 'POST'])
@require_admin
def channel_add():
	f = ChannelForm(request.form)
	if request.method == 'POST' and f.validate():
		c = Channel()
		f.populate_obj(c)
		g.db.add(c)
		# create folder for channel
		create_channel_folders(c.name)
		# commit changes
		g.db.commit()
		flash('Ok computer','success')
		return redirect(url_for('channel_index'))
	return render_template("form.html", title="Channel from", form=f)

@app.route("/channel/<string:name>/")
@require_login
def channel_view(name):
	i = g.db.query(Channel).filter(Channel.name == name).first()
	if not i:
		return abort(404)
	return render_template('channel/view.html', channel = i)

@app.route("/channel/<string:channel>/add", methods=['GET', 'POST'])
@require_login
def channel_add_game(channel):
	c = g.db.query(Channel).filter(Channel.name == channel).first()
	if not c:
		return abort(404)
	f = GameForm(request.form)
	if request.method == 'POST' and f.validate():
		game = Game()
		f.populate_obj(game)
		game.channel = c
		g.db.add(game)
		# create game folders
		create_game_folders(channel, game.name)
		#commit changes
		g.db.commit()
		flash('Ok computer','success')
		return redirect(url_for('channel_view', name=channel))
	return render_template("form.html", title="Game form", form=f)

@app.route("/channel/<string:channel>/<string:game>")
@require_login
def channel_game_view(channel, game):
	i = g.db.query(Game).options(joinedload(Game.builds, innerjoin=False)).filter(Channel.name == channel).filter(Game.name==game).first()
	if not i:
		return abort(404)
	return render_template("channel/game_view.html", game=i)

@app.route("/channel/<string:channel>/<string:game>/add_build", methods=['GET', 'POST'])
@require_login
def channel_game_build_add(channel, game):
	i = g.db.query(Game).filter(Channel.name == channel).filter(Game.name==game).first()
	if not i:
		return abort(404)
	f = BuildForm(request.form)
	if request.method == 'POST' and f.validate():
		if len(os.listdir(os.path.join(config.UPLOAD_DIR, channel, game))) == 0:
			flash('Game folder for platform %s is empty. Upload at least something.' % f.platform.data,'error')
			return render_template("form.html", title="Build form", form=f)
		game_build = GameBuild()
		f.populate_obj(game_build)
		game_build.game = i
		g.db.add(game_build)
		g.db.flush()
		prepare_build(channel, game, game_build)
		g.db.commit()
		flash('Ok computer','success')
		return redirect(url_for('channel_game_view', channel=channel, game=game))
	return render_template("form.html", title="Build form", form=f)

@app.route("/channel/<string:channel>/<string:game>/<string:platform>/build/<int:build>", methods=['GET', 'POST'])
@require_login
def channel_game_build_activate(channel, game, platform, build):
	i = g.db.query(GameBuild).filter(GameBuild.id == build).first()
	if not i:
		return abort(404)
	if i.current:
		return abort(404)
	ai = g.db.query(GameBuild)\
		.filter(GameBuild.game == i.game)\
		.filter(GameBuild.platform == i.platform)\
		.filter(GameBuild.current == True)\
		.first()
	if ai:
		ai.current=False
		g.db.add(ai)
	i.current = True
	g.db.add(i)
	g.db.commit()
	return redirect(url_for('channel_game_view', channel=channel, game=game))

@app.route("/channel/<string:channel>/<string:game>/<string:platform>/wipe/<int:build>", methods=['GET', 'POST'])
@require_login
def channel_game_build_wipe(channel, game, platform, build):
	i = g.db.query(GameBuild).filter(GameBuild.id == build).first()
	if not i:
		return abort(404)
	if i.current:
		return abort(404)
	wipe_build(channel, game, i)
	g.db.delete(i)
	g.db.commit()
	return redirect(url_for('channel_game_view', channel=channel, game=game))

#
# Public part
#

@app.route("/channel/<string:channel>/<string:game>/<string:platform>/latest/<string:md5>")
def torrent_check(channel, game, platform, md5):
	# Fast inner join for querying
	i = g.db.query(GameBuild)\
		.join(Game)\
		.join(Channel)\
		.filter(Channel.name == channel)\
		.filter(Game.name == game)\
		.filter(GameBuild.current == True)\
		.filter(GameBuild.platform == platform.upper())\
		.first()
	if not i:
		return abort(404)
	if md5 == i.md5:
		return make_response("FRESH", 200)
	game_dst_torrent = os.path.join(config.STORAGE_DIR, channel, game, str(i.id), platform, "build.torrent")
	i.downloads += 1
	data = "UPDATE:"
	data += open(game_dst_torrent).read()
	g.db.add(i)
	g.db.commit()
	return make_response(data, 200)

@app.route("/channel/<string:publisher>/<string:game>/<string:platform>/storage/<path:file_path>")
def storage(publisher, game, platform, file_path):
	file_path = path.join('/Users/aku/Downloads/tmp/', file_path)
	file_name = path.basename(file_path)
	return sendfile(file_path, file_name)
