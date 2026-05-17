from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from dishka import AsyncContainer, Container, Provider, make_async_container
from dishka.integrations.fastapi import DishkaRoute, FastapiProvider, setup_dishka
from fastapi import FastAPI

type ContainerLike = Container | AsyncContainer


def build_container(providers: list[Any]) -> AsyncContainer:
    all_providers: list[Provider] = [FastapiProvider(), *providers]
    return make_async_container(*all_providers)


def setup_di(app: FastAPI, container: ContainerLike | None = None) -> ContainerLike:
    if container is None:
        container = build_container([])

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if isinstance(container, AsyncContainer):
                await container.close()
            else:
                container.close()

    app.router.route_class = DishkaRoute
    app.router.lifespan_context = lifespan
    setup_dishka(container=container, app=app)
    return container
