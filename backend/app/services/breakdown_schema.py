from typing import Optional
from pydantic import BaseModel, Field, field_validator


class DepartmentModel(BaseModel):
    model_config = {"extra": "ignore"}


class ADBreakdown(DepartmentModel):
    scene_number: Optional[int] = None
    scene_heading: Optional[str] = None
    int_ext: Optional[str] = None
    day_night: Optional[str] = None
    cast_required: list[str] = Field(default_factory=list)
    extras: list[str] = Field(default_factory=list)
    background_action: list[str] = Field(default_factory=list)
    stunts: list[str] = Field(default_factory=list)
    special_requirements: list[str] = Field(default_factory=list)
    vehicles: list[str] = Field(default_factory=list)
    animals: list[str] = Field(default_factory=list)
    child_actors: list[str] = Field(default_factory=list)
    scene_complexity: Optional[str] = None
    location: Optional[str] = None
    estimated_shooting_considerations: list[str] = Field(default_factory=list)


class DOPBreakdown(DepartmentModel):
    scene: Optional[str] = None
    shot_requirements: list[str] = Field(default_factory=list)
    camera_movement: list[str] = Field(default_factory=list)
    framing: list[str] = Field(default_factory=list)
    lighting_requirements: list[str] = Field(default_factory=list)
    day_night: Optional[str] = None
    natural_artificial_light: list[str] = Field(default_factory=list)
    lens_considerations: list[str] = Field(default_factory=list)
    special_camera_requirements: list[str] = Field(default_factory=list)
    vfx_sfx_considerations: list[str] = Field(default_factory=list)
    practical_lighting: list[str] = Field(default_factory=list)


class GafferBreakdown(DepartmentModel):
    scene: Optional[str] = None
    lighting_requirements: list[str] = Field(default_factory=list)
    practical_lights: list[str] = Field(default_factory=list)
    motivated_lighting: list[str] = Field(default_factory=list)
    day_night: Optional[str] = None
    interior_exterior: Optional[str] = None
    special_lighting: list[str] = Field(default_factory=list)
    power_requirements: list[str] = Field(default_factory=list)
    lighting_equipment_considerations: list[str] = Field(default_factory=list)


class ProductionDesignerBreakdown(DepartmentModel):
    location: Optional[str] = None
    set_requirements: list[str] = Field(default_factory=list)
    set_construction: list[str] = Field(default_factory=list)
    set_dressing: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    period_era: Optional[str] = None
    architecture: list[str] = Field(default_factory=list)
    environment: list[str] = Field(default_factory=list)
    color_style_requirements: list[str] = Field(default_factory=list)
    graphics_signage: list[str] = Field(default_factory=list)
    vehicles: list[str] = Field(default_factory=list)
    special_art_requirements: list[str] = Field(default_factory=list)


class ArtDirectorBreakdown(DepartmentModel):
    construction_requirements: list[str] = Field(default_factory=list)
    set_modifications: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    scenic_work: list[str] = Field(default_factory=list)
    paint: list[str] = Field(default_factory=list)
    carpentry: list[str] = Field(default_factory=list)
    graphics: list[str] = Field(default_factory=list)
    special_builds: list[str] = Field(default_factory=list)
    installation_requirements: list[str] = Field(default_factory=list)
    strike_requirements: list[str] = Field(default_factory=list)


class SetDresserBreakdown(DepartmentModel):
    furniture: list[str] = Field(default_factory=list)
    decorations: list[str] = Field(default_factory=list)
    wall_dressing: list[str] = Field(default_factory=list)
    curtains: list[str] = Field(default_factory=list)
    rugs: list[str] = Field(default_factory=list)
    tables: list[str] = Field(default_factory=list)
    chairs: list[str] = Field(default_factory=list)
    books: list[str] = Field(default_factory=list)
    pictures: list[str] = Field(default_factory=list)
    appliances: list[str] = Field(default_factory=list)
    background_dressing: list[str] = Field(default_factory=list)
    continuity_requirements: list[str] = Field(default_factory=list)


class PropsBreakdown(DepartmentModel):
    hand_props: list[str] = Field(default_factory=list)
    set_props: list[str] = Field(default_factory=list)
    hero_props: list[str] = Field(default_factory=list)
    weapons: list[str] = Field(default_factory=list)
    food_drink: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    electronics: list[str] = Field(default_factory=list)
    special_props: list[str] = Field(default_factory=list)
    prop_continuity: list[str] = Field(default_factory=list)


