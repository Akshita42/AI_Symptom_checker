from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
        
    user = User(
        name=data['name'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Registration successful"})

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({"message": "Login successful"})
    
    return jsonify({"error": "Invalid email or password"}), 401

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

@auth.route('/profile')
@login_required
def profile():
    return jsonify({
        "name": current_user.name,
        "email": current_user.email
    }) 