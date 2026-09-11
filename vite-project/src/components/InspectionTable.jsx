
function InspectionTable() {

  const inspections = [
    {
      id: "INS001",
      product: "Bottle",
      date: "23 Aug 2026",
      result: "PASS",
      confidence: "98.2%"
    },
    {
      id: "INS002",
      product: "Cable",
      date: "23 Aug 2026",
      result: "DEFECT",
      confidence: "91.7%"
    },
    {
      id: "INS003",
      product: "Screw",
      date: "22 Aug 2026",
      result: "PASS",
      confidence: "96.4%"
    },
    {
      id: "INS004",
      product: "Metal Part",
      date: "22 Aug 2026",
      result: "DEFECT",
      confidence: "89.3%"
    },
    {
      id: "INS005",
      product: "Bottle",
      date: "21 Aug 2026",
      result: "PASS",
      confidence: "97.1%"
    }
  ];


  return (
    <div className="inspection-table-container">

      {/* Table Header */}
      <div className="inspection-table-header">

        <div>
          <h2>Recent Inspections</h2>
          <p>Latest quality inspection results</p>
        </div>

        <button className="view-all-btn">
          View All
        </button>

      </div>


      {/* Table */}
      <div className="table-wrapper">

        <table className="inspection-table">

          <thead>
            <tr>
              <th>Inspection ID</th>
              <th>Product</th>
              <th>Date</th>
              <th>Result</th>
              <th>Confidence</th>
              <th>Action</th>
            </tr>
          </thead>


          <tbody>

            {inspections.map((inspection) => (

              <tr key={inspection.id}>

                <td>
                  <strong>{inspection.id}</strong>
                </td>

                <td>{inspection.product}</td>

                <td>{inspection.date}</td>

                <td>

                  <span
                    className={
                      inspection.result === "PASS"
                        ? "status pass"
                        : "status defect"
                    }
                  >
                    {inspection.result}
                  </span>

                </td>

                <td>{inspection.confidence}</td>

                <td>
                  <button className="view-btn">
                    View
                  </button>
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default InspectionTable;