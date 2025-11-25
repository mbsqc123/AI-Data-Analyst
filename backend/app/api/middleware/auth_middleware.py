import jwt
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.env import SECRET_KEY


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths like /login, /signup
        if request.url.path in [
            "/",
            "/docs",
            "/openapi.json",
            "/api/user/v1/login",
            "/api/user/v1/signup",
            "/api/chat/v1/models"
        ]:
            response = await call_next(request)
            return response

        # Also allow access to model-specific endpoints like /api/chat/v1/models/{model_name}
        if request.url.path.startswith("/api/chat/v1/models/"):
            response = await call_next(request)
            return response

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Authorization header missing or invalid"}
            )
        
        print("AUTH HEADER :",auth_header)
        token = auth_header.split(" ")[1]

        try:
            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("id")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Attach the user_email to the request state for access in routes
            request.state.user_id = user_id

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Token has expired"}
            )

        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Invalid token"}
            )

        # Call the next middleware or route handler
        response = await call_next(request)
        return response
