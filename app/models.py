from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'admin' or 'member'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    decisions = db.relationship('Decision', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Decision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    context = db.Column(db.Text, nullable=False)
    alternatives = db.Column(db.Text)
    chosen_option = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Recorded')  
    # Possible values: Draft, Recorded, Implemented, Under Review, Closed
    tags = db.Column(db.String(200))
    project = db.Column(db.String(100))
    decision_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    outcome = db.relationship('Outcome', backref='decision', uselist=False, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='decision', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Decision {self.title}>'

class Outcome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    decision_id = db.Column(db.Integer, db.ForeignKey('decision.id'), nullable=False)
    result = db.Column(db.String(20))  # Good, Neutral, Bad
    impact = db.Column(db.Text)
    lessons_learned = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    decision_id = db.Column(db.Integer, db.ForeignKey('decision.id'), nullable=False)