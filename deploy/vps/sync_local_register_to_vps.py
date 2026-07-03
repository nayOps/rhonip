#!/usr/bin/env python3
"""
Synchronise Register local → VPS : sessions, médias et photos RH.

  python deploy/vps/sync_local_register_to_vps.py --dry-run
  python deploy/vps/sync_local_register_to_vps.py
  python deploy/vps/sync_local_register_to_vps.py --matricule 1010020171
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

VPS_HOST = os.environ.get("ONIP_VPS_HOST", "102.68.62.85")
VPS_USER = os.environ.get("ONIP_VPS_USER", "adn")
VPS_RH_URL = os.environ.get("ONIP_VPS_RH_URL", f"http://{VPS_HOST}:8100")
GUICHET_KEY = os.environ.get("GUICHET_INTERNAL_API_KEY", "fgp_guichet_internal_dev")
SSHPASS = os.environ.get("SSHPASS", "ADNKinshasa**2024")

GW = "fgp_enrollment_gateway"
PG = "onip_postgres"


def run(cmd: list[str], *, check: bool = True, binary: bool = False) -> str | bytes:
    r = subprocess.run(cmd, capture_output=True, check=False)
    if check and r.returncode != 0:
        err = (r.stderr or b"").decode("utf-8", errors="replace")
        out = (r.stdout or b"").decode("utf-8", errors="replace")
        raise RuntimeError(f"Command failed ({r.returncode}): {' '.join(cmd)}\n{err}\n{out}")
    if binary:
        return r.stdout
    return (r.stdout or b"").decode("utf-8", errors="replace").strip()


def ssh(cmd: str) -> str:
    os.environ["SSHPASS"] = SSHPASS
    return run(
        ["sshpass", "-e", "ssh", "-o", "StrictHostKeyChecking=no", f"{VPS_USER}@{VPS_HOST}", cmd]
    )


def local_sql(sql: str) -> str:
    return run(["docker", "exec", PG, "psql", "-U", "onip_user", "-d", "onip_db", "-t", "-A", "-c", sql])


def vps_sql(sql: str) -> str:
    esc = sql.replace("'", "'\"'\"'")
    return ssh(f"docker exec {PG} psql -U onip_user -d onip_db -t -A -c '{esc}'")


def vps_photo_matricules() -> set[str]:
    out = vps_sql(
        "SELECT registration_number FROM employee_employee "
        "WHERE photo IS NOT NULL AND photo <> '';"
    )
    return {line.strip() for line in out.splitlines() if line.strip()}


def vps_session_ids() -> set[str]:
    out = vps_sql("SELECT session_id FROM enrollment_sessions;")
    return {line.strip() for line in out.splitlines() if line.strip()}


def docker_cat(path: str) -> bytes:
    return run(["docker", "exec", GW, "cat", path], binary=True)


def file_uri_to_path(uri: str) -> str | None:
    if not uri or not str(uri).startswith("file:"):
        return None
    return unquote(urlparse(uri).path)


def load_photo_b64(session_id: str, payload: dict) -> str | None:
    face = (payload.get("biometrics") or {}).get("face") or {}
    for key in ("icao_image_base64", "image_base64"):
        val = face.get(key)
        if val:
            raw = str(val)
            return raw.split("base64,", 1)[-1] if "base64," in raw else raw

    uri = (payload.get("persisted_media") or {}).get("photo_uri") or ""
    path = file_uri_to_path(str(uri))
    candidates = []
    if path:
        candidates.append(path)
    candidates += [
        f"/app/media/enrollments/{session_id}/face/photo.jpg",
        f"/app/media/enrollments/{session_id}/face/photo.png",
    ]
    for p in candidates:
        try:
            raw = docker_cat(p)
            if raw:
                return base64.b64encode(raw).decode("ascii")
        except Exception:
            continue
    return None


def fetch_local_sessions(since: str) -> list[dict]:
    out = local_sql(f"""
        SELECT json_agg(row_to_json(t))
        FROM (
            SELECT id::text, session_id, channel, device_id, operator_id, location,
                   payload, payload_hash, COALESCE(payload_signature,'') AS payload_signature,
                   status, progress_percentage, registration_number,
                   COALESCE(employee_status,'') AS employee_status,
                   abis_result, modality_status,
                   COALESCE(error_message,'') AS error_message,
                   validation_errors,
                   created_at::timestamptz::text AS created_at,
                   updated_at::timestamptz::text AS updated_at,
                   completed_at::timestamptz::text AS completed_at,
                   processing_time_ms
            FROM enrollment_sessions
            WHERE registration_number IS NOT NULL
              AND payload->'persisted_media'->>'photo_uri' IS NOT NULL
              AND updated_at::date >= '{since}'
            ORDER BY registration_number, updated_at DESC
        ) t
    """)
    if not out or out == "":
        return []
    data = json.loads(out)
    return data or []


def pick_sessions(sessions: list[dict]) -> list[dict]:
    rank = {"COMPLETED": 3, "PENDING": 2, "FAILED": 1}
    best: dict[str, dict] = {}
    for s in sessions:
        mat = s["registration_number"]
        cur = best.get(mat)
        if not cur:
            best[mat] = s
            continue
        sr, cr = rank.get(s["status"], 0), rank.get(cur["status"], 0)
        if sr > cr or (sr == cr and s["updated_at"] > cur["updated_at"]):
            best[mat] = s
    return list(best.values())


def push_photo(matricule: str, b64: str, dry_run: bool) -> bool:
    if dry_run:
        print(f"  [dry-run] photo RH → {matricule}")
        return True
    r = requests.post(
        f"{VPS_RH_URL}/api/guichet/employee/upsert/",
        json={"registration_number": matricule, "photo_base64": b64},
        headers={"Content-Type": "application/json", "X-Guichet-Internal-Key": GUICHET_KEY},
        timeout=90,
    )
    if r.status_code not in (200, 201):
        print(f"  ERREUR photo RH: {r.status_code} {r.text[:180]}")
        return False
    return True


def ssh_mkdir_remote() -> None:
    ssh("mkdir -p /home/adn/onip-rh/sync_media")


def copy_media(session_id: str, dry_run: bool) -> bool:
    if dry_run:
        print(f"  [dry-run] media → {session_id}")
        return True
    os.environ["SSHPASS"] = SSHPASS
    ssh_mkdir_remote()
    with tempfile.TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / f"{session_id}.tar.gz"
        with open(tar_path, "wb") as f:
            subprocess.run(
                ["docker", "exec", GW, "tar", "czf", "-", "-C", "/app/media/enrollments", session_id],
                stdout=f,
                check=True,
            )
        remote = f"/home/adn/onip-rh/sync_media/{session_id}.tar.gz"
        subprocess.run(
            ["sshpass", "-e", "scp", "-o", "StrictHostKeyChecking=no", str(tar_path), f"{VPS_USER}@{VPS_HOST}:{remote}"],
            check=True,
        )
        ssh(
            f"docker cp {remote} {GW}:/tmp/sync.tar.gz && "
            f"docker exec {GW} bash -c 'mkdir -p /app/media/enrollments && "
            f"tar xzf /tmp/sync.tar.gz -C /app/media/enrollments && rm /tmp/sync.tar.gz' && "
            f"rm -f {remote}"
        )
    return True


def import_sessions_batch(sessions: list[dict], dry_run: bool) -> bool:
    if dry_run:
        print(f"  [dry-run] import {len(sessions)} session(s) sur VPS")
        return True
    payload = json.dumps(sessions, ensure_ascii=False)
    os.environ["SSHPASS"] = SSHPASS
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write(payload)
        local_json = f.name
    try:
        remote = "/home/adn/onip-rh/sync_media/sessions_import.json"
        ssh_mkdir_remote()
        subprocess.run(
            ["sshpass", "-e", "scp", "-o", "StrictHostKeyChecking=no", local_json, f"{VPS_USER}@{VPS_HOST}:{remote}"],
            check=True,
        )
        importer_local = Path(__file__).with_name("import_sessions_vps.py")
        importer_remote = "/home/adn/onip-rh/sync_media/import_sessions_vps.py"
        subprocess.run(
            ["sshpass", "-e", "scp", "-o", "StrictHostKeyChecking=no", str(importer_local), f"{VPS_USER}@{VPS_HOST}:{importer_remote}"],
            check=True,
        )
        ssh(
            f"docker cp {importer_remote} {GW}:/tmp/import_sessions_vps.py && "
            f"docker cp {remote} {GW}:/tmp/sessions_import.json && "
            f"docker exec -w /app -e PYTHONPATH=/app {GW} python /tmp/import_sessions_vps.py /tmp/sessions_import.json"
        )
        return True
    finally:
        os.unlink(local_json)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--since", default="2026-07-01")
    ap.add_argument("--matricule")
    args = ap.parse_args()

    sessions = pick_sessions(fetch_local_sessions(args.since))
    if args.matricule:
        sessions = [s for s in sessions if s["registration_number"] == args.matricule]

    vps_photos: set[str] = set()
    vps_sessions: set[str] = set()
    if not args.dry_run:
        print("Chargement état VPS…", flush=True)
        vps_photos = vps_photo_matricules()
        vps_sessions = vps_session_ids()
        print(f"  VPS: {len(vps_photos)} photos RH, {len(vps_sessions)} sessions", flush=True)

    print(f"Matricules locaux à examiner : {len(sessions)}", flush=True)

    to_import: list[dict] = []
    ok_p = ok_s = skip = fail = 0

    for s in sessions:
        mat, sid = s["registration_number"], s["session_id"]
        print(f"\n--- {mat} ({sid}) ---", flush=True)

        need_sess = args.dry_run or sid not in vps_sessions
        need_photo = args.dry_run or mat not in vps_photos

        if not need_sess and not need_photo:
            print("  déjà complet sur VPS")
            skip += 1
            continue

        b64 = load_photo_b64(sid, s["payload"])
        if not b64:
            print("  ERREUR: photo locale introuvable")
            fail += 1
            continue

        if need_sess:
            if copy_media(sid, args.dry_run):
                to_import.append(s)
                ok_s += 1
            else:
                fail += 1

        if need_photo:
            if push_photo(mat, b64, args.dry_run):
                ok_p += 1
            else:
                fail += 1

    if to_import and not args.dry_run:
        print(f"\n=== Import {len(to_import)} session(s) en base VPS ===")
        import_sessions_batch(to_import, False)

    print(f"\n=== Résumé ===")
    print(f"  photos RH : {ok_p} | sessions : {ok_s} | ignorés : {skip} | échecs : {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
