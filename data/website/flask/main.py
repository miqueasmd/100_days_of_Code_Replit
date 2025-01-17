from flask import Flask, redirect, render_template, request, flash, session
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta, datetime
from functools import wraps
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
import shelve
import os
import time
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()  # Load environment variables

# Create a Flask application instance
app = Flask(__name__, static_url_path="/static")

socketio = SocketIO(app)

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

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_profile', methods=['POST'])
@login_required
def upload_profile():
    if 'profile_pic' not in request.files:
        flash('No file selected')
        return redirect('/dashboard')
        
    file = request.files['profile_pic']
    if file and allowed_file(file.filename):
        filename = f"{session['username']}_{secure_filename(file.filename)}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        with shelve.open('static/db/users', writeback=True) as db:
            db[session['username']]['profile_pic'] = filename
            session['profile_pic'] = filename  # Update session with the new profile picture
            db.sync()
    else:
        flash('Invalid file type. Please upload a PNG, JPG, JPEG, or GIF image.')
    
    return redirect('/dashboard')

# Route for the home page, redirects to the portfolio
@app.route('/')
def index():
    return redirect('/dashboard')

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
#@login_required
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
#@login_required
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

@app.route('/reflection/goto', methods=['POST'])
def goto_reflection():
    day = request.form.get('day')
    if not day or int(day) < 73 or int(day) > 78:
        flash('Invalid day selected')
        return redirect('/reflection/73')
    return redirect(f'/reflection/{day}')

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
#@login_required
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
    session.clear()  # Clear session when accessing login
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            with shelve.open('static/db/users', writeback=True) as db:
                if username in db and db[username]['password'] == password:
                    session['username'] = username
                    if 'profile_pic' in db[username]:  # Add profile pic to session
                        session['profile_pic'] = db[username]['profile_pic']
                    db.sync()
                    flash(f"Welcome back {username}!")
                    return redirect('/dashboard')
                else:
                    flash('Invalid username or password')
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('Login error occurred')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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

@app.route('/chatroom', methods=['GET', 'POST'])
@login_required
def chatroom():
    limit = request.args.get('limit', default=5, type=int)  # Get limit from query parameters
    offset = request.args.get('offset', default=0, type=int)  # Get offset from query parameters
    messages, more_messages = get_messages(limit, offset)  # Fetch messages
    return render_template('chatroom.html', messages=messages, more_messages=more_messages)  # Pass messages and flag to the template

