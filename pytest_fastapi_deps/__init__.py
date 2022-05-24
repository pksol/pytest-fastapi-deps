# type: ignore[attr-defined]
"""A fixture which allows easy replacement of fastapi dependencies for testing"""

import typing

import contextlib
import sys

import pytest as pytest
from fastapi import FastAPI

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()


class DependencyOverrider:
    """
    Allows to override the fastapi dependencies inside a cleanable context.


    Taken from https://stackoverflow.com/a/68687967/3800552 by
    https://stackoverflow.com/users/8944325/mat-win .

    Args:
        app: the fastapi app
        overrides: a dictionary of the override mappings where the key is the
            original function and the value is the replacement function.
    """

    def __init__(
        self, app: FastAPI, overrides: typing.Mapping[typing.Callable, typing.Callable]
    ) -> None:
        self.overrides = overrides
        self._app = app
        self._old_overrides = {}

    def __enter__(self):
        for dep, new_dep in self.overrides.items():
            if dep in self._app.dependency_overrides:
                # Save existing overrides
                self._old_overrides[dep] = self._app.dependency_overrides[dep]
            self._app.dependency_overrides[dep] = self._callable_replacement(new_dep)
        return self

    @staticmethod
    def _callable_replacement(new_dep):
        return new_dep if callable(new_dep) else lambda: new_dep

    def __exit__(self, *args: typing.Any) -> None:
        for dep in self.overrides.keys():
            if dep in self._old_overrides:
                # Restore previous overrides
                self._app.dependency_overrides[dep] = self._old_overrides.pop(dep)
            else:
                # Just delete the entry
                del self._app.dependency_overrides[dep]


class FixtureDependencyOverrider:
    def __init__(self, app: FastAPI):
        self.app = app

    def override(self, overrides: typing.Mapping[typing.Callable, typing.Callable]):
        return DependencyOverrider(self.app, overrides)


@pytest.fixture
def fastapi_dep(request):
    parametrized = getattr(request, "param", None)
    context = (
        contextlib.nullcontext()
        if not parametrized
        else FixtureDependencyOverrider(parametrized[0]).override(parametrized[1])
    )
    with context:
        yield FixtureDependencyOverrider
