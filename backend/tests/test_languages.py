def test_supported_languages(client):
    res = client.get("/api/languages")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 14
    codes = [l["code"] for l in data["supported_languages"]]
    assert "en" in codes
    assert "hi" in codes
    assert "ur" in codes
    assert "sa" in codes

    # Check RTL on Urdu
    ur = next((l for l in data["supported_languages"] if l["code"] == "ur"), None)
    assert ur is not None
    assert ur["is_rtl"] is True

def test_language_translations(client):
    res = client.get("/api/languages/hi/translations")
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "hi"
    assert "translations" in data
    assert "योजनामित्र AI" in data["translations"]["badge_ai"]
