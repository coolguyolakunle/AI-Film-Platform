import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Button from "../components/Button.jsx";
import { useAuth } from "../hooks/useAuth";
import { extractErrorMessage } from "../services/authService";
import { EXPERIENCE_LEVELS, PRODUCTION_ROLES } from "../utils/productionRoles";

export default function ProfileSetup() {
  const { user, updateProfile } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState(user?.name || "");
  const [company, setCompany] = useState(user?.company || "");
  const [productionRole, setProductionRole] = useState(user?.production_role || "ad");
  const [experienceLevel, setExperienceLevel] = useState(user?.experience_level || "professional");
  const [additionalRoles, setAdditionalRoles] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleAdditionalRoleToggle = (roleKey) => {
    setAdditionalRoles((current) =>
      current.includes(roleKey)
        ? current.filter((key) => key !== roleKey)
        : [...current, roleKey],
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await updateProfile({
        name,
        company,
        production_role: productionRole,
        experience_level: experienceLevel,
        additional_roles: additionalRoles,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(extractErrorMessage(err, "Could not save your profile."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-10">
      <div className="mb-6 sm:mb-8">
        <p className="text-sm font-medium text-brand-600">Profile setup</p>
        <h1 className="mt-2 text-2xl font-semibold text-gray-900">Tell us what you do</h1>
        <p className="mt-2 max-w-2xl text-sm text-gray-500">
          Your profile controls which breakdown view opens first after a script is analyzed.
        </p>
      </div>

      {error && (
        <div className="mb-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5 sm:space-y-8">
        <section className="rounded-lg border border-gray-200 bg-white p-4 sm:p-5">
          <h2 className="text-base font-semibold text-gray-900">Identity</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-gray-700">Name</span>
              <input
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-gray-700">Company</span>
              <input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Optional"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </label>
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-4 sm:p-5">
          <h2 className="text-base font-semibold text-gray-900">Primary role</h2>
          <div className="mt-4 grid gap-2 sm:grid-cols-2 sm:gap-3 lg:grid-cols-3">
            {PRODUCTION_ROLES.map((role) => (
              <button
                type="button"
                key={role.key}
                onClick={() => setProductionRole(role.key)}
                className={`rounded-lg border p-3 text-left transition-colors sm:p-4 ${
                  productionRole === role.key
                    ? "border-brand-600 bg-brand-50"
                    : "border-gray-200 bg-white hover:border-gray-300"
                }`}
              >
                <span className="block text-sm font-semibold text-gray-900">{role.label}</span>
                <span className="mt-1 block text-xs text-gray-500">{role.department}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-4 sm:p-5">
          <h2 className="text-base font-semibold text-gray-900">Additional roles</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {PRODUCTION_ROLES.filter((role) => role.key !== productionRole).map((role) => (
              <label
                key={role.key}
                className="flex cursor-pointer items-center gap-2 rounded-full border border-gray-200 px-3 py-1.5 text-sm text-gray-700"
              >
                <input
                  type="checkbox"
                  checked={additionalRoles.includes(role.key)}
                  onChange={() => handleAdditionalRoleToggle(role.key)}
                  className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                />
                {role.label}
              </label>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-4 sm:p-5">
          <h2 className="text-base font-semibold text-gray-900">Experience level</h2>
          <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
            {EXPERIENCE_LEVELS.map((level) => (
              <button
                type="button"
                key={level.key}
                onClick={() => setExperienceLevel(level.key)}
                className={`rounded-lg border px-4 py-3 text-sm font-medium transition-colors ${
                  experienceLevel === level.key
                    ? "border-brand-600 bg-brand-50 text-brand-700"
                    : "border-gray-200 bg-white text-gray-700 hover:border-gray-300"
                }`}
              >
                {level.label}
              </button>
            ))}
          </div>
        </section>

        <div className="flex justify-end">
          <Button type="submit" loading={saving} className="w-full sm:w-auto">
            Save profile
          </Button>
        </div>
      </form>
    </div>
  );
}
