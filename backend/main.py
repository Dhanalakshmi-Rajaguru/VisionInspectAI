from pathlib import Path
import shutil
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlalchemy.orm import Session

from database import SessionLocal, engine

from models import Base, User, Inspection

from schemas import UserCreate, UserLogin

from ml.yolo_service import YOLOService


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="VisionInspect AI",
    description="AI-powered manufacturing quality inspection system",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# JWT CONFIGURATION
# =========================================================

SECRET_KEY = "visioninspect-secret-key-change-this"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================================================
# HTTP BEARER SECURITY
# =========================================================

security = HTTPBearer()


# =========================================================
# PASSWORD HASHING
# =========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str):

    return pwd_context.hash(
        password
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
):

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# =========================================================
# CREATE JWT TOKEN
# =========================================================

def create_access_token(
    user_id: int,
    role: str,
):

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise credentials_exception

        user_id = int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError,
    ):

        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:

        raise credentials_exception

    return user


# =========================================================
# ROLE CHECK
# =========================================================

def require_role(
    allowed_roles: list[str],
):

    def role_checker(
        current_user: User = Depends(
            get_current_user
        ),
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail=(
                    "You do not have permission "
                    "to access this resource"
                ),
            )

        return current_user

    return role_checker


# =========================================================
# QUALITY ENGINEER
# =========================================================

def require_quality_engineer(
    current_user: User = Depends(
        require_role(
            ["quality_engineer"]
        )
    ),
):

    return current_user


# =========================================================
# FACTORY SUPERVISOR
# =========================================================

def require_supervisor(
    current_user: User = Depends(
        require_role(
            ["factory_supervisor"]
        )
    ),
):

    return current_user


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "VisionInspect AI API is running",
        "status": "online",
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/db-test")
def database_test(
    db: Session = Depends(get_db),
):

    try:

        from sqlalchemy import text

        db.execute(
            text("SELECT 1")
        )

        return {
            "status": "success",
            "message": "Database connection successful",
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database connection failed: {str(e)}"
            ),
        )


# =========================================================
# REGISTER
# =========================================================

@app.post("/auth/register")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):

    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    allowed_roles = {
        "quality_engineer",
        "factory_supervisor",
    }

    role = user_data.role

    if role not in allowed_roles:

        raise HTTPException(
            status_code=400,
            detail="Invalid role",
        )

    hashed_password = hash_password(
        user_data.password
    )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=role,
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "message": "User registered successfully",
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/auth/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        user_data.password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user.id,
        user.role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",

        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


# =========================================================
# CURRENT USER
# =========================================================

@app.get("/auth/me")
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }


# =========================================================
# UPLOAD DIRECTORY
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

UPLOAD_DIR = PROJECT_ROOT / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# ALLOWED IMAGE FORMATS
# =========================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


# =========================================================
# INSPECTION ACCESS
#
# QUALITY ENGINEER ONLY
# =========================================================

@app.get("/inspection")
def inspection_access(
    current_user: User = Depends(
        require_quality_engineer
    ),
):

    return {
        "message": "Inspection access granted",
        "user": current_user.name,
        "role": current_user.role,
    }


# =========================================================
# YOLO SERVICE
# =========================================================

yolo_service = YOLOService()


# =========================================================
# YOLO IMAGE INSPECTION
#
# QUALITY ENGINEER ONLY
#
# POST /inspection/predict
#
# Form fields:
# file
#
# IMPORTANT:
# Product category is NOT required.
#
# YOLO26n detects:
#
# 0 = defect
#
# across the trained MVTec categories.
# =========================================================

@app.post("/inspection/predict")
async def predict_inspection(

    file: UploadFile = File(...),

    current_user: User = Depends(
        require_quality_engineer
    ),

    db: Session = Depends(get_db),

):

    # -----------------------------------------------------
    # Validate filename
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided",
        )

    # -----------------------------------------------------
    # Reject MVTec ground-truth masks
    # -----------------------------------------------------

    if "_mask" in file.filename.lower():

        raise HTTPException(
            status_code=400,
            detail=(
                "Ground-truth mask images are not allowed. "
                "Please upload the original product image."
            ),
        )

    # -----------------------------------------------------
    # Validate extension
    # -----------------------------------------------------

    file_extension = (
        Path(file.filename)
        .suffix
        .lower()
    )

    if file_extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG, PNG, BMP, "
                "TIF, TIFF and WebP images are allowed"
            ),
        )

    # -----------------------------------------------------
    # Generate unique filename
    # -----------------------------------------------------

    unique_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    image_path = (
        UPLOAD_DIR / unique_filename
    )

    # -----------------------------------------------------
    # Save uploaded image
    # -----------------------------------------------------

    try:

        with image_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to save image: {str(e)}"
            ),
        )

    # -----------------------------------------------------
    # Run YOLO
    # -----------------------------------------------------

    try:

        result = yolo_service.predict(
            image_path
        )

        # -------------------------------------------------
        # Save inspection to PostgreSQL
        # -------------------------------------------------

        inspection = Inspection(

            user_id=current_user.id,

            image_path=str(
                image_path
            ),

            # ------------------------------------------------
            # Category has been removed from the application.
            #
            # This value is kept only because the existing
            # Inspection database model still has the
            # product_category column.
            # ------------------------------------------------

            product_category="unknown",

            prediction=result[
                "prediction"
            ],

            # ------------------------------------------------
            # Existing database compatibility.
            #
            # anomaly_score stores defect count.
            # ------------------------------------------------

            anomaly_score=str(
                result[
                    "defect_count"
                ]
            ),

            # ------------------------------------------------
            # YOLO confidence threshold.
            # ------------------------------------------------

            threshold="0.25",
        )

        db.add(inspection)

        db.commit()

        db.refresh(inspection)

        # -------------------------------------------------
        # Return YOLO result
        # -------------------------------------------------

        return {

            "message":
                "Inspection completed",

            "id":
                inspection.id,

            "filename":
                file.filename,

            "prediction":
                result[
                    "prediction"
                ],

            "defect_count":
                result[
                    "defect_count"
                ],

            "detections":
                result[
                    "detections"
                ],

            "inspected_by":
                current_user.name,

            "inspected_by_role":
                current_user.role,
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"YOLO inspection failed: {str(e)}"
            ),
        )


