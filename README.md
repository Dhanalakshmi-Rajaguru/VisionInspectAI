# VisionInspect AI

AI-powered manufacturing quality inspection system for detecting defects in industrial products using computer vision and YOLO.

## Project Overview

VisionInspect AI is a web-based quality inspection application designed to assist manufacturing quality engineers in identifying defective products from images.

The system combines:

- React.js frontend
- FastAPI backend
- PostgreSQL database
- JWT authentication
- Role-based access control
- OpenCV-based image preprocessing
- Data augmentation
- YOLO-based defect detection
- MVTec AD dataset

The application allows users to upload an inspection image, process it through the backend, run the trained YOLO model, and obtain a defect prediction.

## Features

- User registration and login
- JWT-based authentication
- Role-based access for:
  - Quality Engineer
  - Factory Supervisor
- Image upload for inspection
- Image preprocessing
- YOLO-based defect detection
- Inspection result storage
- Inspection history
- Dashboard for inspection information
- PostgreSQL database integration

## Technology Stack

### Frontend

- React.js
- Vite
- JavaScript
- Tailwind CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT
- Passlib

### Database

- PostgreSQL

### Machine Learning

- YOLO
- PyTorch
- OpenCV
- NumPy
- MVTec AD dataset

## Project Structure

```text
VisionInspectAI/
│
├── backend/
│   ├── ml/
│   ├── auth.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── requirements.txt
│
├── vite-project/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── package.json
├── package-lock.json
└── README.md