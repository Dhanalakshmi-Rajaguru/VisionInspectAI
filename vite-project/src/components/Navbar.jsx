
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <h2>VisionInspect AI</h2>
      </div>

      {user && (
        <div className="navbar-right">
          <div className="user-info">
            <strong>{user.name}</strong>
            <span>
              {user.role === "quality_engineer"
                ? "Quality Engineer"
                : "Factory Supervisor"}
            </span>
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}

export default Navbar;

