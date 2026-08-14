import { useAuth } from "./hooks/useAuth";
import { ProjectProvider } from "./context/ProjectContext.jsx";
import Navbar from "./components/Navbar.jsx";
import Sidebar from "./components/Sidebar.jsx";
import AppRoutes from "./routes.jsx";

export default function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      {isAuthenticated ? (
        <ProjectProvider>
          <div className="flex flex-1">
            <Sidebar />
            <main className="flex-1 pb-20 md:pb-0">
              <AppRoutes />
            </main>
          </div>
        </ProjectProvider>
      ) : (
        <main className="flex-1">
          <AppRoutes />
        </main>
      )}
    </div>
  );
}
