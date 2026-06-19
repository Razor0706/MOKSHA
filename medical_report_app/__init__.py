from flask import Flask

from .config import BASE_DIR, configure_ocr_engine, configure_upload_folder
from .routes import main_bp


def create_app():
    configure_ocr_engine()

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    configure_upload_folder(app)
    app.register_blueprint(main_bp)
    return app
