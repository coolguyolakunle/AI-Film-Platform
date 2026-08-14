import copy

import pytest
from pydantic import ValidationError

from app.services.breakdown_schema import BreakdownOutput
from app.services.breakdown_engine import build_breakdown

SAMPLE_AI_JSON = {
    "scenes": [
        {
            "scene_number": 1,
            "heading": "INT. WAREHOUSE - NIGHT",
            "int_ext": "INT",
            "time_of_day": "NIGHT",
            "location": "Warehouse",
            "synopsis": "John searches the warehouse with a flashlight.",
            "characters": ["JOHN"],
            "props": ["flashlight"],
            "costumes": ["John's leather jacket"],
            "departments": ["Camera", "Lighting/Gaffer"],
        },
        {
            "scene_number": 2,
            "heading": "EXT. STREET - DAY",
            "int_ext": "EXT",
            "time_of_day": "DAY",
            "location": "Street",
            "synopsis": "Mary walks down the street.",
            "characters": ["MARY"],
            "props": [],
            "costumes": [],
            "departments": ["Camera"],
        },
    ],
    "all_characters": ["JOHN", "MARY"],
    "all_locations": ["Warehouse", "Street"],
    "all_props": ["flashlight"],
    "all_costumes": ["John's leather jacket"],
}


def test_schema_validates_good_output():
    output = BreakdownOutput.model_validate(SAMPLE_AI_JSON)
    assert len(output.scenes) == 2
    assert output.scenes[0].scene_number == 1


def test_schema_rejects_empty_scenes():
    bad = copy.deepcopy(SAMPLE_AI_JSON)
    bad["scenes"] = []
    with pytest.raises(ValidationError):
        BreakdownOutput.model_validate(bad)


def test_schema_normalizes_bad_int_ext():
    bad = copy.deepcopy(SAMPLE_AI_JSON)
    bad["scenes"][0]["int_ext"] = "somewhere weird"
    output = BreakdownOutput.model_validate(bad)
    assert output.scenes[0].int_ext == "INT/EXT"


def test_schema_ignores_extra_fields():
    extra = copy.deepcopy(SAMPLE_AI_JSON)
    extra["unexpected_field"] = "should be ignored"
    output = BreakdownOutput.model_validate(extra)
    assert not hasattr(output, "unexpected_field")


def test_breakdown_engine_builds_summary():
    output = BreakdownOutput.model_validate(SAMPLE_AI_JSON)
    result = build_breakdown(output)
    assert result["summary"]["total_scenes"] == 2
    assert "JOHN" in result["summary"]["characters"]


def test_breakdown_engine_by_department():
    output = BreakdownOutput.model_validate(SAMPLE_AI_JSON)
    result = build_breakdown(output)
    assert result["by_department"]["Camera"] == [1, 2]
    assert result["by_department"]["Lighting/Gaffer"] == [1]


def test_breakdown_engine_ad_view():
    output = BreakdownOutput.model_validate(SAMPLE_AI_JSON)
    result = build_breakdown(output)
    ad = result["views"]["ad"]
    assert ad["int_ext_breakdown"] == {"INT": 1, "EXT": 1}
    assert ad["scenes_by_character"]["JOHN"] == [1]


def test_breakdown_engine_dop_view():
    output = BreakdownOutput.model_validate(SAMPLE_AI_JSON)
    result = build_breakdown(output)
    dop = result["views"]["dop"]
    assert "Warehouse" in dop["scenes_by_location"]
    assert dop["scenes_by_location"]["Warehouse"][0]["scene_number"] == 1


def test_breakdown_engine_gaffer_view():
    output = BreakdownOutput.model_validate(SAMPLE_AI_JSON)
    result = build_breakdown(output)
    gaffer = result["views"]["gaffer"]
    assert gaffer["flagged_scenes"] == [1]


def test_breakdown_engine_producer_view():
    output = BreakdownOutput.model_validate(SAMPLE_AI_JSON)
    result = build_breakdown(output)
    producer = result["views"]["producer"]
    assert producer["total_scenes"] == 2
    assert producer["total_characters"] == 2
    assert producer["department_scene_counts"]["Camera"] == 2
