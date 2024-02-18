from face_detection import Training, Detection
from socket import gethostname, gethostbyname
from flask import Flask, request, render_template ,url_for,redirect, flash ,make_response
from form import RegistrationForm , LoginForm
import os
from flask import render_template, request, flash, redirect, url_for
from flask_jwt_extended import create_access_token, set_access_cookies, JWTManager
from form import LoginForm, RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import email
import psycopg2
from psycopg2 import sql
from flask import Flask, render_template, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = 'd270389871942afca232a044ca2a6f35'
app.config['JWT_SECRET_KEY'] = 'd270389871942afc' 
jwt = JWTManager(app)

@app.route('/')
def upload_form():
    return render_template('upload.html', root_path = app.root_path)

@app.route('/register' , methods=['GET'])
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)
@app.route('/register' , methods=['POST'])
def registerSubmit():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        # Hash the password for security
        password_hash = generate_password_hash(password)

        # Create a new user
        try:
            # Establish a connection to the ElephantSQL database
            conn = psycopg2.connect(
                host='lallah.db.elephantsql.com',
                user='lhxprdgr',
                password='detcwJGuoIxS4iEhQmTVZ2KkR0h4lyQa',
                database='lhxprdgr'
            )

            # Create a cursor object to interact with the database
            cursor = conn.cursor()

            # Insert the new user into the database
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )

            # Commit the changes to the database
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()

            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred while creating your account: {str(e)}', 'danger')
    else:
        flash('Please check your form', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)
@app.route('/login', methods=['POST'])
def loginprocess():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        try:
            # Establish a connection to the PostgreSQL database
            conn = psycopg2.connect(
                host='lallah.db.elephantsql.com',
                user='lhxprdgr',
                password='detcwJGuoIxS4iEhQmTVZ2KkR0h4lyQa',
                database='lhxprdgr'
            )

            # Create a cursor object to interact with the database
            cursor = conn.cursor()

            # Query the database for the user with the provided email
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()

            # If the user exists and the password is correct
            if user_data and check_password_hash(user_data[3], password):
                # Assuming the password hash is stored in the fourth column
                access_token = create_access_token(identity=email)
                response = make_response(redirect(url_for('upload_form')))
                set_access_cookies(response, access_token)
                flash('You have been logged in!', 'success')
                return response
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')

            # Close the cursor and connection
            cursor.close()
            conn.close()
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    
    if file.filename == '':
        return '<div style="color:red;">choose a file</div>'

    if file:
        file.save(os.path.join(app.root_path, 'uploads', file.filename))
        match = Detection()
        if match[file.filename]:
            return match[file.filename][0]
        else:
            return 'no face found'

if __name__ == '__main__':
    app.run(host=gethostbyname(gethostname()), debug=True, port = 5000)