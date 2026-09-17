import base64
import hashlib
import hmac
import json
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class AuthError(Exception):
    """Base error for authentication and authorization failures."""


class AuthenticationError(AuthError):
    pass


class AuthorizationError(AuthError):
    pass


class Role(str, Enum):
    ATHLETE = "ATHLETE"
    STUDENT = "STUDENT"
    COACH = "COACH"
    ASSISTANT_COACH = "ASSISTANT_COACH"
    TEAM_MANAGER = "TEAM_MANAGER"
    GUARDIAN = "GUARDIAN"
    ADMIN = "ADMIN"


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1)
    role: Role
    student_id: str | None = None
    authorized_student_ids: frozenset[str] = frozenset()
    coach_id: str | None = None


class LocalTokenVerifier:
    """Small HMAC verifier used until an external identity provider is added."""

    def __init__(self, secret: str, issuer: str, audience: str, lifetime_seconds: int) -> None:
        self.secret = secret.encode("utf-8")
        self.issuer = issuer
        self.audience = audience
        self.lifetime_seconds = lifetime_seconds

    def verify_bearer_token(self, authorization: str | None) -> AuthenticatedUser:
        if not authorization or not authorization.startswith("Bearer "):
            raise AuthenticationError("Authentication failed")

        token = authorization[7:].strip()
        parts = token.split(".")
        if len(parts) != 3:
            raise AuthenticationError("Authentication failed")

        encoded_header, encoded_payload, encoded_signature = parts
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        expected_signature = hmac.new(self.secret, signing_input, hashlib.sha256).digest()
        try:
            actual_signature = _decode_base64(encoded_signature)
            header = _decode_json(encoded_header)
            claims = _decode_json(encoded_payload)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            raise AuthenticationError("Authentication failed") from None

        if not hmac.compare_digest(actual_signature, expected_signature):
            raise AuthenticationError("Authentication failed")
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise AuthenticationError("Authentication failed")
        if claims.get("iss") != self.issuer or claims.get("aud") != self.audience:
            raise AuthenticationError("Authentication failed")

        now = int(time.time())
        if not isinstance(claims.get("exp"), int) or claims["exp"] <= now:
            raise AuthenticationError("Authentication failed")
        if claims.get("iat", now) > now + 30:
            raise AuthenticationError("Authentication failed")

        try:
            return AuthenticatedUser(
                user_id=claims["sub"],
                role=claims["role"],
                student_id=claims.get("student_id"),
                authorized_student_ids=frozenset(claims.get("student_scope", [])),
                coach_id=claims.get("coach_id"),
            )
        except (KeyError, TypeError, ValidationError):
            raise AuthenticationError("Authentication failed") from None

    def create_local_token(self, user: AuthenticatedUser, now: int | None = None) -> str:
        issued_at = int(time.time()) if now is None else now
        header = {"alg": "HS256", "typ": "JWT"}
        claims: dict[str, Any] = {
            "sub": user.user_id,
            "role": user.role.value,
            "iss": self.issuer,
            "aud": self.audience,
            "iat": issued_at,
            "exp": issued_at + self.lifetime_seconds,
            "student_scope": sorted(user.authorized_student_ids),
        }
        if user.student_id is not None:
            claims["student_id"] = user.student_id
        if user.coach_id is not None:
            claims["coach_id"] = user.coach_id

        encoded_header = _encode_json(header)
        encoded_claims = _encode_json(claims)
        signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
        signature = hmac.new(self.secret, signing_input, hashlib.sha256).digest()
        return f"{encoded_header}.{encoded_claims}.{_encode_base64(signature)}"


class AuthorizationService:
    def authorize_student(
        self,
        principal: AuthenticatedUser,
        requested_student_id: str | None,
    ) -> str:
        if principal.role in {Role.STUDENT, Role.ATHLETE}:
            if principal.student_id is None:
                raise AuthorizationError("Authorization failed")
            if requested_student_id and requested_student_id != principal.student_id:
                raise AuthorizationError("Authorization failed")
            return principal.student_id

        if requested_student_id:
            if principal.role is Role.ADMIN or requested_student_id in principal.authorized_student_ids:
                return requested_student_id
            raise AuthorizationError("Authorization failed")

        if len(principal.authorized_student_ids) == 1:
            return next(iter(principal.authorized_student_ids))
        raise AuthorizationError("Authorization failed")


def _encode_base64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode_base64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _encode_json(value: dict[str, Any]) -> str:
    return _encode_base64(json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def _decode_json(value: str) -> dict[str, Any]:
    decoded = _decode_base64(value).decode("utf-8")
    result = json.loads(decoded)
    if not isinstance(result, dict):
        raise ValueError("Token section must be an object")
    return result