import os

HOST = os.getenv("ICAO_FACE_HOST", "127.0.0.1")
# 50220 est souvent bloqué (plage réservée Windows/Hyper-V 50160–50259) → défaut 50270
PORT = int(os.getenv("ICAO_FACE_PORT", "50270"))

# Seuils décision finale
SCORE_ACCEPTED = int(os.getenv("ICAO_SCORE_ACCEPTED", "90"))
SCORE_REVIEW = int(os.getenv("ICAO_SCORE_REVIEW", "75"))

# Temps réel : score minimal pour statut READY
REALTIME_READY_SCORE = int(os.getenv("ICAO_REALTIME_READY_SCORE", "82"))

# Frames consécutives READY avant auto-capture (frontend, ~280 ms/frame → 12 ≈ 3,4 s)
AUTO_CAPTURE_STABLE_FRAMES = int(os.getenv("ICAO_AUTO_CAPTURE_STABLE_FRAMES", "12"))
