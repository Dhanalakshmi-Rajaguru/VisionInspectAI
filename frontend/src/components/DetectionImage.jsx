import { useState } from "react";

function DetectionImage({ imageUrl, detections = [] }) {
  const [imageSize, setImageSize] = useState({
    width: 1,
    height: 1,
  });

  const handleImageLoad = (event) => {
    setImageSize({
      width: event.target.naturalWidth,
      height: event.target.naturalHeight,
    });
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
      }}
    >
      <img
        src={imageUrl}
        alt="Inspection result"
        onLoad={handleImageLoad}
        style={{
          width: "100%",
          height: "auto",
          display: "block",
        }}
      />

      {detections.map((detection, index) => {
        const { x1, y1, x2, y2 } = detection.bbox;

        const left =
          (x1 / imageSize.width) * 100;

        const top =
          (y1 / imageSize.height) * 100;

        const width =
          ((x2 - x1) / imageSize.width) * 100;

        const height =
          ((y2 - y1) / imageSize.height) * 100;

        return (
          <div
            key={index}
            style={{
              position: "absolute",
              left: `${left}%`,
              top: `${top}%`,
              width: `${width}%`,
              height: `${height}%`,
              border: "3px solid red",
              boxSizing: "border-box",
              pointerEvents: "none",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: "-29px",
                left: "-3px",
                background: "red",
                color: "white",
                padding: "4px 8px",
                fontSize: "14px",
                fontWeight: "bold",
                whiteSpace: "nowrap",
              }}
            >
              defect:{" "}
              {(detection.confidence * 100).toFixed(1)}%
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default DetectionImage;