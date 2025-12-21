from src import app
from src.controllers.auth_controller import protect
from src.controllers.sensor_controller import reset


# @app.before_request
# def before_request():
#     return protect()


@app.route("/api/")
def index():
    return "<p>SGR Sensor</p>"


if __name__ == "__main__":
    with app.app_context():
        reset()

    app.run(host="0.0.0.0", port=5000, debug=True)
