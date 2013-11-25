# -*- coding: utf-8 -*-
from sqlalchemy import MetaData
from sqlalchemy import Column, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Base.metadata = MetaData()

class Terminal(Base):
	__tablename__ = 'terminal'

	id	= Column(Integer, primary_key=True)
	user_id	= Column(Integer)
	name	= Column(Text)
	agent	= Column(Text)
	l2addr	= Column(Text)
	enabled	= Column(Text)

	def __str__(self):
		return "name=%s, mac address=%s" %(self.name, self.l2addr)

def getMySQLSession(username, hostname, password, database):
	uri = 'mysql://%s:%s@%s/%s' %(password, username, hostname, database)
	engine = create_engine(uri)
	MySQLSession = sessionmaker(bind=engine)

	session = MySQLSession()
	return session