"""
This function is currently commented out and not in use.
It handles sending messages via POST requests.

@app.route('/send_message', methods=['POST'])  # Ensure this route is defined
@login_required
def send_message():
    message = request.form.get('message')
    if not message:
        flash('Message cannot be empty.')
        return redirect('/chatroom')

    now = datetime.now()
    timestamp = str(time.time())

    with shelve.open('static/db/chat') as db:
        db[timestamp] = {
            'id': timestamp,
            'username': session['username'],
            'content': message,
            'profile_pic': session.get('profile_pic', 'default_profile.png'),
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
        }

    return redirect('/chatroom')  # Redirect back to the chat room
"""
@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    if not message:
        return  # Optionally handle empty messages

    now = datetime.now()
    timestamp = str(time.time())

    with shelve.open('static/db/chat') as db:
        db[timestamp] = {
            'id': timestamp,  # Store the message ID
            'username': session['username'],
            'content': message,
            'profile_pic': session.get('profile_pic', 'default_profile.png'),
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
        }

    # Broadcast the message to all clients
    emit('receive_message', {
        'id': timestamp,  # Include the message ID in the emitted data
        'username': session['username'],
        'content': message,
        'profile_pic': session.get('profile_pic', 'default_profile.png'),
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)

def get_messages(limit=5, offset=0):
    current_time = datetime.now()
    messages = []
    more_messages = False

    with shelve.open('static/db/chat') as db:
        keys = sorted(db.keys(), reverse=True)  # Get all keys in reverse order
        if offset < len(keys):
            more_messages = True  # There are more messages to load
            for key in keys[offset:offset + limit]:  # Get messages based on offset and limit
                message = db[key]
                if 'timestamp' in message:
                    time_diff = current_time - datetime.strptime(message['timestamp'], '%Y-%m-%d %H:%M:%S')
                    seconds = time_diff.total_seconds()
                    
                    if seconds < 60:
                        message['time_ago'] = 'Just now'
                    elif seconds < 3600:
                        minutes = int(seconds / 60)
                        message['time_ago'] = f'{minutes} minute{"s" if minutes != 1 else ""} ago'
                    elif seconds < 86400:
                        hours = int(seconds / 3600)
                        message['time_ago'] = f'{hours} hour{"s" if hours != 1 else ""} ago'
                    else:
                        days = time_diff.days
                        message['time_ago'] = f'{days} day{"s" if days != 1 else ""} ago'
                messages.append(message)

    # Sort messages from oldest to newest
    messages.sort(key=lambda x: x['timestamp'])  # Assuming 'timestamp' is a string in a sortable format

    return messages, more_messages

@app.route('/delete_message/<message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    with shelve.open('static/db/chat') as db:
        if message_id in db:
            del db[message_id]  # Remove the message from the database
            flash('Message deleted successfully.')
        else:
            flash('Message not found.')
    return redirect('/chatroom')  # Redirect back to the chat room

@app.route('/inspect_chat')
def inspect_chat():
    with shelve.open('static/db/chat') as db:
        messages = {key: db[key] for key in db.keys()}
    return str(messages)  # Display the messages for inspection


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

COUNTRIES = {
    'US': 'United States',
    'GB': 'United Kingdom',
    'ES': 'Spain',
    'FR': 'France',
    'DE': 'Germany',
    'IT': 'Italy',
    'BR': 'Brazil',
    'MX': 'Mexico',
    'JP': 'Japan',
    'AU': 'Australia'
}

def get_spotify_token():
    """Get Spotify access token"""
    try:
        # Update environment variable names to match .env file
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("Missing Spotify credentials")
            raise ValueError("Spotify credentials not found")

        logger.debug("Attempting Spotify authentication...")
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=HTTPBasicAuth(client_id, client_secret)
        )
        
        if response.status_code != 200:
            logger.error(f"Auth failed: {response.status_code}")
            raise ValueError("Authentication failed")
            
        token = response.json()["access_token"]
        logger.debug("Successfully obtained Spotify token")
        return token
        
    except Exception as e:
        logger.exception("Token generation failed")
        raise

def get_spotify_tracks(year, market='ES', token=None, offset=0, limit=10):
    """
    Fetch and sort tracks from Spotify API by popularity.
    
    Args:
        year (str): Year to search for tracks
        market (str): Two-letter country code (default: 'ES')
        token (str): Spotify API token
        offset (int): Starting point for pagination
        limit (int): Number of tracks to return
    
    Returns:
        dict: JSON response with sorted tracks by popularity
    """
    if not token:
        token = get_spotify_token()
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get tracks from Spotify API
    params = {
        'q': f'year:{year}',
        'type': 'track',
        'market': market,
        'limit': 50  # Get more tracks to sort
    }
    
    logger.debug(f"Fetching tracks with params: {params}")
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    
    if response.status_code != 200:
        logger.error(f"API failed: {response.status_code}")
        raise ValueError("API request failed")
    
    data = response.json()
    if 'tracks' in data and 'items' in data['tracks']:
        tracks = data['tracks']['items']
        
        # Filter out duplicates by track ID
        unique_tracks = {track['id']: track for track in tracks}.values()
        
        # Sort by popularity
        sorted_tracks = sorted(unique_tracks, key=lambda x: x.get('popularity', 0), reverse=True)
        
        # Get slice based on offset and limit
        start = offset
        end = offset + limit
        selected_tracks = sorted_tracks[start:end]
        
        # Log selected tracks
        logger.debug(f"Selected tracks ({market}):")
        for idx, track in enumerate(selected_tracks, 1):
            logger.debug(f"{idx}. {track['name']} ({track['popularity']}) - {track['id']}")
        
        data['tracks']['items'] = selected_tracks
    
    return data

@app.route('/music', methods=['GET', 'POST'])
def music():

    """
    Handle music search page requests.
    
    GET: Display empty search form
    POST: Process form submission and display results
    
    Form parameters:
    - year: Year to search (1900-2024)
    - market: Two-letter country code
    - limit: Number of songs to display
    """
        
    if request.method == 'POST':
        year = request.form.get('year', '2024')
        market = request.form.get('market', 'ES')  # Get market from form
        limit = int(request.form.get('limit', 10))
        logger.debug(f"Search params - Year: {year}, Market: {market}, Limit: {limit}")

        try:
            token = get_spotify_token()
            data = get_spotify_tracks(year, market=market, token=token, limit=limit)
            
            songs_html = ""
            for idx, track in enumerate(data['tracks']['items'], 1):
                # Add embed URL to track data
                track['embed_url'] = f"https://open.spotify.com/embed/track/{track['id']}"
                
                song_html = render_template('song_template.html',
                    rank=idx,
                    name=track['name'],
                    artist=track['artists'][0]['name'],
                    album=track['album']['name'],
                    release_date=track['album']['release_date'],
                    popularity=track.get('popularity', 'N/A'),
                    embed_url=track['embed_url']
                )
                songs_html += song_html

            return render_template('music.html', 
                                   songs=songs_html, 
                                   value=year, 
                                   selected_market=market,
                                   selected_limit=limit,  # Pass selected limit to template
                                   countries=COUNTRIES)
                                
        except Exception as e:
            logger.exception("Error processing request")
            flash(str(e))
            return render_template('music.html', 
                                   songs="", 
                                   value=year, 
                                   selected_market=market,
                                   selected_limit=limit,
                                   countries=COUNTRIES)
    
    return render_template('music.html', 
                           songs="", 
                           value="2024", 
                           selected_market="ES",
                           selected_limit=10,
                           countries=COUNTRIES)


@app.route('/load_more', methods=['POST'])
def load_more_songs():

    """
    Handle AJAX requests for loading additional songs.
    
    Form parameters:
    - year: Current year selection
    - market: Current country selection
    - offset: Number of songs already loaded
    - limit: Number of additional songs to load
    """
        
    year = request.form.get('year')
    market = request.form.get('market', 'ES')  # Get market from form data
    offset = int(request.form.get('offset', 0))
    limit = int(request.form.get('limit', 10))
    
    logger.debug(f"Load more - Year: {year}, Market: {market}, Offset: {offset}, Limit: {limit}")
    
    token = get_spotify_token()
    data = get_spotify_tracks(year, market=market, token=token, offset=offset, limit=limit)
    
    songs_html = ""
    for idx, track in enumerate(data['tracks']['items'], offset + 1):
        track['embed_url'] = f"https://open.spotify.com/embed/track/{track['id']}"
        song_html = render_template('song_template.html',
            rank=idx,
            name=track['name'],
            artist=track['artists'][0]['name'],
            album=track['album']['name'],
            release_date=track['album']['release_date'],
            popularity=track.get('popularity', 'N/A'),
            embed_url=track['embed_url']
        )
        songs_html += song_html
    return songs_html

# Start the Flask application
if __name__ == '__main__':
    # Run the Flask application with debug mode enabled for development
    # app.run(host='0.0.0.0', port=81, debug=True) #without socketio
    socketio.run(app, host='0.0.0.0', port=81, debug=True)
