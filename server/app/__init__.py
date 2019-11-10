import flask
from flask_cors import CORS

app = flask.Flask(__name__, static_folder="../../build/static", template_folder="../../build")
CORS(app)
