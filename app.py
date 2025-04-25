from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
from database import db, User, Consultation, Reminder, HealthTip
from pdf_generator import generate_consultation_report
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symptom_checker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # Changed to login_page

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def analyze_symptoms(age, gender, symptoms):
    """Analyze symptoms using Google's Gemini model"""
    try:
        # Add age validation in the function as well
        if age <= 0 or age > 150:
            return {
                "success": False,
                "error": "Invalid age value"
            }

        prompt = f"""You are DR. AI, a medical AI assistant. You MUST follow these rules strictly:

1. ONLY respond to medical and health-related queries
2. Consider the patient's age ({age} years) when providing advice
3. Always identify yourself as DR. AI
4. If a question is not related to health or medicine, respond with:
   "I'm DR. AI, and I can only assist with medical and health-related questions. Please ask me about symptoms, health concerns, or medical advice."

Current Patient Information:
Age: {age} years
Gender: {gender}
Symptoms: {symptoms}

Provide your initial response following this format:

👋 Start with "Hello, I'm DR. AI" and acknowledge their symptoms.

🏥 INITIAL ASSESSMENT:
• Provide brief initial thoughts
• Mention 1-2 most likely conditions
• Consider age-specific conditions and risks

❓ FOLLOW-UP QUESTIONS:
• Ask 2-3 specific questions about their symptoms
• Include age-relevant questions if needed

💊 IMMEDIATE RECOMMENDATIONS:
• Provide 2-3 immediate steps they can take
• Ensure recommendations are age-appropriate

⚕️ MEDICAL DISCLAIMER:
End with: "I'm DR. AI, and this is an AI-based preliminary assessment. For accurate diagnosis and treatment, please consult with a healthcare provider."
"""

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000
            }
        }

        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            analysis = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "success": True,
                "analysis": analysis
            }
        else:
            return {
                "success": False,
                "error": f"API request failed with status code {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/')
def welcome():
    """Render the welcome page first"""
    return render_template('welcome.html')

@app.route('/login_page')
def login_page():
    """Render the login page"""
    return render_template('login.html')

@app.route('/register_page')
def register_page():
    """Render the registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Render the chatbot dashboard"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login requests"""
    data = request.get_json()
    logger.debug(f"Login attempt for email: {data.get('email')}")
    
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        login_user(user)
        logger.debug("Login successful")
        return jsonify({"success": True, "redirect": url_for('dashboard')})
    
    logger.debug("Login failed")
    return jsonify({"success": False, "error": "Invalid email or password"}), 401

@app.route('/register', methods=['POST'])
def register():
    """Handle registration requests"""
    try:
        data = request.get_json()
        logger.debug(f"Registration attempt for email: {data.get('email')}")
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"success": False, "error": "Email already registered"}), 400
        
        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        logger.debug("Registration successful")
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    """Handle logout requests"""
    logout_user()
    return redirect(url_for('welcome'))

