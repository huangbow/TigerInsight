from app import app, db
import os, sys
from flask import render_template, redirect, flash, request, session, json, url_for, flash
from werkzeug import secure_filename
from .models import User, Customer, Interest, Food_style, PotentialCustomer
from .model.prediction import Prediction

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
	session.pop('cat_num', None)
	return redirect('/')


##################################
######    Dash Board #############

@app.route('/dashboard')
def dashboard():
	if session.get('user'):
		return render_template('overview-table.html')
	else:
		return redirect('/home')


def checkDataExist():
	if session.get('cat_num'):
		return True
	return False

@app.route('/overview')
def overview():
	return redirect('/dashboard')




@app.route('/analysis')
def analysis():
	if checkDataExist():
		return redirect(url_for('showanAlysisResult', cat_num=session['cat_num']))
	return render_template('/analysis.html')

@app.route('/analysis/<int:cat_num>')
def showanAlysisResult(cat_num):
	return render_template('/analysis.html', cat_num=cat_num)

@app.route('/analysis/upload_file', methods=['GET', 'POST'])
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
	session.pop('cat_num', None) # clean history result
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file_to_save_path = app.config['UPLOAD_FOLDER']
			file.save(file_save_path)
			

			prediction = Prediction()
			prediction.prediction(file_save_path, file_to_save_path)
			# register a session to store the number of categories
			session['cat_num'] = prediction.category_num

			return redirect(url_for('showanAlysisResult', cat_num=session['cat_num']))#hard code

	return redirect('/analysis')

	
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/potential-customer-list')
def potentialcustomer():
	if not checkDataExist():
		return redirect(url_for('analysis'))
	pc_list_name = os.path.join(app.config['UPLOAD_FOLDER'], 'target_selection.txt')
	pcustomers = []
	with open(pc_list_name, 'rb') as file:
		customers = file.readlines()
		for pc in customers:
			customer = pc.split(',')
			pcustomers.append(customer)

	return render_template('/potential-customer-list.html', pcustomers=pcustomers)


@app.route('/recommend')
def recommend():
	if not checkDataExist():
		return redirect(url_for('analysis'))
	pcustomers = PotentialCustomer.query.all()
	return render_template('recommend.html', pcustomers=pcustomers)

@app.route('/recommend/<name>')
def showcustomer(name):
	return redirect(url_for('customerprofile', name=name))




@app.route('/foodstyle')
def restaurantstyle():
	foodstyle = Food_style.query.all()
	return render_template('/foodstyle.html', foodstyle=foodstyle)



@app.route('/musicstyle')
def musicstyle():
	music_data = open('./data/musicdata.json').read() # json object
	return render_template('/musicstyle.html', input=music_data)


@app.route('/customerprofile')
def customersprofile():
	if not checkDataExist():
		return redirect(url_for('analysis'))
	customers = Customer.query.all()
	return render_template('/customer-profile.html', customers=customers)

@app.route('/customerprofile/<name>')
def customerprofile(name):
	customer = Customer.query.filter(Customer.name == name).all()
	return render_template('/customer-profile.html', customers=customer)









