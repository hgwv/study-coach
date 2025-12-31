from flask import Flask
from extensions import db, login_manager
from auth import auth_bp
from views import main_bp

def create_app():
    app = Flask(__name__)

    # NOTE: fine for local dev; change for deployment later
    app.config["SECRET_KEY"] = "dev-secret-change-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///studycoach.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        # imports ensure models are registered before creating tables
        import models  # noqa: F401
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)