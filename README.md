# pytest-fastapi-deps

<div align="center">

[![Build status](https://github.com/pksol/pytest-fastapi-deps/workflows/build/badge.svg?branch=master&event=push)](https://github.com/pksol/pytest-fastapi-deps/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/pytest-fastapi-deps.svg)](https://pypi.org/project/pytest-fastapi-deps/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/pksol/pytest-fastapi-deps/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pksol/pytest-fastapi-deps/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/pksol/pytest-fastapi-deps/releases)
[![License](https://img.shields.io/github/license/pksol/pytest-fastapi-deps)](https://github.com/pksol/pytest-fastapi-deps/blob/master/LICENSE)

A fixture which allows easy replacement of fastapi dependencies for testing

</div>

## Installation

```bash
pip install pytest-fastapi-deps
```

or install with `Poetry`

```bash
poetry add pytest-fastapi-deps
```

## Use case
Suppose that you have this fastapi endpoint which has a couple of dependencies:
```python
from fastapi import Depends, FastAPI

app = FastAPI()


async def first_dep():
    return {"skip": 0, "limit": 100}


def second_dep():
    return {"skip": 20, "limit": 50}


@app.get("/depends/")
async def get_depends(
    first_dep: dict = Depends(first_dep), second_dep: dict = Depends(second_dep)
):
    return {"first_dep": first_dep, "second_dep": second_dep}
```

For simplicity, this example holds static dictionaries, but in reality these 
dependencies can be anything: dynamic configuration, database information, the 
current user's information, etc.

If you want to test your fastapi endpoint you might wish to mock or replace these 
dependencies with your test code.

This is where the `fastapi_dep` fixture comes to play.

## Usage
The most basic usage is to replace a dependency with a context manager:

```python
from my_project.main import app, first_dep, second_dep
from fastapi.testclient import TestClient

client = TestClient(app)

def my_second_override():
    return {"another": "override"}


def test_get_override_two_dep(fastapi_dep):
    with fastapi_dep(app).override(
        {
            first_dep: "plain_override_object",
            second_dep: my_second_override,
        }
    ):
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": "plain_override_object",
            "second_dep": {"another": "override"},
        }
```

Note how easy it is: you add the `fastapi_dep` fixture, initialize it with the fastapi
`app` and send a dictionary of overrides: the keys are the original functions while the 
values are plain objects that would be returned or replacement functions that would be 
called.

If your use case is to replace the dependencies for the entire duration of your test,
you can use pytest [indirect parameters](https://docs.pytest.org/en/latest/example/parametrize.html#indirect-parametrization) to simplify the body of your test:

```python
import pytest

from my_project.main import app, first_dep, second_dep
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.mark.parametrize(
    "fastapi_dep",
    [
        (
            app,
            {first_dep: lambda: {"my": "override"}},
        )
    ],
    indirect=True,
)
def test_get_override_indirect_dep_param(fastapi_dep):
    response = client.get("/depends")
    assert response.status_code == 200
    assert response.json() == {
        "first_dep": {"my": "override"},
        "second_dep": {"skip": 20, "limit": 50},
    }
```
You must use `indirect=True` and pass a tuple where the first item is the `app` and the
second item is the dictionary with replacement functions.

You can do more fancy stuff and utilize the nature of nested python context managers:

```python
from my_project.main import app, first_dep, second_dep
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_override_dep_inner_context(fastapi_dep):
    with fastapi_dep(app).override({first_dep: lambda: {"my": "override"}}):
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": {"my": "override"},  # overridden 
            "second_dep": {"skip": 20, "limit": 50},  # stayed the same
        }

        # add another override
        with fastapi_dep(app).override({second_dep: lambda: {"another": "override"}}):
            response = client.get("/depends")
            assert response.status_code == 200
            assert response.json() == {
                "first_dep": {"my": "override"},  # overridden 
                "second_dep": {"another": "override"},  # overridden 
            }

        # second override is gone - expect that only the first is overridden
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": {"my": "override"},  # overridden 
            "second_dep": {"skip": 20, "limit": 50},  # returned to normal behaviour 
        }

    # back to normal behaviour
    response = client.get("/depends")
    assert response.status_code == 200
    assert response.json() == {
        "first_dep": {"skip": 0, "limit": 100},
        "second_dep": {"skip": 20, "limit": 50},
    }
```

## 📈 Releases

You can see the list of available releases on the [GitHub Releases](https://github.com/pksol/pytest-fastapi-deps/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

## 🛡 License

[![License](https://img.shields.io/github/license/pksol/pytest-fastapi-deps)](https://github.com/pksol/pytest-fastapi-deps/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/pksol/pytest-fastapi-deps/blob/master/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{pytest-fastapi-deps,
  author = {Peter Kogan},
  title = {A fixture which allows easy replacement of fastapi dependencies for testing},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/pksol/pytest-fastapi-deps}}
}
```

## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)
