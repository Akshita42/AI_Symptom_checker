from app import app, db

with app.app_context():
    db.drop_all()  # This will remove any existing tables
    db.create_all()  # This will create new tables
    print("Database created successfully!")
