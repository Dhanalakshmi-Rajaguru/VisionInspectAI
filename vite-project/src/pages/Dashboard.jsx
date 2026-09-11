import InspectionTable from "../components/InspectionTable";

function Dashboard({ user }) {
  const isQualityEngineer =
    user?.role === "quality_engineer";

  const isSupervisor =
    user?.role === "factory_supervisor";

  const roleName = isQualityEngineer
    ? "Quality Engineer"
    : isSupervisor
      ? "Factory Supervisor"
      : "User";

  return (
    <div className="dashboard">

      {/* =====================================================
          DASHBOARD HEADER
         ===================================================== */}

      <div className="dashboard-header">

        <div>
          <h1>Dashboard</h1>

          <p>
            Monitor your industrial quality inspections.
          </p>
        </div>

        {/* Quality Engineer can directly start inspection */}
        {isQualityEngineer && (
          <button className="new-inspection-btn">
            + New Inspection
          </button>
        )}

      </div>


      {/* =====================================================
          ROLE INFORMATION
         ===================================================== */}

      <div className="dashboard-role-info">
        <span className="role-label">
          Logged in as
        </span>

        <strong>
          {roleName}
        </strong>
      </div>


      {/* =====================================================
          STATISTICS CARDS
         ===================================================== */}

      <div className="stats-grid">

        {/* Total Inspections */}

        <div className="stat-card">

          <div className="stat-icon total-icon">
            <span>▣</span>
          </div>

          <div className="stat-content">

            <p>Total Inspections</p>

            <h2>1,250</h2>

            <div className="stat-change">
              <span className="positive">
                ↑ 12.5%
              </span>

              <small>
                vs last month
              </small>
            </div>

          </div>

        </div>


        {/* Passed Inspections */}

        <div className="stat-card">

          <div className="stat-icon passed-icon">
            <span>✓</span>
          </div>

          <div className="stat-content">

            <p>Passed Inspections</p>

            <h2>1,180</h2>

            <div className="stat-change">
              <span className="positive">
                ↑ 94.4%
              </span>

              <small>
                pass rate
              </small>
            </div>

          </div>

        </div>


        {/* Defective Items */}

        <div className="stat-card">

          <div className="stat-icon defect-icon">
            <span>!</span>
          </div>

          <div className="stat-content">

            <p>Defective Items</p>

            <h2>70</h2>

            <div className="stat-change">
              <span className="negative">
                ↓ 5.6%
              </span>

              <small>
                defect rate
              </small>
            </div>

          </div>

        </div>


        {/* Model Accuracy */}

        <div className="stat-card">

          <div className="stat-icon accuracy-icon">
            <span>◎</span>
          </div>

          <div className="stat-content">

            <p>Model Accuracy</p>

            <h2>96.8%</h2>

            <div className="stat-change">
              <span className="positive">
                ↑ 2.1%
              </span>

              <small>
                improvement
              </small>
            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          DASHBOARD MAIN GRID
         ===================================================== */}

      <div className="dashboard-grid">


        {/* =================================================
            INSPECTION OVERVIEW
           ================================================= */}

        <div className="dashboard-card overview-card">

          <div className="card-header">

            <div>
              <h2>Inspection Overview</h2>

              <p>
                Inspection activity over the last 7 days
              </p>
            </div>


            <select className="period-select">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
              <option>Last 3 Months</option>
            </select>

          </div>


          {/* =================================================
              BAR CHART
             ================================================= */}

          <div className="inspection-chart">


            {/* Y AXIS */}

            <div className="chart-y-axis">

              <span>250</span>
              <span>200</span>
              <span>150</span>
              <span>100</span>
              <span>50</span>
              <span>0</span>

            </div>


            {/* CHART AREA */}

            <div className="chart-area">


              {/* Horizontal grid lines */}

              <div className="grid-lines">

                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>

              </div>


              {/* =================================================
                  BAR CONTAINER
                 ================================================= */}

              <div className="bars">


                {/* Monday */}

                <div className="bar-column">

                  <div
                    className="bar"
                    style={{ height: "44%" }}
                    title="Monday: 110 inspections"
                  ></div>

                  <span>Mon</span>

                </div>


                {/* Tuesday */}

                <div className="bar-column">

                  <div
                    className="bar"
                    style={{ height: "64%" }}
                    title="Tuesday: 160 inspections"
                  ></div>

                  <span>Tue</span>

                </div>


                {/* Wednesday */}

                <div className="bar-column">

                  <div
                    className="bar"
                    style={{ height: "49%" }}
                    title="Wednesday: 122 inspections"
                  ></div>

                  <span>Wed</span>

                </div>


                {/* Thursday */}

                <div className="bar-column">

                  <div
                    className="bar"
                    style={{ height: "82%" }}
                    title="Thursday: 205 inspections"
                  ></div>

                  <span>Thu</span>

                </div>


                {/* Friday */}

                <div className="bar-column">

                  <div
                    className="bar"
                    style={{ height: "62%" }}
                    title="Friday: 155 inspections"
                  ></div>

                  <span>Fri</span>

                </div>


                {/* Saturday */}

                <div className="bar-column">

                  <div
                    className="bar"
                    style={{ height: "87%" }}
                    title="Saturday: 218 inspections"
                  ></div>

                  <span>Sat</span>

                </div>


                {/* Sunday */}

                <div className="bar-column">

                  <div
                    className="bar"
                    style={{ height: "74%" }}
                    title="Sunday: 185 inspections"
                  ></div>

                  <span>Sun</span>

                </div>

              </div>

            </div>

          </div>

        </div>


        {/* =====================================================
            INSPECTION RESULTS
           ===================================================== */}

        <div className="dashboard-card result-card">

          <div className="card-header">

            <div>
              <h2>Inspection Results</h2>

              <p>
                Overall inspection performance
              </p>
            </div>

          </div>


          {/* =================================================
              DONUT CHART
             ================================================= */}

          <div className="result-circle">

            <div className="result-circle-content">

              <strong>94.4%</strong>

              <span>
                Pass Rate
              </span>

            </div>

          </div>


          {/* =================================================
              RESULT STATISTICS
             ================================================= */}

          <div className="result-stats">


            {/* Passed */}

            <div className="result-item">

              <span className="result-dot pass-dot"></span>

              <div>

                <p>Passed</p>

                <strong>
                  1,180
                </strong>

              </div>

            </div>


            {/* Defective */}

            <div className="result-item">

              <span className="result-dot defect-dot"></span>

              <div>

                <p>Defective</p>

                <strong>
                  70
                </strong>

              </div>

            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          RECENT INSPECTIONS
         ===================================================== */}

      <InspectionTable />

    </div>
  );
}

export default Dashboard;