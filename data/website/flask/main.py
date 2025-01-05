from flask import Flask, redirect, render_template, request, flash, session
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from functools import wraps
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import shelve
import os
import time

load_dotenv()  # Load environment variables

# Create a Flask application instance
app = Flask(__name__, static_url_path="/static")

app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Get secret key from .env

csrf = CSRFProtect(app)  # Enable CSRF protection

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,     # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)  # Session expires
)

@app.before_request
def before_request():
    session.permanent = True  # Enable session timeout
    if 'username' in session:
        # Add debug prints
        print(f"Current session created time: {session.get('created', 'Not set')}")
        print(f"Current time: {time.time()}")
        
        # Rotate session periodically
        if 'created' not in session:
            session['created'] = time.time()
        elif time.time() - session['created'] > 300:  # Every 5 mins
            # Create new session
            old_data = dict(session)
            session.clear()
            session.update(old_data)
            session['created'] = time.time()
            print("Session rotated")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login first')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Route for the home page, redirects to the portfolio
@app.route('/')
def index():
    return redirect('/portfolio')

# Route for the portfolio page, renders the portfolio.html template
@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

# Route for the linktree page, renders the linktree.html template
@app.route('/linktree')
def linktree():
    return render_template('linktree.html')

# Route for the first blog redirect, redirects to the /first endpoint
@app.route("/blog/first")
def blog_redirect1():
    return redirect("/first")

# Route for the second blog redirect, redirects to the /second endpoint
@app.route("/blog/second")
def blog_redirect2():
    return redirect("/second")

# Route for the first blog post, renders the blog.html template with context
@app.route('/first')
@login_required
def first_post():
    theme = request.args.get('theme', 'default')
    if theme not in THEMES:
        theme = 'default'
        
    post = {
        'title': "Starting My Coding Journey",
        'date': "December 30, 2024",
        'text': "Beginning the 100 Days of Code challenge."
    }
    return render_template('blog.html', post=post, theme=THEMES[theme])

# Route for the second blog post, renders the blog.html template with context
@app.route('/second')
@login_required
def second_post():
    theme = request.args.get('theme', 'default')
    if theme not in THEMES:
        theme = 'default'
        
    post = {
        'title': "Project Milestones",
        'date': "December 30, 2024",
        'text': "My progress so far in the challenge."
    }
    return render_template('blog.html', post=post, theme=THEMES[theme])

# Dictionary to store reflections for specific days
reflections = {
    "73": {
        "link": "https://github.com/miqueasmd/100_days_of_Code_Replit",
        "reflection": "HTML Basic Course - Learning the fundamentals of web development with HTML."
    },
    "74": {
        "link": "https://github.com/miqueasmd/100_days_of_Code_Replit",
        "reflection": "Adding some style - Exploring CSS to make the website visually appealing."
    },
    "75": {
        "link": "https://github.com/miqueasmd/100_days_of_Code_Replit",
        "reflection": "Link Tree - Building a custom link tree page for social media profiles."
    },
    "76": {
        "link": "https://github.com/miqueasmd/100_days_of_Code_Replit",
        "reflection": "Flask 1 - Introduction to Flask web framework and server setup."
    },
    "77": {
        "link": "https://github.com/miqueasmd/100_days_of_Code_Replit",
        "reflection": "Flask 2 - Working with templates and dynamic routing in Flask."
    },
    "78": {
        "link": "https://github.com/miqueasmd/100_days_of_Code_Replit",
        "reflection": "Reflections - Creating a reflection system using Flask routes and templates."
    }
}

# Route for displaying reflections for specific days
@app.route('/reflection/<day>')
def reflection(day):
    if day not in reflections:
        return "Reflection not found", 404  # Return a 404 error if the day is not in the dictionary
    
    return render_template(
        'reflection.html',
        day=day,
        link=reflections[day]['link'],
        reflection=reflections[day]['reflection']
    )

# Dictionary to store valid user credentials
# Load users from environment variables
users = {
    os.getenv('USER1_NAME'): {
        "email": os.getenv('USER1_EMAIL'),
        "password": os.getenv('USER1_PASSWORD')
    },
    os.getenv('USER2_NAME'): {
        "email": os.getenv('USER2_EMAIL'),
        "password": os.getenv('USER2_PASSWORD')
    },
    os.getenv('USER3_NAME'): {
        "email": os.getenv('USER3_EMAIL'),
        "password": os.getenv('USER3_PASSWORD')
    }
}

