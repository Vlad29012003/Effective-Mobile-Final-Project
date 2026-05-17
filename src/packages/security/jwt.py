from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Literal, TypedDict

import jwt


class JwtTokenPayload(TypedDict, total=False):
    sub: str  # subject — user id
    type: Literal["access", "refresh"]
    sid: str  # session id (used with refresh tokens)
    iat: int  # issued at
    exp: int  # expiration
    iss: str  # issuer
    aud: str  # audience


@dataclass(slots=True)
class JwtConfig:
    secret_key: str
    algorithm: str
    issuer: str | None = None
    audience: str | None = None
    leeway_seconds: int = 30


class JwtManager:
    def __init__(self, config: JwtConfig) -> None:
        self._cfg = config

    def encode(self, payload: JwtTokenPayload, *, ttl: dt.timedelta) -> str:
        now = dt.datetime.now(dt.UTC)
        to_encode: dict[str, Any] = dict(payload)
        to_encode.setdefault("iat", int(now.timestamp()))
        to_encode.setdefault("exp", int((now + ttl).timestamp()))
        if self._cfg.issuer:
            to_encode.setdefault("iss", self._cfg.issuer)
        if self._cfg.audience:
            to_encode.setdefault("aud", self._cfg.audience)
        return jwt.encode(to_encode, self._cfg.secret_key, algorithm=self._cfg.algorithm)

    def decode(self, token: str) -> JwtTokenPayload:
        payload = jwt.decode(
            token,
            self._cfg.secret_key,
            algorithms=[self._cfg.algorithm],
            audience=self._cfg.audience,
            issuer=self._cfg.issuer,
            options={"require": ["exp", "iat"]},
            leeway=self._cfg.leeway_seconds,
        )
        return payload
