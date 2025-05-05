from app import db, User, app  # Import 'app' from your Flask application

def add_synthetic_user():
    with app.app_context():  # Create application context
        synthetic_user = User(
            username="testuser",
            email="testuser@example.com",
            role="influencer",
            password="Test@123"
        )
        synthetic_user.set_password("Test@123")  # Secure hashed password
        db.session.add(synthetic_user)
        db.session.commit()
        print("Synthetic user added successfully!")

if __name__ == "__main__":
    add_synthetic_user()
