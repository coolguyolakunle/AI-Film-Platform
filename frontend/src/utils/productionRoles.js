export const PRODUCTION_ROLES = [
  { key: "ad", label: "AD", department: "Production Management" },
  { key: "producer", label: "Producer", department: "Production Management" },
  { key: "dop", label: "DOP", department: "Camera" },
  { key: "gaffer", label: "Gaffer", department: "Camera" },
  { key: "production_designer", label: "Production Designer", department: "Art Dept" },
  { key: "art_director", label: "Art Director", department: "Art Dept" },
  { key: "set_dresser", label: "Set Dresser", department: "Art Dept" },
  { key: "props", label: "Props", department: "Art Dept" },
  { key: "wardrobe", label: "Wardrobe", department: "Wardrobe" },
  { key: "sound", label: "Sound", department: "Sound" },
];

export const EXPERIENCE_LEVELS = [
  { key: "student", label: "Student" },
  { key: "emerging", label: "Emerging" },
  { key: "professional", label: "Professional" },
  { key: "veteran", label: "Veteran" },
];

export function getRoleLabel(roleKey) {
  return PRODUCTION_ROLES.find((role) => role.key === roleKey)?.label || "Production";
}
