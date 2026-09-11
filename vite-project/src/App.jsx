import { useState } from "react";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Inspection from "./pages/Inspection";
import Login from "./pages/Login";

import { useAuth } from "./context/AuthContext";

import "./App.css";

function App() {
  const { user, loading, logout } = useAuth();

  const [page, setPage] = useState("dashboard");

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>

        <p>Loading VisionInspect AI...</p>
      </div>
    );
  }

  // =====================================================
  // NOT LOGGED IN
  // =====================================================

  if (!user) {
    return <Login />;
  }

  // =====================================================
  // USER ROLE
  // =====================================================

  const role = user.role;

  const isQualityEngineer =
    role === "quality_engineer";

  const isSupervisor =
    role === "factory_supervisor";

  // =====================================================
  // NAVIGATION
  // =====================================================

  const handleNavigation = (selectedPage) => {
    console.log("Navigation clicked:", selectedPage);

    // ---------------------------------------------------
    // QUALITY ENGINEER
    // ---------------------------------------------------

    if (isQualityEngineer) {
      const allowedPages = [
        "dashboard",
        "inspection",
        "inspections",
        "reports",
        "analytics",
        "settings",
      ];

      if (allowedPages.includes(selectedPage)) {
        setPage(selectedPage);
      }

      return;
    }

    // ---------------------------------------------------
    // FACTORY SUPERVISOR
    // ---------------------------------------------------

    if (isSupervisor) {
      const allowedPages = [
        "dashboard",
        "production",
        "alerts",
        "summary",
        "reports",
        "users",
        "settings",
      ];

      if (allowedPages.includes(selectedPage)) {
        setPage(selectedPage);
      }
    }
  };

  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = () => {
    logout();
    setPage("dashboard");
  };

  // =====================================================
  // PLACEHOLDER PAGE
  // =====================================================

  const PlaceholderPage = ({ title, description }) => {
    return (
      <div className="placeholder-page">
        <h1>{title}</h1>

        <p>{description}</p>
      </div>
    );
  };

  // =====================================================
  // PAGE CONTENT
  // =====================================================

  const renderPage = () => {

    // ===================================================
    // DASHBOARD
    // ===================================================

    if (page === "dashboard") {
      return (
        <Dashboard
          user={user}
          setPage={handleNavigation}
        />
      );
    }

    // ===================================================
    // NEW INSPECTION
    // ===================================================

    if (
      page === "inspection" &&
      isQualityEngineer
    ) {
      return (
        <Inspection
          user={user}
        />
      );
    }

    // ===================================================
    // INSPECTIONS
    // ===================================================

    if (page === "inspections") {
      return (
        <PlaceholderPage
          title="Inspections"
          description="View previous inspection records."
        />
      );
    }

    // ===================================================
    // REPORTS
    // ===================================================

    if (page === "reports") {
      return (
        <PlaceholderPage
          title="Reports"
          description="View quality inspection reports."
        />
      );
    }

    // ===================================================
    // ANALYTICS
    // ===================================================

    if (
      page === "analytics" &&
      isQualityEngineer
    ) {
      return (
        <PlaceholderPage
          title="Analytics"
          description="View inspection analytics and performance."
        />
      );
    }

    // ===================================================
    // SETTINGS
    // ===================================================

    if (page === "settings") {
      return (
        <PlaceholderPage
          title="Settings"
          description="Manage system settings."
        />
      );
    }

    // ===================================================
    // SUPERVISOR - USERS
    // ===================================================

    if (
      page === "users" &&
      isSupervisor
    ) {
      return (
        <PlaceholderPage
          title="Users"
          description="Manage system users."
        />
      );
    }

    // ===================================================
    // SUPERVISOR - PRODUCTION
    // ===================================================

    if (
      page === "production" &&
      isSupervisor
    ) {
      return (
        <PlaceholderPage
          title="Production Status"
          description="Monitor production inspection status."
        />
      );
    }

    // ===================================================
    // SUPERVISOR - ALERTS
    // ===================================================

    if (
      page === "alerts" &&
      isSupervisor
    ) {
      return (
        <PlaceholderPage
          title="Critical Alerts"
          description="Monitor critical quality alerts."
        />
      );
    }

    // ===================================================
    // SUPERVISOR - SUMMARY
    // ===================================================

    if (
      page === "summary" &&
      isSupervisor
    ) {
      return (
        <PlaceholderPage
          title="Inspection Summary"
          description="View inspection summary."
        />
      );
    }

    // ===================================================
    // FALLBACK
    // ===================================================

    return (
      <Dashboard
        user={user}
        setPage={handleNavigation}
      />
    );
  };

  // =====================================================
  // APPLICATION
  // =====================================================

  return (
    <div className="app">

      {/* =================================================
          NAVBAR
         ================================================= */}

      <Navbar />

      {/* =================================================
          APPLICATION BODY
         ================================================= */}

      <div className="app-body">

        {/* =================================================
            SIDEBAR
           ================================================= */}

        <Sidebar
          page={page}
          setPage={handleNavigation}
        />

        {/* =================================================
            MAIN CONTENT
           ================================================= */}

        <main className="main-content">
          {renderPage()}
        </main>

      </div>

    </div>
  );
}

export default App;