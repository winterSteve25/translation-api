import os
import uuid

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from translators import LANGUAGES

app = Flask("translation")
CORS(app)


@app.route('/langs', methods=['GET'])
def get_langs():
    return jsonify(LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate():
    binary = request.data
    lang = request.args.get("lang")
    type = request.args.get("type")

    if not lang:
        response = {"error": "missing destination language"}
        return jsonify(response), 400

    if lang not in LANGUAGES:
        response = {"error": "language not supported"}
        return jsonify(response), 400


    filename = str(uuid.uuid4())
    path = './storage'
    saved_path = os.path.join(path, f"{filename}.{type}")
    result_path = os.path.join(path, f"{filename}_translated.{type}")
    os.makedirs(path, exist_ok=True)

    with open(saved_path, 'wb') as file:
        file.write(binary)

    if type == "pdf":
        epub_path = "./storage/{filename}.epub"
        os.system(f"ebook-convert {saved_path} {epub_path} --output-profile tablet")
        os.system(f"poetry run python translators/epub.py {epub_path} -l {lang}")
    else:
        os.system(f"poetry run python translators/epub.py {saved_path} -l {lang}")

    response = send_file(result_path, as_attachment=True)
    os.remove(result_path)
    os.remove(saved_path)

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)