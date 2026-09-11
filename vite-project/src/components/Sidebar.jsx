import { useAuth } from "../context/AuthContext";

function Sidebar({ page, setPage }) {
  const { user } = useAuth();

  const role = user?.role;

  const isQualityEngineer = role === "quality_engineer";
  const isSupervisor = role === "factory_supervisor";

  const navigate = (target) => {
    console.log("SIDEBAR CLICK:", target);
    setPage(target);
  };

  return (
    <aside className="w-64 min-h-screen bg-slate-900 text-white flex flex-col">

      {/* LOGO */}
      <div className="px-6 py-6 border-b border-slate-700">
        <h1 className="text-xl font-bold">
          VisionInspect AI
        </h1>

        <p className="text-xs text-slate-400 mt-1">
          Quality Inspection System
        </p>
      </div>

      {/* USER */}
      <div className="px-6 py-4 border-b border-slate-700">
        <p className="text-xs text-slate-400">
          Logged in as
        </p>

        <p className="text-sm font-semibold mt-1">
          {user?.name}
        </p>

        <p className="text-xs text-blue-400 mt-1">
          {role?.replace("_", " ").toUpperCase()}
        </p>
      </div>

      {/* NAVIGATION */}
      <nav className="flex-1 px-4 py-6">

        <div className="space-y-2">

          {/* DASHBOARD */}
          <button
            type="button"
            onClick={() => navigate("dashboard")}
            className={`w-full text-left px-4 py-3 rounded-lg transition cursor-pointer ${
              page === "dashboard"
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Dashboard
          </button>

          {/* QUALITY ENGINEER */}
          {isQualityEngineer && (
            <button
              type="button"
              onClick={() => navigate("inspection")}
              className={`w-full text-left px-4 py-3 rounded-lg transition cursor-pointer ${
                page === "inspection"
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              New Inspection
            </button>
          )}

          {/* INSPECTIONS */}
          <button
            type="button"
            onClick={() => navigate("inspections")}
            className={`w-full text-left px-4 py-3 rounded-lg transition cursor-pointer ${
              page === "inspections"
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Inspections
          </button>

          {/* REPORTS */}
          <button
            type="button"
            onClick={() => navigate("reports")}
            className={`w-full text-left px-4 py-3 rounded-lg transition cursor-pointer ${
              page === "reports"
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Reports
          </button>

          {/* ANALYTICS */}
          <button
            type="button"
            onClick={() => navigate("analytics")}
            className={`w-full text-left px-4 py-3 rounded-lg transition cursor-pointer ${
              page === "analytics"
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Analytics
          </button>

          {/* SUPERVISOR */}
          {isSupervisor && (
            <button
              type="button"
              onClick={() => navigate("users")}
              className={`w-full text-left px-4 py-3 rounded-lg transition cursor-pointer ${
                page === "users"
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              Users
            </button>
          )}

          {/* SETTINGS */}
          <button
            type="button"
            onClick={() => navigate("settings")}
            className={`w-full text-left px-4 py-3 rounded-lg transition cursor-pointer ${
              page === "settings"
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Settings
          </button>

        </div>

      </nav>

      {/* LOGOUT */}
      {/* <div className="px-4 py-5 border-t border-slate-700"> */}
{/* 
        <button
          type="button"
          onClick={() => {
            console.log("LOGOUT CLICK");
          }}
          className="w-full px-4 py-3 rounded-lg text-left text-slate-300 hover:bg-red-600 hover:text-white transition cursor-pointer"
        >
          Logout
        </button>

      </div> */}

    </aside>
  );
}

export default Sidebar;