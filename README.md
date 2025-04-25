# AI Symptom Checker

# 🧠 AI Symptom Checker — DR. AI 🤖

**DR. AI** # AI Symptom Checker 🏥

An intelligent web-based medical symptom checker powered by Google's Gemini AI that provides preliminary health assessments and medical guidance.

## Features 🌟

- **Smart Symptom Analysis**: Powered by Google's Gemini AI model
- **User Authentication**: Secure login and registration system
- **Personal Health Dashboard**: Track your consultation history
- **Follow-up System**: Track your health progress
- **Age-Specific Analysis**: Tailored recommendations based on age and gender

## Tech Stack 💻

- **Backend**: Flask (Python)
- **Database**: SQLite
- **AI Model**: Google Gemini AI
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: Werkzeug Security for password hashing

## Prerequisites 📋

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key

## Installation 🚀

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-symptom-checker.git
   cd ai-symptom-checker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```env
   FLASK_SECRET_KEY=your_secret_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Running the Application 🏃‍♂️

1. Start the development server:
   ```bash
   python app.py
   ```

2. Access the application at `http://localhost:5000`

## Project Structure 📁

```
.
├── app.py              # Main Flask application
├── database.py         # Database models and configuration
├── static/            # Static files
│   ├── css/          # CSS styles
│   │   └── style.css
│   └── js/           # JavaScript files
│       └── main.js
└── templates/         # HTML templates
    └── index.html
```

## Security Measures 🔒

- Secure password hashing using Werkzeug
- Protected routes with Flask-Login
- Session management
- Environment variable configuration
- No storage of sensitive medical data

## Features in Detail 📝

### Symptom Analysis
- Input your age, gender, and symptoms
- Receive AI-powered preliminary assessment
- Get age-appropriate medical recommendations
- Follow-up questions for better accuracy

### User Dashboard
- View consultation history
- Access Smart Symptom Analysis

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



## Acknowledgments 👏

- Google Gemini AI for powering the symptom analysis
- Flask framework and its community
- All contributors and users of this project

## Disclaimer ⚠️

This application is for informational purposes only and should not be considered as professional medical advice. Always consult with a qualified healthcare provider for medical diagnosis and treatment.

---
Made with ❤️ by [Akshita Dhaka and Adity Senger] 
