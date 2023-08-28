import os
import uuid

from flask import Flask, jsonify, request, send_file
from epub import LANGUAGES

app = Flask("translation")


@app.route('/langs', methods=['GET'])
def get_langs():
    return jsonify(LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate_epub():
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
        os.system(f"poetry run python pdf/translator.py {saved_path} {lang} {result_path}")
        pass
    elif type == "epub":
        os.system(f"poetry run python epub/translator.py {saved_path} -l {lang}")
        pass

    response = send_file(result_path, as_attachment=True)
    os.remove(result_path)
    os.remove(saved_path)

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)