class WardrobeBreakdown(DepartmentModel):
    character: list[str] = Field(default_factory=list)
    costume: list[str] = Field(default_factory=list)
    costume_changes: list[str] = Field(default_factory=list)
    costume_continuity: list[str] = Field(default_factory=list)
    period_clothing: list[str] = Field(default_factory=list)
    uniforms: list[str] = Field(default_factory=list)
    shoes: list[str] = Field(default_factory=list)
    accessories: list[str] = Field(default_factory=list)
    special_wardrobe: list[str] = Field(default_factory=list)
    dirty_wet_bloodied_costume_requirements: list[str] = Field(default_factory=list)


class SoundBreakdown(DepartmentModel):
    dialogue: list[str] = Field(default_factory=list)
    sound_effects: list[str] = Field(default_factory=list)
    ambient_sound: list[str] = Field(default_factory=list)
    playback: list[str] = Field(default_factory=list)
    phones_radios: list[str] = Field(default_factory=list)
    music: list[str] = Field(default_factory=list)
    vehicles: list[str] = Field(default_factory=list)
    special_recording_considerations: list[str] = Field(default_factory=list)
    noisy_locations: list[str] = Field(default_factory=list)
    difficult_sound_environments: list[str] = Field(default_factory=list)


class ProducerBreakdown(DepartmentModel):
    locations: list[str] = Field(default_factory=list)
    cast_requirements: list[str] = Field(default_factory=list)
    extras: list[str] = Field(default_factory=list)
    special_equipment: list[str] = Field(default_factory=list)
    vehicles: list[str] = Field(default_factory=list)
    stunts: list[str] = Field(default_factory=list)
    vfx_sfx: list[str] = Field(default_factory=list)
    construction: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    wardrobe: list[str] = Field(default_factory=list)
    scheduling_concerns: list[str] = Field(default_factory=list)
    potential_cost_drivers: list[str] = Field(default_factory=list)


class DepartmentBreakdowns(DepartmentModel):
    ad: ADBreakdown = Field(default_factory=ADBreakdown)
    dop: DOPBreakdown = Field(default_factory=DOPBreakdown)
    gaffer: GafferBreakdown = Field(default_factory=GafferBreakdown)
    production_designer: ProductionDesignerBreakdown = Field(default_factory=ProductionDesignerBreakdown)
    art_director: ArtDirectorBreakdown = Field(default_factory=ArtDirectorBreakdown)
    set_dresser: SetDresserBreakdown = Field(default_factory=SetDresserBreakdown)
    props: PropsBreakdown = Field(default_factory=PropsBreakdown)
    wardrobe: WardrobeBreakdown = Field(default_factory=WardrobeBreakdown)
    sound: SoundBreakdown = Field(default_factory=SoundBreakdown)
    producer: ProducerBreakdown = Field(default_factory=ProducerBreakdown)


class SceneBreakdown(BaseModel):
    scene_number: int
    heading: str = Field(..., description="Full slugline, e.g. 'INT. WAREHOUSE - NIGHT'")
    int_ext: str = Field(..., description="'INT', 'EXT', or 'INT/EXT'")
    time_of_day: Optional[str] = Field(None, description="e.g. 'DAY', 'NIGHT', 'CONTINUOUS'")
    location: str
    synopsis: str = Field(..., description="One-sentence summary of what happens in the scene")

    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    costumes: list[str] = Field(default_factory=list)
    departments: list[str] = Field(
        default_factory=list,
        description="Crew departments implicated, e.g. 'AD', 'DOP', 'Props', 'Sound'",
    )
    extras: list[str] = Field(default_factory=list)
    vehicles: list[str] = Field(default_factory=list)
    animals: list[str] = Field(default_factory=list)
    stunts: list[str] = Field(default_factory=list)
    special_requirements: list[str] = Field(default_factory=list)
    scene_complexity: Optional[str] = None
    department_breakdowns: DepartmentBreakdowns = Field(default_factory=DepartmentBreakdowns)

    @field_validator("int_ext")
    @classmethod
    def normalize_int_ext(cls, v: str) -> str:
        v = (v or "").strip().upper()
        if v not in {"INT", "EXT", "INT/EXT"}:
            # Don't hard-fail the whole breakdown over a formatting quirk -
            # normalize to a safe default and keep going.
            return "INT/EXT"
        return v


class BreakdownOutput(BaseModel):
    """Top-level structure the AI must return. Strict: extra/unexpected
    fields from the model are ignored rather than silently trusted."""

    scenes: list[SceneBreakdown]
    all_characters: list[str] = Field(default_factory=list)
    all_locations: list[str] = Field(default_factory=list)
    all_props: list[str] = Field(default_factory=list)
    all_costumes: list[str] = Field(default_factory=list)
    all_vehicles: list[str] = Field(default_factory=list)

    model_config = {"extra": "ignore"}

    @field_validator("scenes")
    @classmethod
    def must_have_scenes(cls, v):
        if not v:
            raise ValueError("Breakdown must contain at least one scene.")
        return v
