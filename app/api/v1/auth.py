from __future__ import annotations

import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.core.auth import AuthenticatedUser, LocalTokenVerifier, Role
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/google")
async def google_login() -> RedirectResponse:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")

    state = secrets.token_urlsafe(32)
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
            "state": state,
        }
    )
    response = RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")
    response.set_cookie("google_oauth_state", state, httponly=True, max_age=600, samesite="lax", secure=settings.environment == "production")
    return response


@router.get("/google/callback")
async def google_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None) -> RedirectResponse:
    if error or not code or not state or not secrets.compare_digest(state, request.cookies.get("google_oauth_state", "")):
        raise HTTPException(status_code=400, detail="Invalid Google OAuth callback")

    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            },
        )
        token_response.raise_for_status()
        google_tokens = token_response.json()
        access_token = google_tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=502, detail="Google did not return an access token")

        profile_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_response.raise_for_status()
        profile = profile_response.json()

    user_id = str(profile.get("sub", ""))
    if not user_id:
        raise HTTPException(status_code=502, detail="Google profile has no subject")

    verifier = LocalTokenVerifier(
        settings.auth_secret,
        settings.auth_issuer,
        settings.auth_audience,
        settings.auth_token_lifetime_seconds,
    )
    local_token = verifier.create_local_token(
        AuthenticatedUser(user_id=f"google:{user_id}", role=Role.STUDENT, student_id=f"google:{user_id}"),
    )
    redirect = RedirectResponse(f"{settings.frontend_url}/?access_token={local_token}&auth_provider=google")
    redirect.delete_cookie("google_oauth_state")
    return redirect
