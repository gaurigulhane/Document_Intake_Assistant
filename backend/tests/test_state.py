def test_direct_state_edit(client):
    create_res = client.post("/api/sessions")
    assert create_res.status_code == 201
    session_id = create_res.json()["id"]

    # Direct edit full name
    patch_res = client.patch(f"/api/sessions/{session_id}/state", json={
        "field": "full_name",
        "value": "Gauri Gulhane"
    })
    assert patch_res.status_code == 200
    state_data = patch_res.json()
    assert state_data["data"]["full_name"] == "Gauri Gulhane"
    assert state_data["statuses"]["full_name"] == "confirmed"
    assert state_data["completion_percentage"] > 0
