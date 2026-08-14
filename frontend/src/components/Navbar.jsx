import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { APP_NAME } from "../utils/constants";
import Button from "./Button.jsx";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-30 flex min-h-16 items-center justify-between gap-3 border-b border-gray-200 bg-white/95 px-4 py-3 backdrop-blur sm:px-6">
      <Link
        to={isAuthenticated ? "/dashboard" : "/"}
        className="min-w-0 text-base font-semibold text-brand-700 sm:text-lg"
      >
        {APP_NAME}
      </Link>

      {isAuthenticated ? (
        <div className="flex min-w-0 items-center gap-2 sm:gap-4">
          <div className="min-w-0 text-right">
            <span className="block truncate text-sm font-medium text-gray-700">
              {user?.name}
            </span>
            {user?.production_role_label && (
              <span className="block truncate text-xs text-gray-400 sm:hidden">
                {user.production_role_label}
              </span>
            )}
          </div>
          {user?.production_role_label && (
            <span className="hidden rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 sm:inline-block">
              {user.production_role_label}
            </span>
          )}
          <Button variant="ghost" onClick={handleLogout} className="px-2 sm:px-4">
            Log out
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-gray-900">
            Log in
          </Link>
          <Link to="/register">
            <Button>Sign up</Button>
          </Link>
        </div>
      )}
    </header>
  );
}
