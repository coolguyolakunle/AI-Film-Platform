import json
import pytest

from app import create_app
from app.services import ai_service
from app.services.ai_service import AIServiceError


class _FakeGeminiResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps({
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "scenes": [
                                        {
                                            "scene_number": 1,
                                            "heading": "INT. WAREHOUSE - NIGHT",
                                            "int_ext": "INT",
                                            "time_of_day": "NIGHT",
                                            "location": "Warehouse",
                                            "synopsis": "John searches the warehouse.",
                                            "characters": ["JOHN"],
                                            "props": ["flashlight"],
                                            "costumes": [],
                                            "departments": ["Camera"],
                                        }
                                    ],
                                    "all_characters": ["JOHN"],
                                    "all_locations": ["Warehouse"],
                                    "all_props": ["flashlight"],
                                    "all_costumes": [],
                                })
                            }
                        ]
                    }
                }
            ]
        }).encode("utf-8")


def test_gemini_request_returns_candidate_text(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["api_key"] = request.headers["X-goog-api-key"]
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return _FakeGeminiResponse()

    monkeypatch.setattr(ai_service, "urlopen", fake_urlopen)

    raw_output = ai_service._analyze_with_gemini(
        "test-api-key",
        "gemini-3.6-flash",
        "INT. WAREHOUSE - NIGHT\nJohn searches.",
    )

    parsed = json.loads(raw_output)
    assert parsed["scenes"][0]["heading"] == "INT. WAREHOUSE - NIGHT"
    assert captured["url"].endswith("/models/gemini-3.6-flash:generateContent")
    assert captured["api_key"] == "test-api-key"
    assert captured["timeout"] == 120
    assert captured["payload"]["generationConfig"]["responseMimeType"] == "application/json"


def test_gemini_config_accepts_auth_api_key():
    app = create_app("testing")
    app.config["AI_PROVIDER"] = "gemini"
    app.config["AI_API_KEY"] = "AQ.Ab8RN6JaK5b-test-key"

    with app.app_context():
        provider, api_key, model = ai_service._get_provider_config()

    assert provider == "gemini"
    assert api_key.startswith("AQ.")
    assert model == app.config["GEMINI_MODEL"]
