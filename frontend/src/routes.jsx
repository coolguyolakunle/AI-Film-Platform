import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import UploadScript from "./pages/UploadScript.jsx";
import BreakdownView from "./pages/BreakdownView.jsx";
import ProjectDetail from "./pages/ProjectDetail.jsx";
import ProfileSetup from "./pages/ProfileSetup.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/profile/setup"
        element={
          <ProtectedRoute>
            <ProfileSetup />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:projectId"
        element={
          <ProtectedRoute>
            <ProjectDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/upload"
        element={
          <ProtectedRoute>
            <UploadScript />
          </ProtectedRoute>
        }
      />
      <Route
        path="/breakdown/:scriptId"
        element={
          <ProtectedRoute>
            <BreakdownView />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
