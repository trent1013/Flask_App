# This file contains an example Flask-User application.
# To keep the example simple, we are applying some unusual techniques:
# - Placing everything in one file
# - Using class-based configuration (instead of file-based configuration)
# - Using string-based templates (instead of file-based templates)

from flask import Flask, render_template_string, request
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
import boto3

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quickstart_app.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "SCF Data Ingest Login"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


def create_app():
    """ Flask application factory """
    
    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)

    # Define the User data-model.
    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        email_confirmed_at = db.Column(db.DateTime())

        # User information
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    # Create all database tables
    db.create_all()

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # The Home page is accessible to anyone
    @app.route('/')
    def home_page():
        # String-based templates
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>Home page</h2>
                <p><a href={{ url_for('user.register') }}>Register</a></p>
                <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>Ingest page</a> (login required)</p>
                <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            {% endblock %}
            """)

    # The Members page is only accessible to authenticated users via the @login_required decorator
    @app.route('/members')
    @login_required    # User must be authenticated
    def member_page():
        # String-based templates
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
            <div class="centered" style="text-align: center">
                <h2>Ingest page</h2>

        <!--        <p><a href={{ url_for('user.register') }}>Register</a></p>
                <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>Ingest page</a> (login required)</p>  -->
                <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            </div>     
            <div class="centered" style="text-align: center">
                  <br><br><br>
                  <p>upload excel files here (.xlsx only)</p>
                  <div class="inline" style="display: inline-block">
                  <form method="POST" enctype="multipart/form-data" action="upload">
                    <div>
                      <input id="upload" type=file  name="product"> product.xlsx 
                    </div>
                    <br/>
                    <div>  
                      <input type=file  name="order_header"> order_header.xlsx 
                    </div>
                    <br/>
                    <div> 
                      <input type=file  name="order_detail"> order_detail.xlsx <br/>
                    </div>
                    <br/>
                    <div>
                      <input type=file  name="customer"> customer.xlsx <br/>
                    </div>
                    <br/>
                    <div> 
                      <input type=file  name="customer_schedule"> customer_schedule.xlsx <br/>
                    </div>
                    <br/>
                      <input type="submit">
                  </form>
            <!--  <div class="text-box">
                  <textarea class="form-control" rows=10  id="xlx_json"></textarea>  
              </div>   
                <script>
                    document.getElementById(\'upload\').addEventListener(\'change\', handleFileSelect, false);

                </script>  -->
                </div>
            </div> 
            {% endblock %}   
            """)
    # product, order_header, order_detail, customer, customer_schedule

    #  return app

    @app.route('/upload', methods=['POST'])
    @login_required
    def upload():
        s3 = boto3.resource('s3')

        s3.Bucket('scf-a894fdf4-9c90-431a-b455-d4244da03a1f').put_object(Key='product.xlsx', Body=request.files['product'])
        s3.Bucket('scf-a894fdf4-9c90-431a-b455-d4244da03a1f').put_object(Key='order_header.xlsx', Body=request.files['order_header'])
        s3.Bucket('scf-a894fdf4-9c90-431a-b455-d4244da03a1f').put_object(Key='order_detail.xlsx', Body=request.files['order_detail'])
        s3.Bucket('scf-a894fdf4-9c90-431a-b455-d4244da03a1f').put_object(Key='customer.xlsx', Body=request.files['customer'])
        s3.Bucket('scf-a894fdf4-9c90-431a-b455-d4244da03a1f').put_object(Key='customer_schedule.xlsx', Body=request.files['customer_schedule'])

        # String-based templates
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                  
                      <div class="centered" style="text-align: center">
                          <div class="inline" style="display: inline-block">                
                            <h1>File saved to s3</h1>
                          </div>    
                      </div>
                  
            {% endblock %}
            """)
    return app    
                                 


# Start development web server
if __name__=='__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

