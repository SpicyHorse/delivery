from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relation, backref, joinedload
from sqlalchemy.pool import QueuePool
from sqlalchemy.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.types import TypeDecorator, CHAR, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import asc, desc

from sqlalchemy import Integer, Boolean, Date, DateTime, String, Text
from sqlalchemy import Column, Table, ForeignKey, orm
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint

import config
import uuid

__all__ = (
	'create_engine', 'scoped_session', 'declarative_base', 'sessionmaker',
	'ModelMeta', 'MetaData', 'QueuePool',
	'Table', 'Column',
	'Integer', 'String', 'Boolean', 'DateTime', 'Text', 'GUID', 'Enum',
	'ForeignKey', 'PrimaryKeyConstraint',
	'relation', 'backref', 'joinedload',
	'asc', 'desc'
)

class GUID(TypeDecorator):
	"""Platform-independent GUID type.

	Uses Postgresql's UUID type, otherwise uses
	CHAR(32), storing as stringified hex values.

	"""
	impl = CHAR

	def load_dialect_impl(self, dialect):
		if dialect.name == 'postgresql':
			return dialect.type_descriptor(UUID())
		else:
			return dialect.type_descriptor(CHAR(32))
	
	def process_bind_param(self, value, dialect):
		if value is None:
			return value
		elif dialect.name == 'postgresql':
			return str(value)
		else:
			if not isinstance(value, uuid.UUID):
				return "%.32x" % uuid.UUID(value)
			else:
				# hexstring
				return "%.32x" % value
	
	def process_result_value(self, value, dialect):
		if value is None:
			return value
		else:
			return uuid.UUID(value)
	
	@staticmethod
	def GUID():
		return uuid.uuid1()

class ModelMeta(DeclarativeMeta):
	def __init__(cls, classname, bases, dict_):
		if '_decl_class_registry' not in cls.__dict__:
			if '__tablename__' not in cls.__dict__:
				cls.__tablename__ = classname
			elif cls.__tablename__ is None:
				del cls.__tablename__
			cls.metadata.__dict__.setdefault('_mapped_models', set()).add(cls)
			table_args = getattr(cls, '__table_args__', {})
			if isinstance(table_args, dict):
				table_kwargs = dict(**table_args)
				cls.__table_args__ = table_kwargs
			else:
				table_kwargs = dict(_default_table_kwargs, **table_args[-1])
				cls.__table_args__ = table_args[:-1] + (table_kwargs,)
		return super(ModelMeta, cls).__init__(classname, bases, dict_)
