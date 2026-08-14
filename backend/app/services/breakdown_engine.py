from collections import defaultdict

from app.services.breakdown_schema import BreakdownOutput

DEPARTMENT_VIEW_KEYS = [
    "ad",
    "dop",
    "gaffer",
    "production_designer",
    "art_director",
    "set_dresser",
    "props",
    "wardrobe",
    "sound",
    "producer",
]

DEPARTMENT_LABELS = {
    "ad": "AD",
    "dop": "DOP",
    "gaffer": "Gaffer",
    "production_designer": "Production Designer",
    "art_director": "Art Director",
    "set_dresser": "Set Dresser",
    "props": "Props",
    "wardrobe": "Wardrobe",
    "sound": "Sound",
    "producer": "Producer",
}

DEPARTMENT_ALIASES = {
    "Camera": "DOP",
    "Lighting/Gaffer": "Gaffer",
    "Art/Props": "Props",
    "Wardrobe/Costume": "Wardrobe",
}


def build_breakdown(ai_output: BreakdownOutput) -> dict:
    """
    Take validated AI output and structure it into a scene-first breakdown
    with department-specific views for production users.
    """
    scenes = [_normalize_scene(s.model_dump()) for s in ai_output.scenes]

    by_department = defaultdict(list)
    for scene in scenes:
        departments = scene.get("departments", []) + scene.get("_legacy_departments", [])
        seen_departments = set()
        for dept in departments:
            label = DEPARTMENT_ALIASES.get(dept, dept)
            if label not in seen_departments:
                by_department[label].append(scene["scene_number"])
                seen_departments.add(label)
            if label != dept:
                if dept not in seen_departments:
                    by_department[dept].append(scene["scene_number"])
                    seen_departments.add(dept)

    views = {key: _build_department_view(scenes, key) for key in DEPARTMENT_VIEW_KEYS}
    views["ad"].update(_build_ad_rollups(scenes))
    views["dop"].update(_build_dop_rollups(scenes))
    views["gaffer"].update(_build_gaffer_rollups(scenes, by_department))
    views["producer"].update(_build_producer_rollups(ai_output, scenes, by_department))
    public_scenes = [
        {key: value for key, value in scene.items() if not key.startswith("_")}
        for scene in scenes
    ]

    return {
        "architecture": {
            "source": "SCREENPLAY",
            "canonical_stage": "Scene Breakdown",
            "departments": [
                {
                    "key": "production_management",
                    "label": "Production Management",
                    "roles": ["AD", "Producer"],
                },
                {
                    "key": "camera",
                    "label": "Camera",
                    "roles": ["DOP", "Gaffer"],
                },
                {
                    "key": "art_dept",
                    "label": "Art Dept",
                    "roles": [
                        "Production Designer",
                        "Art Director",
                        "Set Dresser",
                        "Props",
                    ],
                },
                {"key": "wardrobe", "label": "Wardrobe", "roles": ["Wardrobe"]},
                {"key": "sound", "label": "Sound", "roles": ["Sound"]},
            ],
        },
        "scenes": public_scenes,
        "summary": _build_summary(ai_output, scenes),
        "by_department": dict(by_department),
        "views": views,
    }


def _normalize_scene(scene: dict) -> dict:
    departments = scene.get("departments") or []
    scene["_legacy_departments"] = departments
    scene["departments"] = [DEPARTMENT_ALIASES.get(dept, dept) for dept in departments]
    scene["department_breakdowns"] = scene.get("department_breakdowns") or {}
    _hydrate_department_defaults(scene)
    return scene


def _hydrate_department_defaults(scene: dict) -> None:
    breakdowns = scene["department_breakdowns"]

    breakdowns.setdefault("ad", {})
    breakdowns["ad"] = {
        "scene_number": scene["scene_number"],
        "scene_heading": scene["heading"],
        "int_ext": scene["int_ext"],
        "day_night": scene.get("time_of_day"),
        "cast_required": scene.get("characters", []),
        "extras": scene.get("extras", []),
        "stunts": scene.get("stunts", []),
        "special_requirements": scene.get("special_requirements", []),
        "vehicles": scene.get("vehicles", []),
        "animals": scene.get("animals", []),
        "scene_complexity": scene.get("scene_complexity"),
        "location": scene.get("location"),
        **breakdowns["ad"],
    }

    breakdowns.setdefault("dop", {})
    breakdowns["dop"] = {
        "scene": f"Scene {scene['scene_number']}",
        "day_night": scene.get("time_of_day"),
        **breakdowns["dop"],
    }

    breakdowns.setdefault("gaffer", {})
    breakdowns["gaffer"] = {
        "scene": f"Scene {scene['scene_number']}",
        "day_night": scene.get("time_of_day"),
        "interior_exterior": scene.get("int_ext"),
        **breakdowns["gaffer"],
    }

    breakdowns.setdefault("production_designer", {})
    breakdowns["production_designer"] = {
        "location": scene.get("location"),
        "props": scene.get("props", []),
        "vehicles": scene.get("vehicles", []),
        **breakdowns["production_designer"],
    }

    breakdowns.setdefault("props", {})
    breakdowns["props"] = {
        "hand_props": scene.get("props", []),
        **breakdowns["props"],
    }

    breakdowns.setdefault("wardrobe", {})
    breakdowns["wardrobe"] = {
        "character": scene.get("characters", []),
        "costume": scene.get("costumes", []),
        **breakdowns["wardrobe"],
    }

    breakdowns.setdefault("sound", {})
    breakdowns.setdefault("art_director", {})
    breakdowns.setdefault("set_dresser", {})

    breakdowns.setdefault("producer", {})
    breakdowns["producer"] = {
        "locations": [scene.get("location")] if scene.get("location") else [],
        "cast_requirements": scene.get("characters", []),
        "extras": scene.get("extras", []),
        "vehicles": scene.get("vehicles", []),
        "stunts": scene.get("stunts", []),
        "props": scene.get("props", []),
        "wardrobe": scene.get("costumes", []),
        "potential_cost_drivers": _cost_drivers_for_scene(scene),
        **breakdowns["producer"],
    }


