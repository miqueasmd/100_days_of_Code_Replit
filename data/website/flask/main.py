from flask import Flask, redirect, render_template

app = Flask(__name__, static_url_path="/static")

@app.route('/')
def index():
    return redirect('/portfolio')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/linktree')
def linktree():
    return render_template('linktree.html')

@app.route("/blog/first")
def blog_redirect1():
    return redirect("/first")

@app.route("/blog/second")
def blog_redirect2():
    return redirect("/second")

@app.route('/first')
def first_post():
    context = {
        'title': "Starting My Coding Journey",
        'date': "December 30, 2024",
        'text': "Beginning the 100 Days of Code challenge."
    }
    return render_template('blog.html', **context)

@app.route('/second')
def second_post():
    context = {
        'title': "Project Milestones",
        'date': "December 30, 2024",
        'text': "My progress so far in the challenge."
    }
    return render_template('blog.html', **context)

# Add reflections dictionary
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

@app.route('/reflection/<day>')
def reflection(day):
    if day not in reflections:
        return "Reflection not found", 404
    
    return render_template('reflection.html',
        day=day,
        link=reflections[day]['link'],
        reflection=reflections[day]['reflection']
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)