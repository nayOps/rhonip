#!/usr/bin/env python3
"""
Smoke test enrôlement:
- crée et soumet des sessions pour toutes les strates
- vérifie le statut final
- vérifie les insertions dans les tables d'extensions
"""

from __future__ import annotations

import argparse
import json
import random
import string
import subprocess
import sys
import time
from datetime import date
from typing import Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


STRATA = [
    "ELEVES",
    "ETUDIANTS",
    "ELECTEURS",
    "PNC",
    "FARDC",
    "PRISON",
    "REFUGIE",
    "ENFANT",
    "FONCTIONNAIRE",
]

EXT_TABLE_BY_STRATA = {
    "ELEVES": "ext_eleves",
    "ETUDIANTS": "ext_eleves",
    "ELECTEURS": "ext_electeurs",
    "PNC": "ext_pnc",
    "FARDC": "ext_fardc",
    "PRISON": "ext_prison",
    "REFUGIE": "ext_refugies",
    "ENFANT": "ext_enfants",
    "FONCTIONNAIRE": "",
}


def rand_code(size: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=size))


def http_json(method: str, url: str, payload: Dict | None = None, timeout: int = 30) -> Tuple[int, Dict]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(url=url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return response.status, data
    except HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            data = {"raw": raw}
        return err.code, data
    except URLError as err:
        return 0, {"error": str(err)}


def build_core(strate: str, idx: int) -> Dict:
    # Evite la règle âge>=18 sur ELECTEURS
    birth = "1992-05-14" if strate == "ELECTEURS" else "1998-09-20"
    suffix = f"{strate[:3]}{idx:02d}{rand_code(3)}"
    return {
        "nom": f"Smoke{strate[:4]}{idx}",
        "postnom": "Test",
        "prenom": f"Agent{idx}",
        "sexe": "M" if idx % 2 == 0 else "F",
        "date_naissance": birth,
        "lieu_naissance": "Kinshasa",
        "province_naissance": "Kinshasa",
        "nationalite": "CD",
        "province_residence": "Kinshasa",
        "telephone": f"+243810{idx:06d}"[:13],
        "type_piece_identite": "Autre",
        "numero_piece_identite": f"DOC-{suffix}",
        "date_emission_piece": "2020-01-15",
        "lieu_emission_piece": "Kinshasa",
    }


def extension_payload(strate: str, idx: int) -> Dict:
    today = date.today().isoformat()
    if strate in ("ELEVES", "ETUDIANTS"):
        return {
            "matricule_scolaire": f"SCH-{idx}-{rand_code(4)}",
            "etablissement": "Lycée de test",
            "code_etablissement": f"ETB-{idx:03d}",
            "niveau": "6e Secondaire",
            "cycle": "Secondaire",
            "annee_scolaire": "2025-2026",
            "statut_scolaire": "Régulier",
            "province_etablissement": "Kinshasa",
        }
    if strate == "ELECTEURS":
        return {
            "centre_vote": "Centre Test 01",
            "code_centre_vote": f"CENI-{idx:04d}",
            "circonscription": "Kinshasa I",
            "secteur_vote": "Gombe",
            "statut_inscription": "Inscrit",
            "date_inscription_ceni": today,
            "bureau_vote": f"B{idx:03d}",
            "province_vote": "Kinshasa",
            "commune_vote": "Gombe",
        }
    if strate == "PNC":
        return {
            "matricule_pnc": f"PNC-{idx:04d}",
            "grade": "Inspecteur",
            "unite": "Unité Test",
            "fonction": "Patrouille",
            "date_integration": "2018-01-10",
            "statut_service": "Actif",
            "zone_affectation": "Kinshasa",
        }
    if strate == "FARDC":
        return {
            "matricule_fardc": f"FARDC-{idx:04d}",
            "grade": "Lieutenant",
            "unite_affectation": "1ere Brigade",
            "zone_operation": "Ouest",
            "fonction": "Opérations",
            "date_integration": "2017-06-12",
            "statut_militaire": "Actif",
            "type_mission": "Interne",
        }
    if strate == "PRISON":
        return {
            "numero_dossier_judiciaire": f"DOS-{idx:05d}",
            "centre_detention": "CPRK",
            "statut_detention": "Préventif",
            "date_incarceration": "2024-02-01",
            "infraction": "Infraction test",
            "autorite_judiciaire": "Parquet de Gombe",
        }
    if strate == "REFUGIE":
        return {
            "numero_hcr": f"HCR-{idx:05d}",
            "pays_origine": "Soudan",
            "statut_juridique": "Réfugié",
            "document_sejour": "Attestation HCR",
            "date_entree_territoire": "2022-04-01",
            "organisme_encadrement": "HCR",
        }
    if strate == "ENFANT":
        return {
            "tuteur_nom": "Parent Test",
            "tuteur_nin": f"CD-2026-0000-{idx:07d}",
            "lien_tuteur": "Père",
            "adresse_tuteur": "Avenue Test 1, Kinshasa",
            "document_parentalite": "Acte de naissance",
            "autorisation_parentale": True,
        }
    if strate == "FONCTIONNAIRE":
        return {
            "matricule": f"FP-{idx:05d}",
            "ministere": "Ministère Test",
            "grade": "Attaché",
        }
    raise ValueError(f"Strate non gérée: {strate}")


def build_payload(session_id: str, strate: str, idx: int) -> Dict:
    core = build_core(strate, idx)
    ext_key = strate.lower()
    return {
        "session_id": session_id,
        "channel": "fixed",
        "device_id": f"smoke-device-{idx:03d}",
        "operator_id": "smoke-bot",
        "location": {"province": "Kinshasa", "commune": "Gombe"},
        "schema_version": "1.0",
        "core": core,
        "biometrics": {
            "face": {"ref": f"face://{session_id}", "quality": 0.95},
            "fingerprints": {"quality": 0.0},  # optionnel si pending/skipped
            "iris": {"ref": f"iris://{session_id}", "quality": 0.93},
        },
        "strata": [strate],
        "extensions": {ext_key: extension_payload(strate, idx)},
        "auto_process": False,
    }


def poll_status(base_url: str, session_id: str, timeout_s: int = 120) -> Dict:
    deadline = time.time() + timeout_s
    last = {}
    while time.time() < deadline:
        code, data = http_json("GET", f"{base_url}/sessions/status/{session_id}/")
        if code == 200:
            last = data
            status = data.get("status")
            if status in {"COMPLETED", "FAILED", "CANCELLED"}:
                return data
        time.sleep(2)
    return last


def psql_count(repo_root: str, table: str, nins: List[str]) -> int:
    if not nins:
        return 0
    in_values = ",".join(f"'{nin}'" for nin in nins)
    query = f"SELECT COUNT(*) FROM {table} WHERE nin IN ({in_values});"
    cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "fgp_user",
        "-d",
        "fgp_db",
        "-t",
        "-A",
        "-c",
        query,
    ]
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return -1
    try:
        return int(result.stdout.strip() or "0")
    except ValueError:
        return -1


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test toutes strates (3+ enregistrements/strate).")
    parser.add_argument("--base-url", default="http://localhost:8001/api/v1/enrolments")
    parser.add_argument("--per-strata", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--check-extensions",
        action="store_true",
        help="Vérifie aussi les tables extensions en base (strict).",
    )
    args = parser.parse_args()

    total_target = len(STRATA) * args.per_strata
    print(f"[INFO] Démarrage smoke test: {len(STRATA)} strates x {args.per_strata} = {total_target} sessions")

    completed_by_strata: Dict[str, int] = {s: 0 for s in STRATA}
    nins_by_strata: Dict[str, List[str]] = {s: [] for s in STRATA}
    failures: List[Dict] = []

    seq = 0
    for strate in STRATA:
        for i in range(args.per_strata):
            seq += 1
            session_id = f"FGP-SMOKE-{int(time.time() * 1000)}-{rand_code(6)}"
            payload = build_payload(session_id, strate, seq)

            c_code, c_data = http_json("POST", f"{args.base_url}/sessions/", payload)
            if c_code != 201:
                failures.append(
                    {"strate": strate, "session_id": session_id, "step": "create", "code": c_code, "data": c_data}
                )
                print(f"[FAIL][{strate}] create {session_id}: HTTP {c_code}")
                continue

            s_code, s_data = http_json("POST", f"{args.base_url}/sessions/submit/{session_id}/", {})
            if s_code not in (200, 202):
                failures.append(
                    {"strate": strate, "session_id": session_id, "step": "submit", "code": s_code, "data": s_data}
                )
                print(f"[FAIL][{strate}] submit {session_id}: HTTP {s_code}")
                continue

            final_state = poll_status(args.base_url, session_id, timeout_s=args.timeout)
            final_status = final_state.get("status")
            nin = final_state.get("nin")
            if final_status == "COMPLETED" and nin:
                completed_by_strata[strate] += 1
                nins_by_strata[strate].append(nin)
                print(f"[OK][{strate}] {session_id} -> {nin}")
            else:
                failures.append(
                    {
                        "strate": strate,
                        "session_id": session_id,
                        "step": "final_status",
                        "code": final_status,
                        "data": final_state,
                    }
                )
                print(f"[FAIL][{strate}] {session_id} -> {final_status}")

    print("\n=== Résumé sessions COMPLETED ===")
    for s in STRATA:
        print(f"{s:14s}: {completed_by_strata[s]}")

    ext_counts_ok = True
    if args.check_extensions:
        print("\n=== Vérification extensions (par NIN générés) ===")
        for s in STRATA:
            table = EXT_TABLE_BY_STRATA[s]
            if not table:
                print(f"{s:14s}: table=(non disponible) count=NA")
                ext_counts_ok = False
                continue
            count = psql_count(args.repo_root, table, nins_by_strata[s])
            expected = len(nins_by_strata[s])
            ok = count >= expected and count >= args.per_strata
            if not ok:
                ext_counts_ok = False
            print(f"{s:14s}: table={table:16s} count={count} expected>={expected} target>={args.per_strata}")
    else:
        print("\n[INFO] Vérification des tables extensions non demandée (--check-extensions pour l'activer).")

    strata_ok = all(completed_by_strata[s] >= args.per_strata for s in STRATA)
    if failures:
        print("\n=== Échecs détaillés ===")
        for failure in failures:
            print(json.dumps(failure, ensure_ascii=False))

    if strata_ok and ext_counts_ok and not failures:
        print("\n[PASS] Smoke test OK pour toutes les strates.")
        return 0

    print("\n[FAIL] Smoke test incomplet. Voir détails ci-dessus.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
