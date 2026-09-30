# Device Message Summary

A small Python application that reads simulated device messages from a JSON Lines (`.jsonl`) file, validates and processes each message, and exposes the resulting summary through a Flask HTTP endpoint.

## Prerequisites

* Python 3.10+
* `pip`
* Git (optional)

## Project Structure

```text
device-message-summary/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── processor.py
├── data/
│   └── sample.jsonl
├── tests/
│   └── test_processor.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

The application does not require a database, external service, API key, or hardware device.

## Run Tests

From the project root:

```powershell
python -m pytest -q
```

Expected result:

```text
4 passed
```

The test suite covers:

* The required sample input and expected summary.
* A lower sequence arriving after a higher sequence.
* Empty input.
* Input-file read failure through the API.

## Run the Application

From the project root:

```powershell
python -m app.main
```

The API will run at:

```text
http://127.0.0.1:5000
```

Open the summary endpoint:

```text
http://127.0.0.1:5000/summary
```

The endpoint returns the processed device summary as JSON.

## Input Rules

Each input line must contain a JSON object with exactly these fields:

```text
device_id
sequence
status
```

Validation rules:

* `device_id` must be a non-empty string. Whitespace-only values are rejected.
* `sequence` must be an integer greater than or equal to `0`. Boolean values are rejected.
* `status` must be either `ok` or `error`.
* Blank lines and malformed JSON produce a `BAD_JSON` error with the 1-based line number.
* Valid JSON with invalid fields produces an `INVALID_RECORD` error.
* Processing continues after malformed or invalid lines.
* Validation is performed before duplicate detection.
* Duplicate `(device_id, sequence)` pairs are counted, and only the first valid occurrence is accepted.
* The latest device status is determined using the highest accepted sequence number, regardless of input order.
* Devices are returned sorted by `device_id`.

## Sample Input

The supplied sample file is:

```text
data/sample.jsonl
```

It contains device messages including a duplicate record and a malformed JSON record.

For the supplied sample, the expected summary is:

```json
{
  "accepted": 3,
  "duplicates": 1,
  "errors": [
    {
      "type": "BAD_JSON",
      "line": 4
    }
  ],
  "devices": {
    "D01": {
      "ok": 1,
      "error": 1,
      "last_sequence": 3,
      "last_status": "error"
    },
    "D02": {
      "ok": 0,
      "error": 1,
      "last_sequence": 2,
      "last_status": "error"
    }
  }
}
```

## Error Handling

If the configured input file cannot be read, the API returns HTTP `500` with an `INPUT_FILE_READ_ERROR` response instead of treating the input as an empty file.

Example:

```json
{
  "error": "INPUT_FILE_READ_ERROR",
  "message": "..."
}
```

## React Integration

A React page can consume the endpoint using `fetch()`.

The frontend should distinguish between:

* **Loading:** the API request is still in progress.
* **Empty:** the request succeeded but there is no device data.
* **Populated:** the request succeeded and device data is available.
* **API failure:** the request failed or the backend returned an error.

The returned JSON can be stored in React state and used to render the device summaries.

## Assumptions

* The application processes one supplied JSONL file at a time.
* The default input file is `data/sample.jsonl`.
* A different input file can be supplied using the `DEVICE_MESSAGES_FILE` environment variable.
* Device IDs are preserved exactly as supplied when they are valid.
* Duplicate detection is based on `(device_id, sequence)`.
* Only accepted records contribute to device counts and latest-status information.
* No database, hardware device, authentication, or external hosting is required.

## Time Spent

Approximately 3 hours, including implementation, testing, API verification, and documentation.

## Unfinished Work

No required functionality is intentionally unfinished.

A React frontend was not implemented because the assignment only requires an explanation of how a React page could consume the endpoint.

## Known Limitation

The application reads the complete input file when generating the summary. It is therefore intended as a small assignment solution rather than a production-scale streaming data processing system.

## AI and Reuse Note

AI assistance was used during development to:

* Understand and break down the assignment requirements.
* Review implementation approaches for JSONL validation, duplicate detection, and sequence-aware device summaries.
* Troubleshoot Python import and pytest configuration issues.
* Review and improve documentation.

The suggestions were reviewed and adapted to the assignment requirements. The final processing logic, Flask endpoint, tests, and documentation were reviewed before submission.

During development, an import error occurred because Python did not recognize the `app` directory as a package. This was fixed by adding `app/__init__.py`.

The solution was verified by running the automated pytest suite and manually checking the `/summary` endpoint response with the supplied sample data.

No private employer code, credentials, or confidential material was used.

## Walkthrough

The main processing flow is:

```text
JSONL input
    ↓
Read each line
    ↓
Parse JSON
    ↓
Validate record
    ↓
Check duplicate (device_id, sequence)
    ↓
Update accepted/error counts
    ↓
Determine latest sequence/status
    ↓
Sort devices
    ↓
Return summary
    ↓
Flask /summary endpoint
```

The walkthrough demonstrates:

1. The main processing flow in `processor.py`.
2. The malformed JSON failure case and `BAD_JSON` response.
3. The `/summary` API response.
4. The automated tests using `python -m pytest -q`.
5. The design choice of using the highest sequence number to determine the latest device status.
6. The import/package issue found during development and fixed by adding `app/__init__.py`.
