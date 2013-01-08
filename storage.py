from hashlib import md5
import os

from torrent import *
import config

def mkdir(name):
	if not os.path.exists(name):
		os.mkdir(name)

def create_channel_folders(channel):
	for base in [ config.UPLOAD_DIR, config.STORAGE_DIR ]:
		mkdir(os.path.join(base, channel))

def create_game_folders(channel, game):
	for base in [ config.UPLOAD_DIR, config.STORAGE_DIR ]:
		game_folder = os.path.join(base, channel, game)
		mkdir(game_folder)
		for i in [ "win", "mac", "lin" ]:
			game_folder_p = os.path.join(game_folder, i)
			mkdir(game_folder_p)

def prepare_build(channel, game, build):
	# gen vars
	game_src_dir = os.path.join(config.UPLOAD_DIR, channel, game, build.platform.lower())
	game_dst_base = os.path.join(config.STORAGE_DIR, channel, game, str(build.id))
	game_dst_dir = os.path.join(game_dst_base, build.platform.lower())
	game_dst_torrent = os.path.join(game_dst_dir, "build.torrent")
	storage_url = config.STORAGE_URL + "/storage/%s/%s/%s/" % (channel, game, str(build.id))
	# syncronize
	mkdir(game_dst_base)
	r = os.system("rsync -a %s/ %s/" % (game_src_dir, game_dst_dir))
	if r != 0:
		raise Exception("Unable to syncronize game folder")
	# create torrent
	torrent = bencode(Metainfo(game_src_dir, announce=config.TRACKERS, url_list=storage_url))
	open(game_dst_torrent,"w").write(torrent)
	# add signature to build
	build.md5 = md5(torrent).hexdigest()

def get_torrent_content(channel, game, platform):
	game_path = os.path.join(config.STORAGE_DIR, channel, game, platform)
