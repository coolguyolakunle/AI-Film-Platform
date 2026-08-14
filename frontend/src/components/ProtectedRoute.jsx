import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import LoadingSpinner from "../components/LoadingSpinner.jsx";

export default function ProtectedRoute({ children }) {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) return <LoadingSpinner label="Checking session..." />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!user?.profile_completed && location.pathname !== "/profile/setup") {
    return <Navigate to="/profile/setup" replace />;
  }

  return children;
}
