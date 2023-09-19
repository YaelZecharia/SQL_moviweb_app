from flask import Flask
import os
from dotenv import load_dotenv
from datamanager.sql_data_manager import db


# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask application just for the purpose of database creation
app = Flask(__name__)

# Set database path and configuration
db_path = os.path.join(os.path.dirname(__file__), "data", "database_file.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
db.init_app(app)


def create_tables():
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    create_tables()
    print("Tables created successfully!")
