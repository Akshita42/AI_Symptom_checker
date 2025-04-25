# AI Symptom Checker

An AI-powered symptom checker that helps users understand potential medical conditions based on their symptoms. This tool uses OpenAI's GPT model to analyze symptoms and provide informative responses.

## Important Disclaimer

This application is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

## Features

- Input age and gender information
- Describe symptoms in natural language
- Get AI-powered analysis of potential conditions
- Receive severity assessments and general recommendations
- Medical disclaimers and professional consultation reminders
- Modern, responsive web interface

## Tech Stack

- Backend: Flask (Python)
- Frontend: HTML5, CSS3, JavaScript
- AI: OpenAI GPT-3.5 Turbo
- Styling: Bootstrap 5

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your configuration:
   ```
   OPENAI_API_KEY=your_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here  # Optional: for session security
   ```

## Running the Application

To run the application, use the following command:
```bash
python app.py
```

The application will start on `http://localhost:5000` by default.

## Project Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── css/          # CSS styles
│   │   └── style.css
│   └── js/           # JavaScript files
│       └── main.js
└── templates/         # HTML templates
    └── index.html
```

## Security and Privacy

- This application does not store any personal health information
- All communications with the OpenAI API are encrypted
- User data is not persisted between sessions
- HTTPS recommended for production deployment

## Development

To run the application in development mode:
```bash
export FLASK_ENV=development
python app.py
```

## Production Deployment

For production deployment:
1. Use a production-grade WSGI server (e.g., Gunicorn)
2. Enable HTTPS
3. Set up proper security headers
4. Use environment variables for sensitive data

## Support

For issues and feature requests, please open an issue in the repository. 