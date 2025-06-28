from flask import Flask, render_template
from routes import routes_bp
import os
# import gunicorn #Dummy placeholder

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.register_blueprint(routes_bp)


@app.route("/")
def home():
    # print(os.getenv("OPENAI_API_KEY"))
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
