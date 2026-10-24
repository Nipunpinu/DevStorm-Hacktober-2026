def test_list_schemes(client):
    response = client.get("/api/schemes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    # Check schema fields
    first = data[0]
    assert "slug" in first
    assert "official_name" in first
    assert "category" in first
    assert "numeric_benefit_value" in first
    assert "documents_count" in first


def test_scheme_category_filter(client):
    response = client.get("/api/schemes?category=education")
    assert response.status_code == 200
    data = response.json()
    assert all(s["category"] == "education" for s in data)


def test_scheme_detail(client):
    response = client.get("/api/schemes/post-matric?lang=hi")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "post-matric"
    assert "पोस्ट-मैट्रिक" in data["localized_name"]
    assert len(data["documents"]) >= 3
    assert len(data["steps"]) >= 2
    assert len(data["sources"]) >= 1


def test_scheme_checklist(client):
    response = client.get("/api/schemes/post-matric/checklist")
    assert response.status_code == 200
    data = response.json()
    assert "mandatory_documents" in data
    assert "optional_documents" in data
    assert data["total_mandatory"] >= 2
    # Aadhaar is mandatory
    doc_codes = [d["document_code"] for d in data["mandatory_documents"]]
    assert "aadhaar" in doc_codes