def _cost_drivers_for_scene(scene: dict) -> list[str]:
    drivers = []
    if scene.get("time_of_day") == "NIGHT":
        drivers.append("Night shooting or night-for-night lighting")
    if scene.get("extras"):
        drivers.append("Extras/background performers")
    if scene.get("vehicles"):
        drivers.append("Vehicles")
    if scene.get("animals"):
        drivers.append("Animals")
    if scene.get("stunts"):
        drivers.append("Stunts")
    if scene.get("special_requirements"):
        drivers.extend(scene["special_requirements"])
    if scene.get("scene_complexity") == "High":
        drivers.append("High scene complexity")
    return drivers


def _build_summary(ai_output: BreakdownOutput, scenes: list[dict]) -> dict:
    return {
        "total_scenes": len(scenes),
        "characters": ai_output.all_characters,
        "locations": ai_output.all_locations,
        "props": ai_output.all_props,
        "costumes": ai_output.all_costumes,
        "vehicles": ai_output.all_vehicles,
        "department_count": len(DEPARTMENT_VIEW_KEYS),
    }


def _build_department_view(scenes: list[dict], key: str) -> dict:
    return {
        "label": DEPARTMENT_LABELS[key],
        "scenes": [
            {
                "scene_number": scene["scene_number"],
                "heading": scene["heading"],
                "location": scene["location"],
                "int_ext": scene["int_ext"],
                "time_of_day": scene.get("time_of_day"),
                "scene_complexity": scene.get("scene_complexity"),
                "breakdown": scene["department_breakdowns"].get(key, {}),
            }
            for scene in scenes
        ],
    }


def _build_ad_rollups(scenes: list[dict]) -> dict:
    int_ext_counts = defaultdict(int)
    day_night_counts = defaultdict(int)
    scenes_by_character = defaultdict(list)

    for scene in scenes:
        int_ext_counts[scene["int_ext"]] += 1
        if scene.get("time_of_day"):
            day_night_counts[scene["time_of_day"]] += 1
        for character in scene.get("characters", []):
            scenes_by_character[character].append(scene["scene_number"])

    return {
        "scene_order": [
            {
                "scene_number": s["scene_number"],
                "heading": s["heading"],
                "characters": s.get("characters", []),
                "scene_complexity": s.get("scene_complexity"),
            }
            for s in scenes
        ],
        "int_ext_breakdown": dict(int_ext_counts),
        "day_night_breakdown": dict(day_night_counts),
        "scenes_by_character": dict(scenes_by_character),
    }


def _build_dop_rollups(scenes: list[dict]) -> dict:
    scenes_by_location = defaultdict(list)

    for scene in scenes:
        scenes_by_location[scene["location"]].append({
            "scene_number": scene["scene_number"],
            "heading": scene["heading"],
            "int_ext": scene["int_ext"],
            "time_of_day": scene.get("time_of_day"),
        })

    return {"scenes_by_location": dict(scenes_by_location)}


def _build_gaffer_rollups(scenes: list[dict], by_department: dict) -> dict:
    lighting_scenes = by_department.get("Gaffer", [])

    lighting_conditions = []
    for scene in scenes:
        if scene["scene_number"] in lighting_scenes or not lighting_scenes:
            lighting_conditions.append({
                "scene_number": scene["scene_number"],
                "int_ext": scene["int_ext"],
                "time_of_day": scene.get("time_of_day"),
                "location": scene["location"],
            })

    return {
        "flagged_scenes": lighting_scenes,
        "lighting_conditions": lighting_conditions,
    }


def _build_producer_rollups(
    ai_output: BreakdownOutput,
    scenes: list[dict],
    by_department: dict,
) -> dict:
    return {
        "total_scenes": len(scenes),
        "total_characters": len(ai_output.all_characters),
        "total_locations": len(ai_output.all_locations),
        "total_props": len(ai_output.all_props),
        "total_costumes": len(ai_output.all_costumes),
        "total_vehicles": len(ai_output.all_vehicles),
        "department_scene_counts": {
            dept: len(scene_numbers) for dept, scene_numbers in by_department.items()
        },
        "cost_drivers": [
            {
                "scene_number": scene["scene_number"],
                "heading": scene["heading"],
                "drivers": scene["department_breakdowns"]["producer"].get(
                    "potential_cost_drivers", []
                ),
            }
            for scene in scenes
            if scene["department_breakdowns"]["producer"].get("potential_cost_drivers")
        ],
    }
