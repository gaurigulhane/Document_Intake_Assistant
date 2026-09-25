def test_conflict_detection_and_resolution(client):
    create_res = client.post("/api/sessions")
    session_id = create_res.json()["id"]

    # 1. Set confirmed name
    client.patch(f"/api/sessions/{session_id}/state", json={
        "field": "full_name",
        "value": "John Smith"
    })

    # 2. User sends contradictory name
    msg_res = client.post(f"/api/sessions/{session_id}/messages", json={
        "content": "My name is Jane Doe"
    })
    assert msg_res.status_code == 200
    state_res = msg_res.json()["structured_state"]
    assert state_res["statuses"]["full_name"] == "conflicted"

    # 3. Check conflicts endpoint
    conf_res = client.get(f"/api/sessions/{session_id}/conflicts")
    assert conf_res.status_code == 200
    conflicts = conf_res.json()
    assert len(conflicts) > 0
    conflict_id = conflicts[0]["id"]

    # 4. Resolve conflict by keeping new
    res_res = client.post(f"/api/sessions/{session_id}/conflicts/{conflict_id}/resolve", json={
        "choice": "use_new"
    })
    assert res_res.status_code == 200
    resolved_state = res_res.json()
    assert resolved_state["data"]["full_name"] == "Jane Doe"
    assert resolved_state["statuses"]["full_name"] == "confirmed"
