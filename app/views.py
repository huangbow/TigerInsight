from app import app, db
import os
from flask import render_template, redirect, flash, request, session, json, url_for
from werkzeug import secure_filename
from .models import User, Customer, Interest

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
	return redirect('/')


@app.route('/dashboard')
def dashboard():
	if session.get('user'):
		return render_template('overview-table.html')
	else:
		return redirect('/home')

@app.route('/potential-customer-list')
def customer():
	customers = Customer.query.all()
	return render_template('potential-customer-list.html', customers=customers)

@app.route('/overview')
def overview():
	return redirect('/dashboard')


@app.route('/foodstyle')
def restaurantstyle():
	data = [
        {"text": "Italian Food", "count": "236"},
        {"text": "Asian", "count": "382"},
        {"text": "American", "count": "170"},
        {"text": "Burger", "count": "123"},
        {"text": "Pizza", "count": "12"},
        {"text": "Wine", "count": "170"},
        {"text": "Beer", "count": "370"},
        {"text": "Grill", "count": "10"},
        {"text": "Korean BBQ", "count": "170"},
      ]
	return render_template('/bubble-chart.html', input=json.dumps(data))

@app.route('/analysis')
def analysis():
	return render_template('/analysis.html')

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('analysis',
			                        filename=filename))
	return redirect('/analysis')