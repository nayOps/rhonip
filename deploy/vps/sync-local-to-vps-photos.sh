#!/usr/bin/env bash
# Compare local vs VPS — sessions et photos à synchroniser
set -euo pipefail

echo "=== LOCAL: sessions COMPLETED avec photo (depuis 2026-07-01) ==="
docker exec onip_postgres psql -U onip_user -d onip_db -t -A -c "
SELECT registration_number || '|' || session_id || '|' || status
FROM enrollment_sessions
WHERE status IN ('COMPLETED','PENDING','FAILED')
  AND registration_number IS NOT NULL
  AND payload->'persisted_media'->>'photo_uri' IS NOT NULL
  AND updated_at::date >= '2026-07-01'
ORDER BY registration_number;
" | tee /tmp/local_sessions.txt

echo ""
echo "count local: $(wc -l < /tmp/local_sessions.txt)"
