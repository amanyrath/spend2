"""FastAPI entrypoint for SpendSense API.

This module provides RESTful API endpoints for the SpendSense recommendation engine,
including personalized recommendations, user personas, and feature signals.
"""

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import os
from datetime import datetime

# Import SpendSense modules with comprehensive fallback handling
generate_recommendations = None
get_persona_assignment = None
get_user_features = None

# Try multiple import paths
try:
    # Try importing from src.engine (may fail due to missing subdirectories)
    from src.engine import generate_recommendations
except ImportError as e:
    print(f"Warning: Could not import from src.engine: {e}")

try:
    # Try importing from engine directly
    if generate_recommendations is None:
        from engine import generate_recommendations
except ImportError:
    pass

try:
    # Try importing persona assignment
    from src.assignment import get_persona_assignment
except ImportError:
    try:
        from assignment import get_persona_assignment
    except ImportError:
        pass

try:
    # Try importing signal detection
    from src.signal_detection import get_user_features
except ImportError:
    try:
        from signal_detection import get_user_features
    except ImportError:
        pass

# Define stub functions if imports failed
if generate_recommendations is None:
    def generate_recommendations(user_id: str, time_window: str = "30d"):
        """Stub function - recommendation engine not available."""
        return []

if get_persona_assignment is None:
    def get_persona_assignment(user_id: str, time_window: str = "30d"):
        """Stub function - persona assignment not available."""
        return {"persona": "general_wellness", "primary_persona": "general_wellness"}

if get_user_features is None:
    def get_user_features(user_id: str, time_window: str = "30d"):
        """Stub function - signal detection not available."""
        return {}

# Initialize FastAPI app
app = FastAPI(
    title="SpendSense API",
    description="Personalized financial recommendations powered by behavioral signals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on deployment environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(description="Service health status")
    timestamp: str = Field(description="Current timestamp")
    version: str = Field(description="API version")


class RecommendationsResponse(BaseModel):
    """Recommendations response."""
    user_id: str = Field(description="User identifier")
    time_window: str = Field(description="Time window used for analysis")
    recommendations: List[Dict[str, Any]] = Field(description="List of personalized recommendations")
    count: int = Field(description="Number of recommendations")


class PersonaResponse(BaseModel):
    """User persona response."""
    user_id: str = Field(description="User identifier")
    time_window: str = Field(description="Time window used for analysis")
    persona_assignment: Optional[Dict[str, Any]] = Field(description="Persona assignment details")


class SignalsResponse(BaseModel):
    """User signals response."""
    user_id: str = Field(description="User identifier")
    time_window: str = Field(description="Time window used for analysis")
    signals: Dict[str, Any] = Field(description="Computed behavioral signals")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")


# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "SpendSense API",
        "version": "1.0.0",
        "description": "Personalized financial recommendations powered by behavioral signals",
        "documentation": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and deployment verification."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get(
    "/api/v1/recommendations/{user_id}",
    response_model=RecommendationsResponse,
    tags=["Recommendations"],
    responses={
        404: {"model": ErrorResponse, "description": "User not found or no recommendations available"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_recommendations(
    user_id: str,
    time_window: str = Query(
        default="30d",
        regex="^(30d|180d)$",
        description="Time window for analysis: 30d or 180d"
    ),
    authorization: Optional[str] = Header(None, description="Firebase ID token")
):
    """
    Get personalized recommendations for a user.

    Returns a list of education content and partner offers matched to the user's
    financial behavior, persona, and current signals.

    Args:
        user_id: User identifier
        time_window: Time window for analysis (30d or 180d)
        authorization: Optional Firebase authentication token

    Returns:
        RecommendationsResponse with personalized recommendations
    """
    try:
        # TODO: Implement Firebase token verification if authorization header is provided
        # For now, proceed without authentication

        recommendations = generate_recommendations(user_id, time_window)

        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"No recommendations found for user {user_id} in time window {time_window}"
            )

        return RecommendationsResponse(
            user_id=user_id,
            time_window=time_window,
            recommendations=recommendations,
            count=len(recommendations)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@app.get(
    "/api/v1/persona/{user_id}",
    response_model=PersonaResponse,
    tags=["Personas"],
    responses={
        404: {"model": ErrorResponse, "description": "User persona not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_persona(
    user_id: str,
    time_window: str = Query(
        default="30d",
        regex="^(30d|180d)$",
        description="Time window for analysis: 30d or 180d"
    ),
    authorization: Optional[str] = Header(None, description="Firebase ID token")
):
    """
    Get persona assignment for a user.

    Returns the user's assigned persona based on their financial behavior patterns.

    Args:
        user_id: User identifier
        time_window: Time window for analysis (30d or 180d)
        authorization: Optional Firebase authentication token

    Returns:
        PersonaResponse with persona assignment details
    """
    try:
        persona_assignment = get_persona_assignment(user_id, time_window)

        if not persona_assignment:
            raise HTTPException(
                status_code=404,
                detail=f"No persona assignment found for user {user_id}"
            )

        return PersonaResponse(
            user_id=user_id,
            time_window=time_window,
            persona_assignment=persona_assignment
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving persona: {str(e)}"
        )


@app.get(
    "/api/v1/signals/{user_id}",
    response_model=SignalsResponse,
    tags=["Signals"],
    responses={
        404: {"model": ErrorResponse, "description": "User signals not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_signals(
    user_id: str,
    time_window: str = Query(
        default="30d",
        regex="^(30d|180d)$",
        description="Time window for analysis: 30d or 180d"
    ),
    authorization: Optional[str] = Header(None, description="Firebase ID token")
):
    """
    Get behavioral signals for a user.

    Returns computed signals including credit utilization, income stability,
    subscription patterns, and savings behavior.

    Args:
        user_id: User identifier
        time_window: Time window for analysis (30d or 180d)
        authorization: Optional Firebase authentication token

    Returns:
        SignalsResponse with computed behavioral signals
    """
    try:
        signals = get_user_features(user_id, time_window)

        if not signals:
            raise HTTPException(
                status_code=404,
                detail=f"No signals found for user {user_id}"
            )

        return SignalsResponse(
            user_id=user_id,
            time_window=time_window,
            signals=signals
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving signals: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "Resource not found", "detail": str(exc.detail) if hasattr(exc, 'detail') else None}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if os.getenv("DEBUG") else None}
    )


# Application factory for Vercel serverless deployment
def create_app():
    """Create and configure the FastAPI application."""
    return app


# ASGI app for uvicorn
if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn for local development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
