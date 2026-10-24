def test_assistant_chat_endpoint(client):
    """Assistant chat accepts query, relevant scheme slug, and returns honest response."""
    payload = {
        "message": "What documents do I need for Post-Matric Scholarship?",
        "language": "en",
        "scheme_slug": "post-matric"
    }
    response = client.post("/api/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert "disclaimer" in data
