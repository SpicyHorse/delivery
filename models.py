from datetime import datetime
from database import *

from os import urandom, path
from hashlib import sha256
from binascii import b2a_hex

import config

if config.APP_DEBUG:
	engine = create_engine(config.DB_URL, poolclass=QueuePool, pool_recycle=config.DB_POOL_RTTL, echo=True)
else:
	engine = create_engine(config.DB_URL, pool_size=config.DB_POOL_SIZE, pool_recycle=config.DB_POOL_RTTL)
database_session = scoped_session(sessionmaker(bind=engine))
metadata = MetaData()
ModelBase = declarative_base(metadata=metadata, bind=engine, metaclass=ModelMeta)

class User(ModelBase):
	id			= Column(Integer, primary_key=True)
	name		= Column(String(40), nullable=False, unique=True)
	email		= Column(String(320), nullable=False, unique=True)
	salt		= Column(String(6), nullable=False)
	salted		= Column(String(64), nullable=False)
	
	def __init__(self, name, email, password=None):
		self.name = name
		self.email = email
		self.password = password
	
	@property
	def password(self):
		return self.salted
	
	@password.setter
	def password(self, value):
		self.salt = b2a_hex(urandom(3))
		self.salted = sha256(value + self.salt).hexdigest()
	
	def check_password(self, value):
		return self.salted == sha256(value + self.salt).hexdigest()
	
	@property
	def is_admin(self):
		return self.id in config.APP_ADMINS
	
	@staticmethod
	def find_by_id(id):
		return database_session.query(User).filter(User.id == id).first()
	
	@staticmethod
	def find_by_email(email):
		return database_session.query(User).filter(User.email == email).first()

class Channel(ModelBase):
	id			= Column(Integer, primary_key=True)
	name		= Column(String(128), nullable=False, unique=True)
	description	= Column(String(512))

	def __init__(self, name=None, description=None):
		self.name = name
		self.description = description

class Game(ModelBase):
	id			= Column(Integer, primary_key=True)
	name		= Column(String(128), nullable=False, unique=True)
	description	= Column(String(512))
	channel_id	= Column(Integer, ForeignKey('Channel.id'), nullable=False)
	# relations
	channel		= relation(Channel, backref='games')

	def __init__(self, name=None, description=None):
		self.name = name
		self.description = description

class GameBuild(ModelBase):
	id			= Column(Integer, primary_key=True)
	name		= Column(String(128), nullable=False, unique=True)
	description	= Column(String(512))
	md5			= Column(String(32), index=True)
	current		= Column(Boolean, index=True, nullable=False, default=False)
	created_at	= Column(DateTime, nullable=False, default=datetime.now)
	platform	= Column(Enum('WIN', 'MAC', 'LIN', name="platform"), nullable=False)
	game_id		= Column(Integer, ForeignKey('Game.id'), nullable=False)
	downloads	= Column(Integer, nullable=False, default=0)
	# relations
	game		= relation(Game, backref='builds')

	def __init__(self, name=None, description=None):
		self.name = name
		self.description = description
