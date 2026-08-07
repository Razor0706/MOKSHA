import os
from medical_report_app import create_app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    print(f" -> Starting MOKSHA Flask App on http://{host}:{port}/")
    print(" -> Make sure to use HTTP (http://127.0.0.1:5000) in your browser.")
    app.run(host=host, port=port, debug=True)
