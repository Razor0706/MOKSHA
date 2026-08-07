import os
import socket
from medical_report_app import create_app


def find_free_port(host, preferred_port):
    port = preferred_port
    while port < preferred_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                port += 1
    return preferred_port


app = create_app()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    requested_port = int(os.getenv("PORT", 5000))
    port = find_free_port(host, requested_port)

    if port != requested_port:
        print(f" [!] Port {requested_port} is in use. Switched to available port {port}.")

    print("\n========================================================")
    print(f" MOKSHA Flask App Running At: http://{host}:{port}/")
    print(f" IMPORTANT: Open http://127.0.0.1:{port}/ (HTTP, not HTTPS)")
    print("========================================================\n")

    app.run(host=host, port=port, debug=True, use_reloader=False)
