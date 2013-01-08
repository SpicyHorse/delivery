from pyftpdlib import ftpserver
from models import User

class DeliveryAuth(ftpserver.DummyAuthorizer):
	def validate_authentication(self, username, password):
		u = User.findByEmail(username)
		return u and u.check_password(password) or False

def create_server():
	handler = ftpserver.FTPHandler
	handler.authorizer = DeliveryAuth()
	handler.banner = "Always spicy, Always ready to deliver.\nUse your email as username."
	server = ftpserver.FTPServer(('', 21), handler)
	server.max_cons = 256
	server.max_cons_per_ip = 5
	return server