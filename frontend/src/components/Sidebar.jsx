import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/upload", label: "Upload Script" },
];

export default function Sidebar() {
  return (
    <>
      <aside className="hidden w-56 shrink-0 border-r border-gray-200 bg-white py-6 md:block">
        <nav className="flex flex-col gap-1 px-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive ? "bg-brand-50 text-brand-700" : "text-gray-600 hover:bg-gray-50"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-2 border-t border-gray-200 bg-white px-3 py-2 shadow-[0_-8px_20px_rgba(15,23,42,0.06)] md:hidden">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `mx-1 rounded-lg px-3 py-2 text-center text-xs font-medium transition-colors ${
                isActive ? "bg-brand-50 text-brand-700" : "text-gray-500"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
