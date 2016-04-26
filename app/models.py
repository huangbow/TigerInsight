from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password = db.Column(db.String(120), index=True)
	def __repr__(self):
		return '<User %r>' % (self.email)


class Customer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(120), index=True, unique=True)
	name = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	facebook = db.Column(db.String(224), index=True, unique=True)

	def __repr__(self):
		return '<Customer %r' % (self.name)

class PotentialCustomer(object):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(120), index=True, unique=True)
	name = db.Column(db.String(64), index=True, unique=True)
	recommend = db.Column(db.String(400), index=True, unique=True)

	def __repr__(self):
		return '<PotentialCustomer %r' % (self.name)
		

class Interest(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	interest = db.Column(db.String(64), index=True)
	user_id = db.Column(db.String(64), db.ForeignKey('customer.id'))

	def __repr__(self):
		return '<Interest %r' % (self.interest)

class Food_style(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), index=True, unique=True)
	tags= db.Column(db.String(224), index=True, unique=True)

	def __repr__(self):
		return '<Food_style %r' % (self.name)