# =========================================================
# GET INSPECTION HISTORY
#
# QUALITY ENGINEER:
# Own inspections only
#
# FACTORY SUPERVISOR:
# All inspections
# =========================================================

@app.get("/inspections")
def get_inspections(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),

):

    # -----------------------------------------------------
    # QUALITY ENGINEER
    # -----------------------------------------------------

    if current_user.role == "quality_engineer":

        inspections = (

            db.query(Inspection)

            .filter(
                Inspection.user_id
                == current_user.id
            )

            .order_by(
                Inspection.created_at.desc()
            )

            .all()
        )

    # -----------------------------------------------------
    # FACTORY SUPERVISOR
    # -----------------------------------------------------

    elif current_user.role == "factory_supervisor":

        inspections = (

            db.query(Inspection)

            .order_by(
                Inspection.created_at.desc()
            )

            .all()
        )

    else:

        raise HTTPException(
            status_code=403,
            detail="Invalid user role",
        )

    result = []

    for inspection in inspections:

        result.append({

            "id":
                inspection.id,

            "user_id":
                inspection.user_id,

            "image_path":
                inspection.image_path,

            "product_category":
                inspection.product_category,

            "prediction":
                inspection.prediction,

            "anomaly_score":
                inspection.anomaly_score,

            "threshold":
                inspection.threshold,

            "created_at":
                inspection.created_at,
        })

    return result


# =========================================================
# GET SINGLE INSPECTION
# =========================================================

@app.get("/inspection/{inspection_id}")
def get_inspection(

    inspection_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),

):

    inspection = (

        db.query(Inspection)

        .filter(
            Inspection.id == inspection_id
        )

        .first()
    )

    if inspection is None:

        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    # -----------------------------------------------------
    # QUALITY ENGINEER
    #
    # Own inspections only
    # -----------------------------------------------------

    if (

        current_user.role
        == "quality_engineer"

        and

        inspection.user_id
        != current_user.id

    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You do not have access "
                "to this inspection"
            ),
        )

    return {

        "id":
            inspection.id,

        "user_id":
            inspection.user_id,

        "image_path":
            inspection.image_path,

        "product_category":
            inspection.product_category,

        "prediction":
            inspection.prediction,

        "anomaly_score":
            inspection.anomaly_score,

        "threshold":
            inspection.threshold,

        "created_at":
            inspection.created_at,
    }


# =========================================================
# SUPERVISOR DASHBOARD
#
# FACTORY SUPERVISOR ONLY
# =========================================================

@app.get("/supervisor")
def supervisor_dashboard(

    current_user: User = Depends(
        require_supervisor
    ),

    db: Session = Depends(
        get_db
    ),

):

    total_inspections = (
        db.query(Inspection)
        .count()
    )

    pending_inspections = (

        db.query(Inspection)

        .filter(
            Inspection.prediction
            == "pending"
        )

        .count()
    )

    passed_inspections = (

        db.query(Inspection)

        .filter(
            Inspection.prediction
            == "pass"
        )

        .count()
    )

    defective_inspections = (

        db.query(Inspection)

        .filter(
            Inspection.prediction
            == "defect"
        )

        .count()
    )

    return {

        "total_inspections":
            total_inspections,

        "pending_inspections":
            pending_inspections,

        "passed_inspections":
            passed_inspections,

        "defective_inspections":
            defective_inspections,
    }


# =========================================================
# QUALITY ENGINEER DASHBOARD
#
# QUALITY ENGINEER ONLY
# =========================================================

@app.get("/quality-engineer")
def quality_engineer_dashboard(

    current_user: User = Depends(
        require_quality_engineer
    ),

    db: Session = Depends(
        get_db
    ),

):

    total_inspections = (

        db.query(Inspection)

        .filter(
            Inspection.user_id
            == current_user.id
        )

        .count()
    )

    pending_inspections = (

        db.query(Inspection)

        .filter(

            Inspection.user_id
            == current_user.id,

            Inspection.prediction
            == "pending",

        )

        .count()
    )

    passed_inspections = (

        db.query(Inspection)

        .filter(

            Inspection.user_id
            == current_user.id,

            Inspection.prediction
            == "pass",

        )

        .count()
    )

    defective_inspections = (

        db.query(Inspection)

        .filter(

            Inspection.user_id
            == current_user.id,

            Inspection.prediction
            == "defect",

        )

        .count()
    )

    return {

        "total_inspections":
            total_inspections,

        "pending_inspections":
            pending_inspections,

        "passed_inspections":
            passed_inspections,

        "defective_inspections":
            defective_inspections,
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {

        "status":
            "healthy",

        "service":
            "VisionInspect AI",
    }


# =========================================================
# PRINT ALL ROUTES
# =========================================================

for route in app.routes:

    if hasattr(route, "methods"):

        print(
            f"{route.path} -> "
            f"{route.methods}"
        )