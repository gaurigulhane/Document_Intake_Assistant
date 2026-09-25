def test_generate_document(client):
    create_res = client.post("/api/sessions")
    session_id = create_res.json()["id"]

    client.patch(f"/api/sessions/{session_id}/state", json={
        "field": "full_name",
        "value": "Alice Walker"
    })

    doc_res = client.post(f"/api/sessions/{session_id}/document")
    assert doc_res.status_code == 200
    doc_data = doc_res.json()
    assert "FICTIONAL DOCUMENT — NOT LEGAL ADVICE" in doc_data["disclaimer"]
    assert "Alice Walker" in doc_data["document_text"]