@app.route('/profile')
@login_required
def get_profile():
    """Get user profile information"""
    try:
        return jsonify({
            "success": True,
            "profile": {
                "name": current_user.name,
                "email": current_user.email
            }
        })
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Handle symptom analysis requests"""
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug print
        
        if not all(field in data for field in ['age', 'gender', 'symptoms']):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400

        # Age validation
        try:
            age = int(data['age'])
            if age <= 0 or age > 150:
                return jsonify({
                    "success": False,
                    "error": "Age must be between 1 and 150 years"
                }), 400
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid age value"
            }), 400

        # Analyze symptoms
        result = analyze_symptoms(
            age=age,
            gender=data['gender'],
            symptoms=data['symptoms']
        )
        print("Analysis result:", result)  # Debug print

        if result.get("success"):
            # Create new consultation record
            consultation = Consultation(
                user_id=current_user.id,
                age=age,
                gender=data['gender'],
                symptoms=data['symptoms'],
                analysis=result['analysis']
            )
            db.session.add(consultation)
            db.session.commit()

            return jsonify({
                "success": True,
                "response": result['analysis'],
                "consultation_id": consultation.id
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Analysis failed")
            }), 500

    except Exception as e:
        print("Error:", str(e))  # Debug print
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/history')
@login_required
def get_history():
    """Get user's consultation history"""
    try:
        print("Fetching history for user:", current_user.id)  # Debug print
        consultations = Consultation.query.filter_by(user_id=current_user.id)\
            .order_by(Consultation.created_at.desc()).all()
        
        history = []
        for c in consultations:
            try:
                history.append({
                    'id': c.id,
                    'age': c.age,
                    'gender': c.gender,
                    'symptoms': c.symptoms,
                    'created_at': c.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                print(f"Error processing consultation {c.id}:", str(e))
                continue
        
        print("Found consultations:", len(history))  # Debug print
        return jsonify({
            "success": True,
            "history": history
        })
    except Exception as e:
        print(f"History error: {str(e)}")  # Debug print
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate_report/<int:consultation_id>')
@login_required
def generate_report(consultation_id):
    """Generate PDF report for a consultation"""
    consultation = Consultation.query.get_or_404(consultation_id)
    if consultation.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        filename = generate_consultation_report(consultation, tmp.name)
        return send_file(
            filename,
            as_attachment=True,
            download_name=f'medical_report_{consultation.created_at.strftime("%Y%m%d")}.pdf'
        )

@app.route('/health_tips')
def get_health_tips():
    """Get health tips"""
    tips = HealthTip.query.order_by(HealthTip.created_at.desc()).limit(5).all()
    return jsonify([{
        'title': tip.title,
        'content': tip.content
    } for tip in tips])

@app.route('/reminders', methods=['GET', 'POST'])
@login_required
def manage_reminders():
    """Manage reminders"""
    if request.method == 'GET':
        reminders = Reminder.query.filter_by(
            user_id=current_user.id,
            completed=False
        ).order_by(Reminder.due_date).all()
        
        return jsonify([{
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'type': r.type,
            'due_date': r.due_date.isoformat()
        } for r in reminders])
    
    else:  # POST
        data = request.get_json()
        reminder = Reminder(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description', ''),
            type=data['type'],
            due_date=datetime.fromisoformat(data['due_date'])
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        return jsonify({"success": True})

@app.route('/follow_up', methods=['POST'])
@login_required
def follow_up():
    try:
        data = request.get_json()
        message = data.get('message')
        consultation_id = data.get('consultation_id')
        
        if not message or not consultation_id:
            return jsonify({"success": False, "error": "Missing message or consultation ID"}), 400

        # Get the existing consultation
        consultation = Consultation.query.get(consultation_id)
        if not consultation:
            return jsonify({"success": False, "error": "Consultation not found"}), 404

        # Build context from previous conversation
        context = f"""You are DR. AI, a medical symptom analysis chatbot. You MUST follow these rules strictly:

1. ONLY respond to medical and health-related queries
2. If the user asks about non-medical topics, respond with:
   "I apologize, but I can only assist with medical and health-related questions. Please ask me about symptoms, health concerns, or medical advice."
3. Never answer questions about non-medical topics

Previous consultation context:
Age: {consultation.age}
Gender: {consultation.gender}
Initial symptoms: {consultation.symptoms}
Previous conversation: {consultation.analysis}

User's new message: "{message}"

If the question is medical/health-related:
1. Provide a clear, informative response
2. Maintain conversation context
3. Give actionable medical advice when appropriate
4. Use emojis for engagement
5. Stay professional while being friendly
6. Add relevant medical disclaimers when needed

If the question is NOT medical/health-related:
Respond ONLY with: "I apologize, but I can only assist with medical and health-related questions. Please ask me about symptoms, health concerns, or medical advice."

Remember to format responses with appropriate sections (e.g., 🏥 ASSESSMENT, 💊 RECOMMENDATIONS) when providing medical advice."""

        # Make API call to Gemini
        payload = {
            "contents": [{
                "parts": [{
                    "text": context
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000
            }
        }

        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Update consultation with the new interaction
            consultation.analysis += f"\n\nUser: {message}\nDR. AI: {ai_response}"
            db.session.commit()

            return jsonify({
                "success": True,
                "response": ai_response
            })
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return jsonify({
                "success": False,
                "error": f"API request failed with status code {response.status_code}"
            }), 500

    except Exception as e:
        print(f"Follow-up error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/consultation/<int:consultation_id>', methods=['GET', 'DELETE'])
@login_required
def manage_consultation(consultation_id):
    """Manage individual consultations"""
    try:
        consultation = Consultation.query.get_or_404(consultation_id)
        
        if consultation.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        if request.method == 'DELETE':
            db.session.delete(consultation)
            db.session.commit()
            return jsonify({"success": True})

        return jsonify({
            "success": True,
            "consultation": {
                "id": consultation.id,
                "age": consultation.age,
                "gender": consultation.gender,
                "symptoms": consultation.symptoms,
                "initial_response": consultation.analysis,
                "created_at": consultation.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        print(f"Consultation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)