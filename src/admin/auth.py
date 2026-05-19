from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response


class AdminAuth(AuthenticationBackend):
    def __init__(self, username: str, password: str, secret_key: str) -> None:
        super().__init__(secret_key=secret_key)
        self._username = username
        self._password = password

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == self._username and password == self._password:
            request.session["admin_authenticated"] = True
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | Response:
        return bool(request.session.get("admin_authenticated"))
