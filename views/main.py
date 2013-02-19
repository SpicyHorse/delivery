from application import *
from datetime import timedelta
from models import *

from json import JSONEncoder

@app.route('/')
def index():
	dl_cnt = g.db.query(
			DownloadHistory.downloaded_at,
			func.count('*').label('dl_cnt'),
			func.max(DownloadHistory.seed_cnt).label('seed_cnt'),
			func.max(DownloadHistory.peer_cnt).label('peer_cnt')
		)\
		.filter(DownloadHistory.downloaded_at > datetime.now()-timedelta(1))\
		.group_by(func.hour(DownloadHistory.downloaded_at))\
		.order_by(DownloadHistory.downloaded_at)\
		.all()
	enc = JSONEncoder()
	dl_cnt_p = [[],[],[]]
	for i in xrange(0, 25):
		dl_cnt_p[0].append([i,0])
		dl_cnt_p[1].append([i,0])
		dl_cnt_p[2].append([i,0])
	for i in dl_cnt:
		x = i[0].hour
		dl_cnt_p[0][x] = [x, i[1]]
		dl_cnt_p[1][x] = [x, i[2]]
		dl_cnt_p[2][x] = [x, i[3]]
	cnt_stats = g.db.query(
			DownloadHistory.country_code,
			func.count('*').label('dl_cnt')
		)\
		.filter(DownloadHistory.downloaded_at > datetime.now()-timedelta(1))\
		.group_by(DownloadHistory.country_code)\
		.order_by(DownloadHistory.country_code)\
		.all()
	print cnt_stats
	return render_template("index.html", dl_cnt_p=dl_cnt_p, cnt_stats=cnt_stats)
