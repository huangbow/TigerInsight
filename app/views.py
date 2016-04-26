from app import app, db
import os
from flask import render_template, redirect, flash, request, session, json, url_for, flash
from werkzeug import secure_filename
from .models import User, Customer, Interest, Food_style, PotentialCustomer

upload_success = True

@app.route('/')
def index():
	if session.get('user'):
		return render_template('logout.html', title='Tiger Insight', team='Team Tiger!')
	else:
		return redirect('/home')
	

@app.route('/home')
def home():
	return render_template('login.html', title='Tiger Insight', team='Team Tiger!')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
	try:
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']
		user = User.query.filter_by(email=_email, password=_password).first()
		if user:
			session['user'] = user.email
			return redirect('/dashboard')
		else:
			return redirect('/')
	except Exception, e:
		return str(e)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
	session.pop('user', None)
	upload_success=True
	return redirect('/')


@app.route('/dashboard')
def dashboard():
	if session.get('user'):
		return render_template('overview-table.html')
	else:
		return redirect('/home')

@app.route('/potential-customer-list')
def potentialcustomer():
	pcustomers = PotentialCustomer.query.all()
	return render_template('potential-customer-list.html', pcustomers=pcustomers)

@app.route('/potential-customer-list/<name>')
def showcustomer(name):
	return redirect(url_for('customerprofile', name=name))

@app.route('/overview')
def overview():
	return redirect('/dashboard')


@app.route('/foodstyle')
def restaurantstyle():
	foodstyle = Food_style.query.all()
	return render_template('/foodstyle.html', foodstyle=foodstyle)


@app.route('/analysis')
def analysis():
	return render_template('/analysis.html', success=upload_success)

@app.route('/customerprofile')
def customersprofile():
	customers = Customer.query.all()
	return render_template('/customer-profile.html', customers=customers)

@app.route('/customerprofile/<name>')
def customerprofile(name):
	customer = Customer.query.filter(Customer.name == name).all()
	return render_template('/customer-profile.html', customers=customer)

@app.route('/musicstyle')
def musicstyle():
	data = [
        {"text": "Jazz", "count": "236"},
        {"text": "Hip-Hop", "count": "382"},
        {"text": "Rhythm & Blues", "count": "170"},
        {"text": "Swing", "count": "123"},
        {"text": "Blue", "count": "12"},
        {"text": "Pop", "count": "170"},
        {"text": "Soul", "count": "370"},
        {"text": "Funk", "count": "10"},
        {"text": "County", "count": "170"},
      ]
	return render_template('/musicstyle.html', input=json.dumps(data))

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			global upload_success
			upload_success = False
			return render_template('/analysis.html', success=upload_success)
	return redirect('/analysis')