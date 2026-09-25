def test_download_pdf(client):
    create_res = client.post("/api/sessions")
    session_id = create_res.json()["id"]

    client.patch(f"/api/sessions/{session_id}/state", json={
        "field": "full_name",
        "value": "Bob Vance"
    })

    pdf_res = client.get(f"/api/sessions/{session_id}/document/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")
