import json

REQUIRED_KEYS = {"device_id","sequence","status"}
VALID_STATUSES = {"ok","error"}

def is_valid_record(record):
    return (
        isinstance(record, dict)
        and set(record.keys()) == REQUIRED_KEYS
        and isinstance(record["device_id"], str)
        and bool(record["device_id"].strip())
        and not isinstance(record["sequence"], bool)
        and isinstance(record["sequence"], int)
        and record["sequence"] >= 0
        and record["status"] in VALID_STATUSES
    )

def process_lines(lines):
    accepted = 0
    duplicates = 0
    errors =[]

    seen_pairs =set()
    devices = {}

    for line_number,raw_line in enumerate(lines,start=1):

        if not raw_line.strip():
            errors.append({
                "type" : "BAD_JSON",
                "line" : line_number
            })

            continue

        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            errors.append({
                "type": "BAD_JSON",
                "line": line_number
            })

            continue

        if not is_valid_record(record):
            errors.append({
                "type": "INVALID_RECORD",
                "line": line_number
            })
            continue
        
        device_id = record["device_id"]
        sequence = record["sequence"]
        status = record["status"]

        pair = (device_id, sequence)

        if pair in seen_pairs:
            duplicates +=1

            continue

        seen_pairs.add(pair)
        accepted +=1

        if device_id not in devices:
            devices[device_id] = {
                "ok": 0,
                "error": 0,
                "last_sequence": None,
                "last_status": None
            }

        device = devices[device_id]

        device[status] +=1

        if (
            device["last_sequence"] is None
            or sequence > device["last_sequence"]
        ):
            device["last_sequence"] = sequence
            device["last_status"] = status

    sorted_devices = {
        device_id: devices[device_id]
        for device_id in sorted(devices)
    }

    return {
        "accepted": accepted,
        "duplicates": duplicates,
        "errors": errors,
        "devices": sorted_devices
    }


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return process_lines(file)
