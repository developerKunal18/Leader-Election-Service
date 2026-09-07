import time
from threading import Lock
from flask import Flask, jsonify, request

app = Flask(__name__)
LEASE_SECONDS = 30
_state_lock = Lock()
_leader = None

def _expire():
    global _leader
    if _leader and _leader["expires_at"] <= time.time():
        _leader = None

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/leader")
def current_leader():
    with _state_lock:
        _expire()
        if not _leader:
            return jsonify({"leader": None})
        return jsonify({"leader": _leader["node_id"], "expires_in": max(0, int(_leader["expires_at"] - time.time()))})

@app.post("/api/leader/acquire")
def acquire():
    global _leader
    node_id = (request.get_json(silent=True) or {}).get("node_id")
    if not isinstance(node_id, str) or not node_id.strip():
        return jsonify({"error": "node_id_required"}), 400
    with _state_lock:
        _expire()
        if _leader:
            if _leader["node_id"] == node_id:
                return jsonify({"leader": node_id, "already_leader": True, "expires_in": int(_leader["expires_at"] - time.time())})
            return jsonify({"error": "leader_exists", "leader": _leader["node_id"]}), 409
        _leader = {"node_id": node_id, "expires_at": time.time() + LEASE_SECONDS}
        return jsonify({"leader": node_id, "expires_in": LEASE_SECONDS}), 201

@app.post("/api/leader/renew")
def renew():
    node_id = (request.get_json(silent=True) or {}).get("node_id")
    if not isinstance(node_id, str) or not node_id.strip():
        return jsonify({"error": "node_id_required"}), 400
    with _state_lock:
        _expire()
        if not _leader: return jsonify({"error": "no_active_leader"}), 404
        if _leader["node_id"] != node_id: return jsonify({"error": "not_leader"}), 403
        _leader["expires_at"] = time.time() + LEASE_SECONDS
        return jsonify({"leader": node_id, "renewed": True, "expires_in": LEASE_SECONDS})

@app.post("/api/leader/release")
def release():
    global _leader
    node_id = (request.get_json(silent=True) or {}).get("node_id")
    if not isinstance(node_id, str) or not node_id.strip():
        return jsonify({"error": "node_id_required"}), 400
    with _state_lock:
        _expire()
        if not _leader: return jsonify({"error": "no_active_leader"}), 404
        if _leader["node_id"] != node_id: return jsonify({"error": "not_leader"}), 403
        _leader = None
        return jsonify({"released": True, "node_id": node_id})

@app.errorhandler(404)
def not_found(_): return jsonify({"error": "resource_not_found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
