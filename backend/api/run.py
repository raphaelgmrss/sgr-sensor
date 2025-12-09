from src import app
from src.controllers.auth_controller import protect


# @app.before_request
# def before_request():
#     return protect()


@app.route("/")
def index():
    return "<p>SGR Sensor</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
