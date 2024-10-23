from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Quiz result model
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Dashboard route (after login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Quiz route
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    questions = [
        {"question": "What is the default port for HTTP?", "options": ["80", "443", "22", "25"], "answer": "80"},
        {"question": "Which of the following is a phishing attack?", "options": ["Email Spoofing", "SQL Injection", "XSS", "DDoS"], "answer": "Email Spoofing"}
    ]
    
    if request.method == 'POST':
        score = 0
        for i in range(len(questions)):
            user_answer = request.form.get(f'answer{i}')
            if user_answer == questions[i]['answer']:
                score += 1

        # Save quiz result
        if 'user_id' in session:
            new_result = QuizResult(user_id=session['user_id'], score=score)
            db.session.add(new_result)
            db.session.commit()
        return render_template('result.html', score=score, total=len(questions))
    
    return render_template('quiz.html', questions=questions)

# Leaderboard route
@app.route('/leaderboard')
def leaderboard():
    results = QuizResult.query.order_by(QuizResult.score.desc()).limit(10).all()
    return render_template('leaderboard.html', results=results)

if __name__ == '__main__':
    with app.app_context():  # Ensure we are in an app context
        db.create_all()  # This creates the database if it doesn't exist
    app.run(debug=True)

