import { useCallback, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";

import { useFetch } from "../hooks/useFetch";
import { useAuth } from "../hooks/useAuth";
import { getBreakdown, downloadBreakdownExport } from "../services/breakdownService";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import Button from "../components/Button.jsx";
import { getRoleLabel } from "../utils/productionRoles";

const TABS = [
  { key: "scenes", label: "Scenes" },
  { key: "ad", label: "AD" },
  { key: "dop", label: "DOP" },
  { key: "gaffer", label: "Gaffer" },
  { key: "production_designer", label: "Designer" },
  { key: "art_director", label: "Art Dir" },
  { key: "set_dresser", label: "Set Dresser" },
  { key: "props", label: "Props" },
  { key: "wardrobe", label: "Wardrobe" },
  { key: "sound", label: "Sound" },
  { key: "producer", label: "Producer" },
];

const FIELD_LABELS = {
  scene_number: "Scene number",
  scene_heading: "Scene heading",
  int_ext: "INT/EXT",
  day_night: "Day/Night",
  cast_required: "Cast required",
  background_action: "Background action",
  scene_complexity: "Scene complexity",
  estimated_shooting_considerations: "Shooting considerations",
  shot_requirements: "Shot requirements",
  camera_movement: "Camera movement",
  lighting_requirements: "Lighting requirements",
  natural_artificial_light: "Natural/artificial light",
  lens_considerations: "Lens considerations",
  special_camera_requirements: "Special camera requirements",
  vfx_sfx_considerations: "VFX/SFX considerations",
  practical_lighting: "Practical lighting",
  practical_lights: "Practical lights",
  motivated_lighting: "Motivated lighting",
  interior_exterior: "Interior/exterior",
  special_lighting: "Special lighting",
  power_requirements: "Power requirements",
  lighting_equipment_considerations: "Equipment considerations",
  set_requirements: "Set requirements",
  set_construction: "Set construction",
  set_dressing: "Set dressing",
  period_era: "Period/era",
  color_style_requirements: "Color/style",
  graphics_signage: "Graphics/signage",
  special_art_requirements: "Special art",
  construction_requirements: "Construction",
  set_modifications: "Set modifications",
  scenic_work: "Scenic work",
  special_builds: "Special builds",
  installation_requirements: "Installation",
  strike_requirements: "Strike",
  wall_dressing: "Wall dressing",
  background_dressing: "Background dressing",
  continuity_requirements: "Continuity",
  hand_props: "Hand props",
  set_props: "Set props",
  hero_props: "Hero props",
  food_drink: "Food/drink",
  special_props: "Special props",
  prop_continuity: "Prop continuity",
  costume_changes: "Costume changes",
  costume_continuity: "Costume continuity",
  period_clothing: "Period clothing",
  special_wardrobe: "Special wardrobe",
  dirty_wet_bloodied_costume_requirements: "Dirty/wet/bloodied",
  sound_effects: "Sound effects",
  ambient_sound: "Ambient sound",
  phones_radios: "Phones/radios",
  special_recording_considerations: "Recording considerations",
  noisy_locations: "Noisy locations",
  difficult_sound_environments: "Difficult environments",
  cast_requirements: "Cast requirements",
  special_equipment: "Special equipment",
  vfx_sfx: "VFX/SFX",
  scheduling_concerns: "Scheduling concerns",
  potential_cost_drivers: "Potential cost drivers",
};

export default function BreakdownView() {
  const { scriptId } = useParams();
  const { user } = useAuth();
  const fetcher = useCallback(() => getBreakdown(scriptId), [scriptId]);
  const { data: breakdown, loading, error } = useFetch(fetcher, [scriptId]);

  const defaultRoleTab = user?.production_role || "scenes";
  const [activeTab, setActiveTab] = useState(defaultRoleTab);
  const [showFullView, setShowFullView] = useState(false);
  const [exportingFormat, setExportingFormat] = useState(null);
  const [exportError, setExportError] = useState("");

  const visibleTabs = useMemo(() => {
    if (showFullView || !user?.production_role) return TABS;
    return TABS.filter((tab) => tab.key === "scenes" || tab.key === user.production_role);
  }, [showFullView, user?.production_role]);

  const handleFullViewToggle = () => {
    const nextFullView = !showFullView;
    setShowFullView(nextFullView);
    if (!nextFullView && user?.production_role) {
      setActiveTab(user.production_role);
    }
  };

  const handleExport = async (format) => {
    setExportingFormat(format);
    setExportError("");
    try {
      await downloadBreakdownExport(scriptId, format, `breakdown.${format}`);
    } catch (err) {
      setExportError("Export failed. Please try again.");
    } finally {
      setExportingFormat(null);
    }
  };

  if (loading) return <LoadingSpinner label="Loading breakdown..." />;

  if (error || !breakdown) {
    return (
      <EmptyState
        title="No breakdown yet"
        body="This script doesn't have a breakdown yet. Go back to the project and click Analyze to generate one."
      />
    );
  }

  const data = breakdown.ai_output_json;
  if (breakdown.status === "failed") {
    return (
      <EmptyState
        title="Analysis failed"
        body={data?.error || "The AI provider could not complete the breakdown."}
        tone="error"
      />
    );
  }

  if (!data) {
    return (
      <EmptyState
        title="Breakdown processing"
        body={`Breakdown status: ${breakdown.status}. Check back once analysis finishes.`}
      />
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-10">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <Link to={-1} className="text-sm font-medium text-brand-600 hover:underline">
            Back
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-gray-900">Script Breakdown</h1>
          <p className="mt-2 text-sm text-gray-500">
            {data.summary.total_scenes} scene{data.summary.total_scenes === 1 ? "" : "s"} |{" "}
            {data.summary.characters.length} character{data.summary.characters.length === 1 ? "" : "s"} |{" "}
            {data.summary.locations.length} location{data.summary.locations.length === 1 ? "" : "s"} |{" "}
            {data.summary.department_count || Object.keys(data.views || {}).length} departments
          </p>
          {user?.production_role && (
            <p className="mt-1 text-sm text-brand-700">
              Showing your {getRoleLabel(user.production_role)} breakdown first.
            </p>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2 sm:flex">
          {user?.production_role && (
            <Button variant="secondary" onClick={handleFullViewToggle}>
              {showFullView ? "My View" : "Full View"}
            </Button>
          )}
          <Button
            variant="secondary"
            loading={exportingFormat === "pdf"}
            onClick={() => handleExport("pdf")}
          >
            Export PDF
          </Button>
          <Button
            variant="secondary"
            loading={exportingFormat === "csv"}
            onClick={() => handleExport("csv")}
          >
            Export CSV
          </Button>
        </div>
      </div>

      {exportError && (
        <div className="mt-3 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{exportError}</div>
      )}

      {data.architecture && <ArchitectureBand architecture={data.architecture} />}

      <div className="mt-6 flex gap-1 overflow-x-auto border-b border-gray-200">
        {visibleTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`whitespace-nowrap px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "border-b-2 border-brand-600 text-brand-700"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {activeTab === "scenes" ? (
          <ScenesTab scenes={data.scenes} />
        ) : (
          <DepartmentTab view={data.views?.[activeTab]} />
        )}
      </div>
    </div>
  );
}

function EmptyState({ title, body, tone = "default" }) {
  return (
    <div className="mx-auto max-w-2xl px-6 py-16 text-center text-gray-500">
      <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
      <p className={`mt-2 text-sm ${tone === "error" ? "text-red-600" : "text-gray-500"}`}>
        {body}
      </p>
    </div>
  );
}

function Card({ children, className = "" }) {
  return (
    <div className={`rounded-lg border border-gray-200 bg-white p-4 sm:p-5 ${className}`}>{children}</div>
  );
}

function Tag({ children }) {
  if (!children) return null;
  return (
    <span className="inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
      {children}
    </span>
  );
}

function ArchitectureBand({ architecture }) {
  return (
    <div className="mt-6 rounded-lg border border-gray-200 bg-gray-50 p-3 sm:p-4">
      <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase text-gray-400">
        <span>{architecture.source}</span>
        <span>-&gt;</span>
        <span>{architecture.canonical_stage}</span>
      </div>
      <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {architecture.departments.map((department) => (
          <div key={department.key} className="rounded-lg bg-white p-3">
            <p className="text-sm font-medium text-gray-900">{department.label}</p>
            <div className="mt-2 flex flex-wrap gap-1">
              {department.roles.map((role) => (
                <Tag key={role}>{role}</Tag>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScenesTab({ scenes }) {
  return (
    <div className="flex flex-col gap-4">
      {scenes.map((scene) => (
        <Card key={scene.scene_number}>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase text-gray-400">
                Scene {scene.scene_number}
              </p>
              <h3 className="mt-1 font-medium text-gray-900">{scene.heading}</h3>
              <p className="mt-1 text-sm text-gray-600">{scene.synopsis}</p>
            </div>
            <div className="flex gap-2">
              <Tag>{scene.int_ext}</Tag>
              <Tag>{scene.time_of_day}</Tag>
              <Tag>{scene.scene_complexity}</Tag>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-5">
            <SceneField label="Cast" items={scene.characters} />
            <SceneField label="Extras" items={scene.extras} />
            <SceneField label="Props" items={scene.props} />
            <SceneField label="Wardrobe" items={scene.costumes} />
            <SceneField label="Departments" items={scene.departments} />
          </div>
        </Card>
      ))}
    </div>
  );
}

function SceneField({ label, items }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-400">{label}</p>
      {items && items.length > 0 ? (
        <div className="mt-1 flex flex-wrap gap-1">
          {items.map((item) => (
            <Tag key={item}>{item}</Tag>
          ))}
        </div>
      ) : (
        <p className="mt-1 text-xs text-gray-300">-</p>
      )}
    </div>
  );
}

function DepartmentTab({ view }) {
  if (!view) {
    return <EmptyState title="No department view" body="This breakdown does not include that department yet." />;
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold text-gray-900">{view.label}</h2>
      {view.scenes.map((scene) => (
        <Card key={`${view.label}-${scene.scene_number}`}>
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase text-gray-400">
                Scene {scene.scene_number}
              </p>
              <h3 className="mt-1 font-medium text-gray-900">{scene.heading}</h3>
              <p className="mt-1 text-sm text-gray-500">{scene.location}</p>
            </div>
            <div className="flex gap-2">
              <Tag>{scene.int_ext}</Tag>
              <Tag>{scene.time_of_day}</Tag>
              <Tag>{scene.scene_complexity}</Tag>
            </div>
          </div>
          <DepartmentFields breakdown={scene.breakdown} />
        </Card>
      ))}
    </div>
  );
}

function DepartmentFields({ breakdown }) {
  const entries = Object.entries(breakdown || {}).filter(([, value]) => {
    if (Array.isArray(value)) return value.length > 0;
    return value !== null && value !== undefined && value !== "";
  });

  if (entries.length === 0) {
    return <p className="mt-4 text-sm text-gray-400">No supported requirements found.</p>;
  }

  return (
    <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {entries.map(([key, value]) => (
        <div key={key} className="border-t border-gray-100 pt-3">
          <p className="text-xs font-medium text-gray-400">{FIELD_LABELS[key] || titleize(key)}</p>
          {Array.isArray(value) ? (
            <div className="mt-1 flex flex-wrap gap-1">
              {value.map((item) => (
                <Tag key={item}>{item}</Tag>
              ))}
            </div>
          ) : (
            <p className="mt-1 text-sm text-gray-700">{value}</p>
          )}
        </div>
      ))}
    </div>
  );
}

function titleize(key) {
  return key
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

