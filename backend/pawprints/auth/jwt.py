from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from config import Config

bearer_scheme = HTTPBearer()

config = Config()


def _utcnow() -> datetime:
    """Return current UTC time as an aware datetime."""
    return datetime.now(UTC)


def _encode(payload: dict[str, Any]) -> str:
    """Encode a JWT with the configured SECRET_KEY and ALGORITHM."""
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def _decode(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.

    Parameters
    ----------
    token : str
        Encoded JWT.

    Returns
    -------
    dict
        Decoded payload.

    Raises
    ------
    HTTPException
        If the token is invalid or expired.
    """
    try:
        # jose will validate `exp` automatically; leeway helps with minor clock skew.
        return jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
            options={"verify_aud": False},
        )
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")


def create_jwt_token(data: dict[str, Any]) -> tuple[str, datetime]:
    """
    Create an access JWT from the supplied payload.

    Parameters
    ----------
    data : dict
        Claims to include in the token (e.g., ``{"username": "...", "email": "..."}``).

    Returns
    -------
    (str, datetime)
        A tuple of (encoded JWT, expiration datetime in UTC).

    Notes
    -----
    - The function sets an ``exp`` claim based on ``ACCESS_TOKEN_EXPIRE_MINUTES``.
    - The expiration returned is timezone-aware UTC.
    """
    to_encode = data.copy()
    expire = _utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return _encode(to_encode), expire


def decode_jwt_token(token: str) -> dict[str, Any]:
    """
    Decode a JWT and return its payload.

    Parameters
    ----------
    token : str
        Encoded JWT.

    Returns
    -------
    dict
        Decoded payload.

    Raises
    ------
    HTTPException
        If the token is invalid or expired.
    """
    return _decode(token)
