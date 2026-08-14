import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import current_app, has_app_context
from pydantic import ValidationError

from app.services.breakdown_schema import BreakdownOutput

# Rough safety ceiling so a huge script doesn't blow past the model's context
# window unexpectedly. A cleaner long-term fix is chunking scenes across
# multiple calls and merging results.
MAX_INPUT_CHARS = 120_000

SYSTEM_PROMPT = """You are a professional film production breakdown team. You read screenplays and produce a precise, structured production breakdown by scene and department.

Return ONLY valid JSON matching this exact shape, with no commentary, no markdown code fences, and no text before or after the JSON:

{
  "scenes": [
    {
      "scene_number": 1,
      "heading": "INT. WAREHOUSE - NIGHT",
      "int_ext": "INT",
      "time_of_day": "NIGHT",
      "location": "Warehouse",
      "synopsis": "One sentence describing what happens.",
      "characters": ["JOHN", "MARY"],
      "props": ["flashlight", "crowbar"],
      "costumes": ["John's leather jacket"],
      "departments": ["AD", "DOP", "Gaffer", "Props", "Sound"],
      "extras": ["warehouse workers"],
      "vehicles": ["pickup truck"],
      "animals": [],
      "stunts": ["fall through window"],
      "special_requirements": ["rain effect"],
      "scene_complexity": "High",
      "department_breakdowns": {
        "ad": {
          "scene_number": 1,
          "scene_heading": "INT. WAREHOUSE - NIGHT",
          "int_ext": "INT",
          "day_night": "NIGHT",
          "cast_required": ["JOHN", "MARY"],
          "extras": [],
          "background_action": ["workers cross behind John"],
          "stunts": [],
          "special_requirements": [],
          "vehicles": [],
          "animals": [],
          "child_actors": [],
          "scene_complexity": "Medium",
          "location": "Warehouse",
          "estimated_shooting_considerations": ["night interior lighting setup"]
        },
        "dop": {
          "scene": "Scene 1",
          "shot_requirements": ["track John through aisles"],
          "camera_movement": ["handheld search movement"],
          "framing": ["tight flashlight closeups"],
          "lighting_requirements": ["low-key warehouse ambience"],
          "day_night": "NIGHT",
          "natural_artificial_light": ["artificial practicals"],
          "lens_considerations": ["wide lens for aisles"],
          "special_camera_requirements": [],
          "vfx_sfx_considerations": [],
          "practical_lighting": ["overhead fluorescents"]
        },
        "gaffer": {
          "scene": "Scene 1",
          "lighting_requirements": ["low-key warehouse ambience"],
          "practical_lights": ["overhead fluorescents"],
          "motivated_lighting": ["flashlight motivates moving beam"],
          "day_night": "NIGHT",
          "interior_exterior": "INT",
          "special_lighting": [],
          "power_requirements": [],
          "lighting_equipment_considerations": []
        },
        "production_designer": {
          "location": "Warehouse",
          "set_requirements": ["industrial storage aisles"],
          "set_construction": [],
          "set_dressing": ["crates", "dusty shelves"],
          "props": ["flashlight", "crowbar"],
          "period_era": "Present day",
          "architecture": ["industrial"],
          "environment": ["dusty", "abandoned"],
          "color_style_requirements": ["cold metal tones"],
          "graphics_signage": [],
          "vehicles": [],
          "special_art_requirements": []
        },
        "art_director": {
          "construction_requirements": [],
          "set_modifications": [],
          "materials": [],
          "scenic_work": [],
          "paint": [],
          "carpentry": [],
          "graphics": [],
          "special_builds": [],
          "installation_requirements": [],
          "strike_requirements": []
        },
        "set_dresser": {
          "furniture": [],
          "decorations": [],
          "wall_dressing": [],
          "curtains": [],
          "rugs": [],
          "tables": [],
          "chairs": [],
          "books": [],
          "pictures": [],
          "appliances": [],
          "background_dressing": ["crates", "dusty shelves"],
          "continuity_requirements": []
        },
        "props": {
          "hand_props": ["flashlight"],
          "set_props": ["crates"],
          "hero_props": ["crowbar"],
          "weapons": [],
          "food_drink": [],
          "phones": [],
          "documents": [],
          "electronics": [],
          "special_props": [],
          "prop_continuity": ["flashlight remains with John"]
        },
        "wardrobe": {
          "character": ["JOHN"],
          "costume": ["leather jacket"],
          "costume_changes": [],
          "costume_continuity": ["jacket continues from previous scene"],
          "period_clothing": [],
          "uniforms": [],
          "shoes": [],
          "accessories": [],
          "special_wardrobe": [],
          "dirty_wet_bloodied_costume_requirements": []
        },
        "sound": {
          "dialogue": ["JOHN whispers"],
          "sound_effects": ["footsteps", "metal creaks"],
          "ambient_sound": ["warehouse hum"],
          "playback": [],
          "phones_radios": [],
          "music": [],
          "vehicles": [],
          "special_recording_considerations": [],
          "noisy_locations": [],
          "difficult_sound_environments": []
        },
        "producer": {
          "locations": ["Warehouse"],
          "cast_requirements": ["JOHN", "MARY"],
          "extras": [],
          "special_equipment": ["camera stabilizer"],
          "vehicles": [],
          "stunts": [],
          "vfx_sfx": [],
          "construction": [],
          "props": ["flashlight", "crowbar"],
          "wardrobe": ["leather jacket"],
          "scheduling_concerns": ["night work"],
          "potential_cost_drivers": ["night lighting package"]
        }
      }
    }
  ],
  "all_characters": ["JOHN", "MARY"],
  "all_locations": ["Warehouse", "Street"],
  "all_props": ["flashlight", "crowbar"],
  "all_costumes": ["John's leather jacket"],
  "all_vehicles": ["pickup truck"]
}

Rules:
- Number scenes sequentially starting at 1, in the order they appear.
- A "scene" is delimited by a slugline (INT./EXT./INT-EXT).
- Track named characters consistently across scenes, even if referred to differently.
- Only include requirements that are explicitly stated or strongly implied by the action description. Do not invent details the script does not support.
- The canonical scene fields are the shared source of truth. Department breakdowns are the same scene interpreted through each department's lens.
- departments should be drawn from: AD, DOP, Gaffer, Production Designer, Art Director, Set Dresser, Props, Wardrobe, Sound, Producer, Stunts, SFX/VFX, Locations, Transport. Only include departments genuinely implicated by the scene.
- Use empty arrays for department fields that have no supported requirements.
- Use scene_complexity values Low, Medium, or High based on cast, extras, locations, stunts, vehicles, animals, child actors, SFX/VFX, night work, construction, sound difficulty, and continuity.
- If the script text appears truncated or incomplete, still break down whatever is present.
"""


