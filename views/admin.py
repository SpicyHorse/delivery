from application import *
from models import *
from forms import *

@app.route('/admin/')
@require_admin
def admin_index():
	return render_template('admin/index.html')
