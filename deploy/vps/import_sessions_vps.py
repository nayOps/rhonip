"""Import enrollment sessions JSON sur le VPS (exécuté dans fgp_enrollment_gateway)."""
import json
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "enrollment_gateway.settings")

import django  # noqa: E402

django.setup()

from apps.enrollment.models import EnrollmentSession  # noqa: E402
from django.utils.dateparse import parse_datetime  # noqa: E402


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sessions_import.json"
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)

    for row in rows:
        sid = row["session_id"]
        defaults = {
            "channel": row["channel"],
            "device_id": row["device_id"],
            "operator_id": row["operator_id"],
            "location": row["location"],
            "payload": row["payload"],
            "payload_hash": row["payload_hash"],
            "payload_signature": row.get("payload_signature") or None,
            "status": row["status"],
            "progress_percentage": row.get("progress_percentage") or 0,
            "registration_number": row["registration_number"],
            "employee_status": row.get("employee_status") or None,
            "abis_result": row.get("abis_result") or {},
            "modality_status": row.get("modality_status") or {},
            "error_message": row.get("error_message") or None,
            "validation_errors": row.get("validation_errors") or [],
            "processing_time_ms": row.get("processing_time_ms"),
        }
        ca = row.get("completed_at")
        if ca:
            defaults["completed_at"] = parse_datetime(ca)
        _, created = EnrollmentSession.objects.update_or_create(
            session_id=sid,
            defaults=defaults,
        )
        print(sid, "created" if created else "updated")

    print("OK", len(rows))


if __name__ == "__main__":
    main()
