from fastapi.testclient import TestClient

from app.core.config import settings


def test_test_endpoint(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/utils/test/")
    assert r.status_code == 200
    assert r.json() == {"message": "hello world"}
