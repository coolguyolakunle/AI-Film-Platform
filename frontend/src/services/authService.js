import api from "./api";

export async function register({ name, email, password }) {
  const { data } = await api.post("/auth/register", { name, email, password });
  return data; // { token, user }
}

export async function login({ email, password }) {
  const { data } = await api.post("/auth/login", { email, password });
  return data; // { token, user }
}

export async function loginWithGoogle(idToken) {
  const { data } = await api.post("/auth/google", { id_token: idToken });
  return data; // { token, user }
}

export async function fetchGoogleConfig() {
  const { data } = await api.get("/auth/google/config");
  return data; // { configured, client_id }
}

export async function fetchCurrentUser() {
  const { data } = await api.get("/auth/me");
  return data.user;
}

export async function fetchProfile() {
  const { data } = await api.get("/auth/profile");
  return data; // { user, production_roles, experience_levels }
}

export async function updateProfile(payload) {
  const { data } = await api.put("/auth/profile", payload);
  return data.user;
}

export function extractErrorMessage(error, fallback = "Something went wrong. Please try again.") {
  return error?.response?.data?.message || fallback;
}
