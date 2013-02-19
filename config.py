from os import path

# Application secret key for session encryption
APP_SECRET		= '412eb10d76c1aaabae094cc3a0148ee875b84331d8e7f8ca70f7d94d9b44fbcf'

# Application administrators
APP_ADMINS		= [ 1 ]

# Disable debug to enable session store encryption
APP_DEBUG		= True

# Database settings
DB_URL			= 'mysql://root:qwe123qwe@localhost/delivery'
DB_POOL_RTTL	= 60
DB_POOL_SIZE	= 4

# Delivery storage configuration
STORAGE_URL		= "http://storage"
STORAGE_DIR		= "storage"
UPLOAD_DIR		= "uploads"
TRACKERS		= [
	[	# First tire
		"http://delivery.spicyhorse.com:80/announce",
		"udp://delivery.spicyhorse.com:80",
	],
	[	# Second tire
		"udp://tracker.publicbt.com:80",
		"udp://tracker.openbittorrent.com:80"
	]
]
LAUNCHER_VERSION_MIN = 0
# your configuration can override some part of mine ;-)
if path.isfile('config_local.py'):
	execfile('config_local.py')
