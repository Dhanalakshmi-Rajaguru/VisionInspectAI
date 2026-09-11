import { useRef, useState } from "react";

function Inspection({ user }) {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const [imageDimensions, setImageDimensions] = useState({
    width: 1,
    height: 1,
  });

  const API_URL = "http://127.0.0.1:8000";

  // =====================================================
  // ALLOWED IMAGE TYPES
  // =====================================================

  const allowedTypes = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/bmp",
    "image/tiff",
    "image/webp",
  ];

  // =====================================================
  // FORMAT FILE SIZE
  // =====================================================

  const formatFileSize = (bytes) => {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  // =====================================================
  // SELECT IMAGE
  // =====================================================

  const handleImageChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError("");
    setResult(null);

    // -------------------------------------------------
    // Check image type
    // -------------------------------------------------

    if (!allowedTypes.includes(file.type)) {
      setError(
        "Unsupported image format. Please select JPG, JPEG, PNG, BMP, TIFF or WebP."
      );

      event.target.value = "";
      return;
    }

    // -------------------------------------------------
    // Reject MVTec ground-truth masks
    // -------------------------------------------------

    const lowerFileName = file.name.toLowerCase();

    if (lowerFileName.includes("_mask")) {
      setError(
        "Ground-truth mask images are not allowed. Please upload the original product image."
      );

      event.target.value = "";
      return;
    }

    // -------------------------------------------------
    // Check file size
    // -------------------------------------------------

    if (file.size > 10 * 1024 * 1024) {
      setError("Image size must be less than 10 MB.");

      event.target.value = "";
      return;
    }

    // -------------------------------------------------
    // Remove previous preview URL
    // -------------------------------------------------

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const imageUrl = URL.createObjectURL(file);

    setSelectedFile(file);
    setPreviewUrl(imageUrl);

    setImageDimensions({
      width: 1,
      height: 1,
    });
  };

  // =====================================================
  // RESULT IMAGE LOAD
  // =====================================================

  const handleResultImageLoad = (event) => {
    setImageDimensions({
      width: event.target.naturalWidth,
      height: event.target.naturalHeight,
    });
  };

  // =====================================================
  // REMOVE IMAGE
  // =====================================================

  const handleRemoveImage = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(null);
    setPreviewUrl("");
    setResult(null);
    setError("");

    setImageDimensions({
      width: 1,
      height: 1,
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // =====================================================
  // RUN INSPECTION
  // =====================================================

  const handleInspection = async () => {
    setError("");
    setResult(null);

    // -------------------------------------------------
    // Image validation
    // -------------------------------------------------

    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    // -------------------------------------------------
    // JWT validation
    // -------------------------------------------------

    const token = localStorage.getItem("access_token");

    if (!token) {
      setError("Your session has expired. Please login again.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();

      // FastAPI expects "file"
      formData.append("file", selectedFile);

      // -------------------------------------------------
      // Send request to FastAPI
      // -------------------------------------------------

      const response = await fetch(
        `${API_URL}/inspection/predict`,
        {
          method: "POST",

          headers: {
            Authorization: `Bearer ${token}`,
          },

          body: formData,
        }
      );

      let data = {};

      try {
        data = await response.json();
      } catch {
        data = {};
      }

      // =================================================
      // ERROR HANDLING
      // =================================================

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error(
            "Unauthorized. Please login again."
          );
        }

        if (response.status === 403) {
          throw new Error(
            "You do not have permission to perform an inspection."
          );
        }

        if (response.status === 404) {
          throw new Error(
            "Inspection endpoint not found."
          );
        }

        if (response.status === 422) {
          throw new Error(
            data.detail
              ? JSON.stringify(data.detail)
              : "Invalid inspection request."
          );
        }

        throw new Error(
          data.detail || "Inspection failed."
        );
      }

      // =================================================
      // SUCCESS
      // =================================================

      console.log(
        "YOLO inspection result:",
        data
      );

      setResult(data);

    } catch (err) {
      console.error(
        "Inspection error:",
        err
      );

      if (err instanceof TypeError) {
        setError(
          "Cannot connect to VisionInspect AI server. Make sure FastAPI is running on http://127.0.0.1:8000."
        );
      } else {
        setError(
          err.message ||
            "Unable to complete inspection."
        );
      }

    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // RESULT STATUS
  // =====================================================

  const isNormal =
    result?.prediction?.toLowerCase() === "pass";

  // =====================================================
  // RENDER YOLO DETECTION BOXES
  // =====================================================

  const renderDetectionBoxes = () => {
    if (!result?.detections?.length) {
      return null;
    }

    if (
      !imageDimensions.width ||
      !imageDimensions.height
    ) {
      return null;
    }

    return result.detections.map(
      (detection, index) => {
        const bbox = detection?.bbox;

        if (!bbox) {
          return null;
        }

        const {
          x1,
          y1,
          x2,
          y2,
        } = bbox;

        // Convert original image coordinates
        // to percentage positions.

        const left =
          (x1 / imageDimensions.width) * 100;

        const top =
          (y1 / imageDimensions.height) * 100;

        const width =
          ((x2 - x1) /
            imageDimensions.width) *
          100;

        const height =
          ((y2 - y1) /
            imageDimensions.height) *
          100;

        const confidence =
          Number(
            detection.confidence || 0
          ) * 100;

        return (
          <div
            key={index}
            className="yolo-detection-box"
            style={{
              position: "absolute",
              left: `${left}%`,
              top: `${top}%`,
              width: `${width}%`,
              height: `${height}%`,
              border: "3px solid red",
              boxSizing: "border-box",
              pointerEvents: "none",
              zIndex: 5,
            }}
          >
            {/* DEFECT LABEL */}

            <div
              className="yolo-detection-label"
              style={{
                position: "absolute",
                left: "-3px",
                top: "-32px",
                background: "red",
                color: "white",
                padding: "5px 9px",
                fontSize: "14px",
                fontWeight: "700",
                lineHeight: "1",
                whiteSpace: "nowrap",
                borderRadius: "3px",
              }}
            >
              defect: {confidence.toFixed(1)}%
            </div>
          </div>
        );
      }
    );
  };

  // =====================================================
  // HIGHEST CONFIDENCE
  // =====================================================

  const highestConfidence =
    result?.detections?.length > 0
      ? Math.max(
          ...result.detections.map(
            (detection) =>
              Number(
                detection.confidence || 0
              )
          )
        ) * 100
      : null;

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="inspection-page">

      {/* =================================================
          PAGE HEADER
         ================================================= */}

      <div className="inspection-page-header">

        <div>

          <h1>
            New Inspection
          </h1>

          <p>
            Upload a product image and run
            AI-powered quality inspection.
          </p>

        </div>

      </div>

      {/* =================================================
          MAIN CONTENT
         ================================================= */}

      <div className="inspection-content">

        {/* =================================================
            LEFT CARD
           ================================================= */}

        <div className="upload-card">

          {/* CARD HEADER */}

          <div className="inspection-card-header">

            <div>

              <h2>
                Product Image
              </h2>

              <p>
                Upload an image for quality
                inspection.
              </p>

            </div>

          </div>

          {/* =================================================
              FILE INPUT
             ================================================= */}

          <input
            ref={fileInputRef}
            id="product-image-upload"
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/bmp,image/tiff,image/webp"
            onChange={handleImageChange}
            disabled={loading}
            style={{
              position: "absolute",
              width: "1px",
              height: "1px",
              opacity: 0,
              overflow: "hidden",
              pointerEvents: "none",
            }}
          />

          {/* =================================================
              UPLOAD AREA
             ================================================= */}

          {!selectedFile ? (

            <label
              htmlFor="product-image-upload"
              className="upload-area"
              style={{
                display: "block",
                cursor: loading
                  ? "not-allowed"
                  : "pointer",
              }}
            >

              <div className="upload-icon">
                📁
              </div>

              <h3>
                Upload Product Image
              </h3>

              <p>
                Click here to select an image
              </p>

              <span>
                Supported formats:
                JPG, JPEG, PNG,
                BMP, TIFF, WebP
              </span>

            </label>

          ) : (

            <div className="image-container">

              <img
                src={previewUrl}
                alt="Selected product"
                className="image-preview"
              />

              <button
                type="button"
                className="remove-image-btn"
                onClick={handleRemoveImage}
                disabled={loading}
              >
                Remove
              </button>

            </div>

          )}

          {/* =================================================
              SELECTED FILE
             ================================================= */}

          {selectedFile && (

            <div className="selected-file">

              <span className="file-icon">
                📄
              </span>

              <div className="selected-file-info">

                <p>
                  {selectedFile.name}
                </p>

                <small>
                  {formatFileSize(
                    selectedFile.size
                  )}
                </small>

              </div>

            </div>

          )}

          {/* =================================================
              ERROR
             ================================================= */}

          {error && (

            <div className="inspection-error">
              ⚠ {error}
            </div>

          )}

          {/* =================================================
              SUBMIT BUTTON
             ================================================= */}

          <button
            type="button"
            className="inspect-btn"
            onClick={handleInspection}
            disabled={
              loading ||
              !selectedFile
            }
          >

            {loading
              ? "Analyzing Image..."
              : "Submit for Inspection"}

          </button>

        </div>

        {/* =================================================
            RIGHT RESULT CARD
           ================================================= */}

        <div className="result-card-inspection">

          {/* CARD HEADER */}

          <div className="inspection-card-header">

            <div>

              <h2>
                Inspection Result
              </h2>

              <p>
                AI analysis results will
                appear here.
              </p>

            </div>

          </div>

          {/* =================================================
              LOADING
             ================================================= */}

          {loading && (

            <div className="empty-result">

              <div className="loading-icon">
                ⚙
              </div>

              <h3>
                Analyzing Image...
              </h3>

              <p>
                VisionInspect AI is analyzing
                the uploaded image.
              </p>

              <div className="loading-bar">

                <div className="loading-progress"></div>

              </div>

            </div>

          )}

          {/* =================================================
              NO RESULT
             ================================================= */}

          {!loading && !result && (

            <div className="empty-result">

              <div className="result-icon">
                ◎
              </div>

              <h3>
                No Inspection Result
              </h3>

              <p>
                Upload a product image to
                begin the inspection.
              </p>

            </div>

          )}

          {/* =================================================
              RESULT
             ================================================= */}

          {!loading && result && (

            <div className="inspection-result">

              {/* =================================================
                  YOLO DETECTION IMAGE
                 ================================================= */}

              <div
                className="yolo-result-image"
                style={{
                  width: "100%",
                  marginBottom: "25px",
                }}
              >

                <div
                  className="yolo-image-wrapper"
                  style={{
                    position: "relative",
                    width: "100%",
                    overflow: "visible",
                    borderRadius: "8px",
                  }}
                >

                  <img
                    src={previewUrl}
                    alt="YOLO inspection result"
                    onLoad={handleResultImageLoad}
                    style={{
                      width: "100%",
                      height: "auto",
                      display: "block",
                      borderRadius: "8px",
                    }}
                  />

                  {/* YOLO BOXES */}

                  {renderDetectionBoxes()}

                </div>

              </div>

              {/* =================================================
                  STATUS
                 ================================================= */}

              <div
                className={
                  isNormal
                    ? "result-status pass-result"
                    : "result-status defect-result"
                }
              >

                <div className="result-status-icon">

                  {isNormal
                    ? "✓"
                    : "⚠"}

                </div>

                <h3>
                  {result.prediction?.toUpperCase()}
                </h3>

              </div>

              {/* =================================================
                  PREDICTION
                 ================================================= */}

              <div className="result-detail">

                <span>
                  Prediction
                </span>

                <strong>
                  {result.prediction || "-"}
                </strong>

              </div>

              {/* =================================================
                  DEFECT COUNT
                 ================================================= */}

              <div className="result-detail">

                <span>
                  Defect Count
                </span>

                <strong>
                  {result.defect_count ?? 0}
                </strong>

              </div>

              {/* =================================================
                  HIGHEST CONFIDENCE
                 ================================================= */}

              <div className="result-detail">

                <span>
                  Highest Confidence
                </span>

                <strong>

                  {highestConfidence !== null
                    ? `${highestConfidence.toFixed(
                        2
                      )}%`
                    : "-"}

                </strong>

              </div>

              {/* =================================================
                  DETECTED DEFECTS
                 ================================================= */}

              {result.detections?.length > 0 && (

                <div
                  className="result-detections"
                  style={{
                    marginTop: "20px",
                  }}
                >

                  <h3>
                    Detected Defects
                  </h3>

                  {result.detections.map(
                    (detection, index) => {

                      const confidence =
                        Number(
                          detection.confidence ||
                            0
                        ) * 100;

                      const bbox =
                        detection.bbox;

                      return (

                        <div
                          className="detection-item"
                          key={index}
                          style={{
                            padding: "12px",
                            marginBottom: "10px",
                            border:
                              "1px solid #ddd",
                            borderRadius: "6px",
                          }}
                        >

                          {/* DEFECT */}

                          <div className="result-detail">

                            <span>
                              Defect {index + 1}
                            </span>

                            <strong>
                              {confidence.toFixed(
                                2
                              )}%
                            </strong>

                          </div>

                          {/* CLASS */}

                          <div className="result-detail">

                            <span>
                              Class
                            </span>

                            <strong>
                              {detection.class_name ||
                                "defect"}
                            </strong>

                          </div>

                          {/* BOUNDING BOX */}

                          {bbox && (

                            <div className="result-detail">

                              <span>
                                Bounding Box
                              </span>

                              <strong>
                                (
                                {Number(
                                  bbox.x1
                                ).toFixed(1)}
                                ,{" "}
                                {Number(
                                  bbox.y1
                                ).toFixed(1)}
                                ) → (
                                {Number(
                                  bbox.x2
                                ).toFixed(1)}
                                ,{" "}
                                {Number(
                                  bbox.y2
                                ).toFixed(1)}
                                )
                              </strong>

                            </div>

                          )}

                        </div>

                      );

                    }
                  )}

                </div>

              )}

              {/* =================================================
                  INSPECTED BY
                 ================================================= */}

              <div className="result-detail">

                <span>
                  Inspected By
                </span>

                <strong>
                  {result.inspected_by || "-"}
                </strong>

              </div>

              {/* =================================================
                  ROLE
                 ================================================= */}

              <div className="result-detail">

                <span>
                  Role
                </span>

                <strong>

                  {result.inspected_by_role
                    ?.replace("_", " ")
                    ?.toUpperCase() || "-"}

                </strong>

              </div>

              {/* =================================================
                  MESSAGE
                 ================================================= */}

              <div className="result-message">

                {isNormal ? (

                  <p>
                    ✓ The inspected product
                    appears to meet the
                    required quality standards.
                  </p>

                ) : (

                  <p>
                    ⚠ A potential
                    manufacturing defect
                    was detected. Further
                    inspection may be required.
                  </p>

                )}

              </div>

              {/* =================================================
                  NEW INSPECTION
                 ================================================= */}

              <button
                type="button"
                className="new-inspection-button"
                onClick={handleRemoveImage}
              >
                Start New Inspection
              </button>

            </div>

          )}

        </div>

      </div>

    </div>
  );
}

export default Inspection;