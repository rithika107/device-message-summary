import os
from pathlib import Path

from flask import Flask, jsonify

from .processor import process_file

def create_app(sample_file=None):
    app = Flask(__name__)
    app.json.sort_keys = False

    default_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "sample.jsonl"
    )

    input_file = Path(
        sample_file
        or default_file)
    
    @app.get("/")
    def home():
        return {
            "message": "Device Message Summary API",
            "endpoint": "/summary"
        }
    
    @app.get("/summary")
    def summary():
        try:
            result = process_file(input_file)
        except(OSError,UnicodeError) as exc:
            return jsonify({
                "error": "INPUT_FILE_READ_ERROR",
                "message": str(exc)
            }), 500

        return jsonify(result)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
         
