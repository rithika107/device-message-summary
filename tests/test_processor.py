from app.processor import process_lines
from app.main import create_app


def test_sample_data():

    lines = [
        '{"device_id":"D01","sequence":1,"status":"ok"}\n',
        '{"device_id":"D01","sequence":1,"status":"ok"}\n',
        '{"device_id":"D02","sequence":2,"status":"error"}\n',
        '{"device_id":"D02","sequence":bad,"status":"ok"}\n',
        '{"device_id":"D01","sequence":3,"status":"error"}\n',
    ]

    result = process_lines(lines)

    assert result["accepted"] == 3
    assert result["duplicates"] == 1
    assert result["errors"] == [
        {"type": "BAD_JSON", "line": 4}
    ]

    assert result["devices"]["D01"] == {
        "ok": 1,
        "error": 1,
        "last_sequence": 3,
        "last_status": "error"
    }

    assert result["devices"]["D02"] == {
        "ok": 0,
        "error": 1,
        "last_sequence": 2,
        "last_status": "error"
    }


def test_lower_sequence_does_not_replace_latest():
    
    lines = [
        '{"device_id":"D01","sequence":10,"status":"ok"}\n',
        '{"device_id":"D01","sequence":5,"status":"error"}\n',
    ]

    result = process_lines(lines)

    assert result["accepted"] == 2
    assert result["duplicates"] == 0

    assert result["devices"]["D01"]["last_sequence"] == 10
    assert result["devices"]["D01"]["last_status"] == "ok"


def test_empty_input():
    
    result = process_lines([])

    assert result == {
        "accepted": 0,
        "duplicates": 0,
        "errors": [],
        "devices": {}
    }

def test_summary_file_read_failure(tmp_path):
    missing_file = tmp_path / "missing.jsonl"

    app = create_app(missing_file)
    client = app.test_client()

    response = client.get("/summary")

    assert response.status_code == 500

    body = response.get_json()

    assert body["error"] == "INPUT_FILE_READ_ERROR"