# Define the login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username is required.")])
    email = StringField('Email', validators=[DataRequired(message="Email is required."), Email(message="Invalid email format.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])
    submit = SubmitField('Login')

# Route for displaying the login form
@app.route('/form', methods=['GET', 'POST'])
def show_form():
    form = LoginForm()  # Create an instance of the form
    if form.validate_on_submit():  # Check if the form is submitted and valid
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Handle login logic here...
        if username in users:
            user = users[username]
            if user['email'] == email and user['password'] == password:
                session['username'] = username  # Store username in session
                flash('Login successful!', 'success')  # Flash success message
                return render_template('success.html', username=username)  # Render the success page
            else:
                flash('Invalid email or password.', 'error')
                return render_template('error.html')  # Redirect to error page
        else:
            flash('Username not found.', 'error')
            return render_template('error.html')  # Redirect to error page

    return render_template('form.html', form=form)  # Pass the form to the template
    
# Route for displaying the robot identification form
@app.route('/not_robot')
def show_robot_form():
    # Render the 'not_robot.html' form template
    return render_template('not_robot.html')

# Route for handling the robot identification form submission
@app.route("/robot", methods=["POST"])
def robot():
    try:
        # Check answers to the robot-identification questions
        if request.form['metal'] == "Yes":  # Check if "metal" question is "Yes"
            flash("You're a robot!")  # Flash message for robot detection
        elif "error" in request.form["infinity"].lower():  # Check for specific keyword in the text input
            flash("You're a robot!")  # Flash message for robot detection
        elif request.form["food"] == "synthetic oil":  # Check dropdown selection for robot food
            flash("You're a robot!")  # Flash message for robot detection
        else:
            flash("Welcome, human!")  # Flash message for valid human detection
    except:
        # Handle any unexpected errors during the form submission
        flash("An error occurred")  # Flash general error message
    return redirect('/not_robot')  # Redirect back to the 'not_robot.html' form

# Define supported languages
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'ru': 'Russian',
    'ja': 'Japanese'
}

# Default content in English
DEFAULT_CONTENT = {
    'title': 'Welcome to our Website',
    'subtitle': 'Choose your language',
    'content': 'This is a multilingual website using dynamic translation.'
}

@app.route('/multilingual')
def multilingual():
    lang = request.args.get('lang', 'en')
    
    if lang not in LANGUAGES:
        flash('Language not supported')
        return redirect('/multilingual?lang=en')
        
    try:
        if lang != 'en':
            translator = GoogleTranslator(source='en', target=lang)
            content = {
                'title': translator.translate(DEFAULT_CONTENT['title']),
                'subtitle': translator.translate(DEFAULT_CONTENT['subtitle']),
                'content': translator.translate(DEFAULT_CONTENT['content'])
            }
        else:
            content = DEFAULT_CONTENT
            
        return render_template('multilingual.html', 
                             content=content, 
                             languages=LANGUAGES,
                             current_lang=lang)
    except Exception as e:
        flash(f'Translation error: {str(e)}')
        return redirect('/multilingual?lang=en')
    
# Theme definitions
THEMES = {
    'default': {
        'background': '#1c2333',
        'text': '#ffffff',
        'accent': '#4a9eff'
    },
    'light': {
        'background': '#e6f6ee',    # Softer pastel green background
        'text': '#ffffff',          # White text
        'accent': '#179c5d',        # Darker greeb accent
        'link': '#179c5d'           # Dark green links
    },
    'dark': {
        'background': '#000000',
        'text': '#00ff00',
        'accent': '#ff00ff'
    }
}

@app.route('/blog/<post>', methods=['GET'])
@login_required
def blog(post):
    theme = request.args.get('theme', 'default')
    if theme not in THEMES:
        theme = 'default'
        
    posts = {
        'hello': {
            'title': 'Hello World',
            'date': 'October 25th',
            'text': 'Here is my first blog entry.'
        },
        'bye': {
            'title': 'Bye World',
            'date': 'October 25th',
            'text': 'Here is my last blog entry.'
        }
    }
    
    if post not in posts:
        return "Post not found", 404
        
    return render_template('blog.html', 
                         post=posts[post],
                         theme=THEMES[theme])

# User authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Store next URL if coming from somewhere
    if request.method == 'GET':
        next_url = request.args.get('next') or request.referrer
        if next_url:
            session['next'] = next_url

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        with shelve.open('static/db/users') as db:
            if username in db and db[username]['password'] == password:
                session['username'] = username
                # Redirect to stored URL or default to blog
                next_url = session.pop('next', '/blog')
                flash(f"Welcome back {db[username]['name']}!")
                return redirect(next_url)
            else:
                flash('Invalid username or password')
                return redirect('/login')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    session.clear()  # Clear session when accessing login

    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            name = request.form.get('name')
            
            with shelve.open('static/db/users') as db:
                print(f"Current users before signup: {list(db.keys())}")  # Debug info
                if username in db:
                    flash('Username already exists')
                    return redirect('/signup')
                
                db[username] = {
                    'name': name,
                    'password': password
                }
                print(f"User added: {username}")  # Debug info
                flash('Account created successfully!')
                return redirect('/login')
    except Exception as e:
        print(f"Signup error: {str(e)}")  # Debug info
        flash('An error occurred during signup')
        return redirect('/signup')
    
    return render_template('signup.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    session.clear()  # Clear session when accessing login
    
    if request.method == 'POST':
        username = request.form.get('username')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        with shelve.open('static/db/users', writeback=True) as db:  # Added writeback=True
            print(f"Attempting password change for user: {username}")
            print(f"Current users in db: {list(db.keys())}")
            
            if username in db and db[username]['password'] == old_password:
                # Update password
                db[username]['password'] = new_password
                print(f"Old password: {old_password}")
                print(f"New password: {new_password}")
                
                # Verify update
                print(f"Updated user data: {db[username]}")
                
                # Force write
                db.sync()
                
                flash('Password changed successfully!')
                return redirect('/login')  # Redirect to login instead of portfolio
            else:
                print(f"Authentication failed for user: {username}")
                flash('Invalid credentials')
                return redirect('/change_password')
    
    return render_template('change_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect('/login')

@app.route('/blog')
def blog_list():
    with shelve.open('static/db/posts') as db:
        posts = []
        for key in reversed(sorted(db.keys())):
            post = db[key]
            # Only show posts if user is author
            if session.get('username') == post.get('author'):
                post['id'] = key
                posts.append(post)
    return render_template('blog_list.html', posts=posts)

@app.route('/blog/<post_id>')
def blog_single(post_id):
    try:
        with shelve.open('static/db/posts', writeback=True) as db:
            print(f"Available post IDs: {list(db.keys())}")  # Debug
            print(f"Requested post ID: {post_id}")  # Debug
            
            if post_id in db:
                post = db[post_id]
                if session.get('username') == post.get('author'):
                    post['id'] = post_id
                    return render_template('blog_single.html', post=post)
                
            flash('Post not found or unauthorized')
            print("Post not found or unauthorized")  # Debug
    except Exception as e:
        print(f"Error viewing post: {str(e)}")
        flash('Error accessing post')
    return redirect('/blog')

@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def blog_new():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        post_id = str(time.time())
        
        with shelve.open('static/db/posts', writeback=True) as db:
            db[post_id] = {
                'title': title,
                'body': body,
                'date': time.strftime('%Y-%m-%d'),
                'author': session['username']
            }
        return redirect('/blog')

    return render_template('blog_edit.html')

@app.route('/blog/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def blog_edit(post_id):
    try:
        with shelve.open('static/db/posts', writeback=True) as db:
            if post_id not in db:
                flash('Post not found')
                return redirect('/blog')
                
            post = db[post_id]
            if post['author'] != session['username']:
                flash('Unauthorized access')
                return redirect('/blog')
                
            if request.method == 'POST':
                db[post_id].update({
                    'title': request.form.get('title'),
                    'body': request.form.get('body'),
                    'date': time.strftime('%Y-%m-%d'),
                    'edited': True
                })
                db.sync()
                flash('Post updated successfully')
                return redirect('/blog')
            
            post['id'] = post_id
            return render_template('blog_edit.html', post=post)
    except Exception as e:
        print(f"Error editing post: {str(e)}")
        flash('Error accessing post')
        return redirect('/blog')

@app.route('/blog/delete/<post_id>', methods=['POST'])
@login_required
def blog_delete(post_id):
    with shelve.open('static/db/posts', writeback=True) as db:
        if post_id in db:
            del db[post_id]
            flash('Post deleted successfully')
    return redirect('/blog')

# Start the Flask application
if __name__ == '__main__':
    # Run the Flask application with debug mode enabled for development
    app.run(host='0.0.0.0', port=81, debug=True)
