import socket
from werkzeug.security import generate_password_hash, check_password_hash

class Controller(object):

	def __init__(self, plant_address="10.0.0.92", port=1025, pw="pw"):
		self.plant_address_ = plant_address
		self.port_ = port
		self.socket_ = None
		self.admin_pw_ = generate_password_hash(pw)
		self.active_ = None
		self.users_ = dict()
		self.mode_ = 0
		
	# Bootup procedure, connecting to plant
	def bootup(self):
		if self.socket_ == None:
			self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket_.connect((self.plant_address_, self.port_))
			print("Connection Successful")
		except:
			print("Connection Failed")
	
	# Add User
	def add_user(self):
		user = input("Enter User ID: ")
		pw = input("Enter User PW: ")
		pw2 = input("Confirm User PW: ")
		if user in self.users_.keys():
			print("User already exists")
			return None
		if pw == pw2:
			admin_pw = input("Enter Admin PW: ")
			if self.authenticate_admin(admin_pw):
				self.users_[user] = generate_password_hash(pw)
				print("User successfully added")
			else:
				print("Invalid Admin PW")
		else:
			print("Passwords do not match")
	
	# Create session bound to User
	def create_session(self):
		if self.active_ is None:
			user = input("Enter User ID: ")
			if user == "quit":
				self.mode_ = -1
			if user in self.users_.keys():
				self.active_ = user
				print("Session Created")
		
	# Authenticate Admin
	def authenticate_admin(self, pw):
		if check_password_hash(self.admin_pw_, pw):
			return True
		return False
		
	# Authenticate User
	def authenticate(self, pw):
		if self.active_ is None:
			return False
		elif check_password_hash(self.users_[self.active_], pw):
			return True
		return False
	
	# Admin mode
	def admin_main(self):
		while True:
			admin_pw = input("Enter Admin PW: ")
			if self.authenticate_admin(admin_pw):
				break
		while True:
			command = input("Choose action:\n1. Add User\n2. Exit\n")
			if command == "quit":
				self.mode_ = -1
				break
			try:
				command = int(command)
			except:
				print("Invalid Command")
				continue
			if command == 1:
				self.add_user()
			elif command == 2:
				self.mode_ = 1
				print("Exiting Admin Mode\n---")
				break
		
	# Control program main loop
	def prog_main(self):
		self.create_session()
		if self.mode_ < 0:
			print("Terminating Program")
			return None
		while (self.active_ is None) == False:
			print("Active User: {}".format(self.active_))
			try:
				command = input("Input Command (Integer):\n1. Replace filter\n2. Increase flow rate\n3. Decrease flow rate\n4. Increase vitamin input\n5. Decrease vitamin input\n6. Increase pH\n7. Decrease pH\n8. Halt Plant\n9. Run Plant\n10. End Session\n")
				if command == "admin":
					self.mode_ = 0
					print("Entering Admin Mode\n---")
					break
				elif command == "quit":
					self.mode_ = -1
					break
				try:
					command = int(command)
				except:
					print("Invalid Command")
					continue
				if command == 1:
					payload = "filter"
				elif command == 2:
					payload = "incFlow"
				elif command == 3:
					payload = "decFlow"
				elif command == 4:
					payload = "incVit"
				elif command == 5:
					payload = "decVit"
				elif command == 6:
					payload = "incpH"
				elif command == 7:
					payload = "decpH"
				elif command == 8:
					payload = "halt"
				elif command == 9:
				    payload = "run"
				else:
					continue
				pw = input("Enter User PW: ")
				if self.authenticate(pw):
					self.socket_.send(payload.encode('utf-8'))
					print("{} sent".format(payload))
				else:
					print("Invalid User PW")
			except KeyboardInterrupt:
				self.mode_ = -1
				break
		self.active_ = None
		print("Terminating Program")
		
	
	def main(self):
		while self.mode_ >= 0:
			if self.mode_ == 0:
				self.admin_main()
			elif self.mode_ == 1:
				self.prog_main()
			
if __name__ == "__main__":
	c = Controller()
	c.bootup()
	c.main()