from flask import render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models.emotion_model import predict, train_model
from app.models.models import EmotionEntry, User
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

def register_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered. Please log in or use a different email.')
                return redirect(url_for('register'))
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                flash('Login successful!')
                return redirect(url_for('profile'))
            flash('Invalid username or password.')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out.')
        return redirect(url_for('home'))

    @app.route('/profile')
    def profile():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_id = session['user_id']
        user = User.query.get(user_id)
        entries = EmotionEntry.query.filter_by(user_id=user_id).order_by(EmotionEntry.timestamp.desc()).all()
        return render_template('profile.html', user=user, entries=entries)

    @app.route('/update_profile', methods=['GET', 'POST'])
    def update_profile():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_id = session['user_id']
        user = User.query.get(user_id)
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            db.session.commit()
            flash('Profile updated successfully.')
            return redirect(url_for('profile'))
        return render_template('update_profile.html', user=user)

    @app.route('/analyze_emotion', methods=['POST'])
    def analyze_emotion():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_id = session['user_id']
        emotion_text = request.form['emotion']
        emotion_result = predict(emotion_text)
        print(f"Text: {emotion_text}, Prediction: {emotion_result}")  # Debugging info
        new_entry = EmotionEntry(text=emotion_text, emotion=emotion_result, user_id=user_id)
        db.session.add(new_entry)
        db.session.commit()
        flash('Emotion recorded successfully!')
        return redirect(url_for('profile'))

    @app.route('/train_model')
    def train_model_route():
        train_model()
        return "Model training complete"

    @app.route('/emotion_tracking')
    def emotion_tracking():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_id = session['user_id']
        entries = EmotionEntry.query.filter_by(user_id=user_id).order_by(EmotionEntry.timestamp.desc()).all()
        return render_template('emotion_tracking.html', entries=entries)

    @app.route('/recommendations')
    def recommendations():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_id = session['user_id']
        entries = EmotionEntry.query.filter_by(user_id=user_id).order_by(EmotionEntry.timestamp.desc()).limit(5).all()

        # Debugging: Print entries to console
        for entry in entries:
            print(f"Entry Text: {entry.text}, Entry Emotion: {entry.emotion}")

        # Analyze emotions
        emotion_counts = {}
        for entry in entries:
            emotion = entry.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            print(f"Emotion: {emotion}, Count: {emotion_counts[emotion]}")  # Debugging info

        # Determine predominant emotion
        if emotion_counts:
            predominant_emotion = max(emotion_counts, key=emotion_counts.get)
            recommendations = get_recommendations_for_emotion(predominant_emotion)
            print(f"Predominant Emotion: {predominant_emotion}")  # Debugging info
            print(f"Recommendations: {recommendations}")  # Debugging info
        else:
            recommendations = ["Start tracking your emotions to receive personalized recommendations!"]

        print(f"Final Recommendations: {recommendations}")  # Final Debugging info before rendering

        return render_template('recommendations.html', recommendations=recommendations)

    def get_recommendations_for_emotion(emotion):
        recommendations_dict = {
            'happy': [
                "Keep up the great mood! Consider sharing your happiness with someone today.",
                "Maintain your positive outlook by practicing gratitude."
            ],
            'sad': [
                "It might help to talk to a friend or family member about how you're feeling.",
                "Engage in an activity you enjoy to lift your spirits."
            ],
            'anxious': [
                "Try a deep-breathing exercise to calm your mind.",
                "Consider practicing mindfulness meditation."
            ],
            # Add more emotions and recommendations as needed
        }
        return recommendations_dict.get(emotion, ["Explore our resources to support your well-being."])

    @app.route('/crisis_support')
    def crisis_support():
        return render_template('crisis_support.html')

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            email = request.form['email']
            user = User.query.filter_by(email=email).first()
            if user:
                flash('A password reset link has been sent to your email.')
                # Implement password reset email sending functionality here
            else:
                flash('No account found with that email.')
        return render_template('forgot_password.html')

    def send_reminder_email():
        # Placeholder function if you want to keep the email reminder functionality in the future.
        pass

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_reminder_email, trigger="interval", hours=24)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())