class AIServiceError(Exception):
    """Raised when the AI call fails or returns output that cannot be validated."""


def _get_provider_config():
    provider = current_app.config.get("AI_PROVIDER", "gemini")
    api_key = current_app.config.get("AI_API_KEY")

    if not api_key:
        raise AIServiceError(
            "No AI_API_KEY is configured on the server. Set it in your .env file."
        )

    if provider == "anthropic":
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        model = "claude-sonnet-4-6"
        return provider, client, model

    if provider == "gemini":
        model = current_app.config.get("GEMINI_MODEL", "gemini-3.6-flash")
        return provider, api_key, model

    raise AIServiceError(f"Unsupported AI_PROVIDER: '{provider}'")


def _get_max_output_tokens() -> int:
    if not has_app_context():
        return 30000
    return int(current_app.config.get("AI_MAX_OUTPUT_TOKENS", 30000))


def _analyze_with_anthropic(client, model, text_for_prompt: str) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=_get_max_output_tokens(),
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text_for_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def _analyze_with_gemini(api_key: str, model: str, text_for_prompt: str) -> str:
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{quote(model, safe='')}:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": text_for_prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": _get_max_output_tokens(),
            "responseMimeType": "application/json",
        },
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise AIServiceError(
            f"Gemini API request failed with HTTP {e.code}: {error_body}"
        ) from e
    except URLError as e:
        raise AIServiceError(f"Gemini API request failed: {e.reason}") from e

    try:
        data = json.loads(response_body)
        candidates = data.get("candidates") or []
        parts = candidates[0]["content"].get("parts", []) if candidates else []
        raw_output = "".join(part.get("text", "") for part in parts)
    except (KeyError, TypeError, IndexError, json.JSONDecodeError) as e:
        raise AIServiceError(f"Gemini API returned an unexpected response: {e}") from e

    if not raw_output.strip():
        raise AIServiceError("Gemini API returned an empty response.")

    return raw_output


def _extract_json(raw_response_text: str) -> dict:
    """
    LLMs sometimes wrap JSON in markdown fences or add stray text despite
    instructions. Strip fences first, then fall back to grabbing the
    outermost {...} block before giving up.
    """
    text = raw_response_text.strip()

    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError as e:
            raise AIServiceError(
                "AI response was not valid JSON. This often means the response "
                "was truncated while generating the large department breakdown. "
                f"Parser details: {e}"
            ) from e

    raise AIServiceError("AI response did not contain a JSON object.")


def analyze_script(raw_text: str) -> BreakdownOutput:
    """
    Send script text to the configured AI provider and return a validated
    BreakdownOutput. Raises AIServiceError on any failure.
    """
    if not raw_text or not raw_text.strip():
        raise AIServiceError("No script text was provided to analyze.")

    text_for_prompt = raw_text
    truncated = False
    if len(text_for_prompt) > MAX_INPUT_CHARS:
        text_for_prompt = text_for_prompt[:MAX_INPUT_CHARS]
        truncated = True

    provider, client, model = _get_provider_config()

    try:
        if provider == "anthropic":
            raw_output = _analyze_with_anthropic(client, model, text_for_prompt)
        elif provider == "gemini":
            raw_output = _analyze_with_gemini(client, model, text_for_prompt)
        else:
            raise AIServiceError(f"Unsupported AI_PROVIDER: '{provider}'")
    except AIServiceError:
        raise
    except Exception as e:
        raise AIServiceError(f"AI provider request failed: {e}") from e

    parsed_json = _extract_json(raw_output)

    try:
        breakdown = BreakdownOutput.model_validate(parsed_json)
    except ValidationError as e:
        raise AIServiceError(f"AI response failed schema validation: {e}") from e

    if truncated:
        breakdown_dict = breakdown.model_dump()
        breakdown_dict["_truncated"] = True
        breakdown = BreakdownOutput.model_validate(
            {k: v for k, v in breakdown_dict.items() if k != "_truncated"}
        )

    return breakdown
