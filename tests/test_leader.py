import app as m

def setup_function():
    m._leader = None

def test_health():
    assert m.app.test_client().get("/health").status_code == 200

def test_first_node_becomes_leader():
    r = m.app.test_client().post("/api/leader/acquire", json={"node_id":"node-1"})
    assert r.status_code == 201 and r.json["leader"] == "node-1"

def test_second_node_rejected():
    c=m.app.test_client()
    c.post("/api/leader/acquire", json={"node_id":"node-1"})
    r=c.post("/api/leader/acquire", json={"node_id":"node-2"})
    assert r.status_code == 409

def test_renew_and_release():
    c=m.app.test_client()
    c.post("/api/leader/acquire", json={"node_id":"node-1"})
    assert c.post("/api/leader/renew", json={"node_id":"node-1"}).status_code == 200
    assert c.post("/api/leader/release", json={"node_id":"node-1"}).status_code == 200
    assert c.get("/api/leader").json["leader"] is None

def test_non_leader_cannot_change_leader():
    c=m.app.test_client()
    c.post("/api/leader/acquire", json={"node_id":"node-1"})
    assert c.post("/api/leader/renew", json={"node_id":"node-2"}).status_code == 403
    assert c.post("/api/leader/release", json={"node_id":"node-2"}).status_code == 403

def test_expired_leader_can_be_replaced():
    c=m.app.test_client()
    c.post("/api/leader/acquire", json={"node_id":"node-1"})
    m._leader["expires_at"]=0
    r=c.post("/api/leader/acquire", json={"node_id":"node-2"})
    assert r.status_code == 201 and r.json["leader"] == "node-2"
