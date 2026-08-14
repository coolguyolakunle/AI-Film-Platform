import { createContext, useState, useEffect, useCallback } from "react";
import {
  login as loginRequest,
  register as registerRequest,
  loginWithGoogle as googleLoginRequest,
  fetchCurrentUser,
  updateProfile as updateProfileRequest,
} from "../services/authService";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On first load, if we have a token, try to restore the session.
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    fetchCurrentUser()
      .then(setUser)
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (credentials) => {
    const { token, user: loggedInUser } = await loginRequest(credentials);
    localStorage.setItem("token", token);
    setUser(loggedInUser);
    return loggedInUser;
  }, []);

  const register = useCallback(async (payload) => {
    const { token, user: newUser } = await registerRequest(payload);
    localStorage.setItem("token", token);
    setUser(newUser);
    return newUser;
  }, []);

  const loginWithGoogle = useCallback(async (idToken) => {
    const { token, user: loggedInUser } = await googleLoginRequest(idToken);
    localStorage.setItem("token", token);
    setUser(loggedInUser);
    return loggedInUser;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (payload) => {
    const updatedUser = await updateProfileRequest(payload);
    setUser(updatedUser);
    return updatedUser;
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    loginWithGoogle,
    updateProfile,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
