import os
import secrets

from flask import Flask, render_template
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import BASE_DIR, configure_ocr_engine, configure_upload_folder
from .routes import main_bp


def create_app():
    configure_ocr_engine()

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024,
        SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_urlsafe(32)),
    )
    # Enable ProxyFix if behind a reverse proxy (e.g. Render/Nginx)
    if os.getenv("USE_PROXY_FIX", "false").lower() in ("true", "1"):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    configure_upload_folder(app)
    app.register_blueprint(main_bp)

    @app.errorhandler(RequestEntityTooLarge)
    def upload_too_large(error):
        max_upload_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return (
            render_template(
                "result.html",
                error=f"The uploaded image is too large. Please upload an image smaller than {max_upload_mb} MB.",
            ),
            413,
        )

    return app
