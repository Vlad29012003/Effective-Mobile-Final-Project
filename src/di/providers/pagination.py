from dishka import Provider, Scope, provide
from fastapi import Request

from configs import Settings
from presentations.api.schemas.common import PaginationParams


class PaginationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def pagination_params(self, request: Request, settings: Settings) -> PaginationParams:
        qp = request.query_params

        try:
            page = int(qp.get("page", settings.PAGINATION_DEFAULT_PAGE))
        except (ValueError, TypeError):
            page = settings.PAGINATION_DEFAULT_PAGE
        if page < 1:
            page = 1

        try:
            page_size = int(qp.get("page_size", settings.PAGINATION_DEFAULT_PAGE_SIZE))
        except (ValueError, TypeError):
            page_size = settings.PAGINATION_DEFAULT_PAGE_SIZE
        if page_size < 1:
            page_size = settings.PAGINATION_DEFAULT_PAGE_SIZE
        if page_size > settings.PAGINATION_MAX_PAGE_SIZE:
            page_size = settings.PAGINATION_MAX_PAGE_SIZE

        return PaginationParams(page=page, page_size=page_size, sort=qp.get("sort"))
