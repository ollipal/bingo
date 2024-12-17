from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows ALL origins (*)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=False)