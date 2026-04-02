from flask import Flask, request, jsonify
from flask_cors import CORS
import preprocessing
import residual
import features
import identification

app = Flask(__name__)

# Enable CORS
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():

    file = request.files['file']

    image = preprocessing.process(file)

    res = residual.extract(image)

    feat = features.extract(res)

    result = identification.identify(feat)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)