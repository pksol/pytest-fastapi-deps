import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

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


client = TestClient(app)


def test_get_default_dep():
    response = client.get("/depends")
    assert response.status_code == 200
    assert response.json() == {
        "first_dep": {"skip": 0, "limit": 100},
        "second_dep": {"skip": 20, "limit": 50},
    }


def test_get_override_single_dep(fastapi_dep):
    with fastapi_dep(app).override({first_dep: lambda: {"my": "override"}}):
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": {"my": "override"},
            "second_dep": {"skip": 20, "limit": 50},
        }


def test_get_override_unrelated_dep(fastapi_dep):
    with fastapi_dep(app).override(
        {
            first_dep: lambda: {"my": "override"},
            test_get_override_unrelated_dep: lambda: {"another": "override"},
        }
    ):
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": {"my": "override"},
            "second_dep": {"skip": 20, "limit": 50},
        }


def test_get_override_two_dep(fastapi_dep):
    with fastapi_dep(app).override(
        {
            first_dep: lambda: {"my": "override"},
            second_dep: lambda: {"another": "override"},
        }
    ):
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": {"my": "override"},
            "second_dep": {"another": "override"},
        }


def test_get_override_dep_inner_context(fastapi_dep):
    with fastapi_dep(app).override({first_dep: lambda: {"my": "override"}}):
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": {"my": "override"},
            "second_dep": {"skip": 20, "limit": 50},
        }

        # add another override
        with fastapi_dep(app).override({second_dep: lambda: {"another": "override"}}):
            response = client.get("/depends")
            assert response.status_code == 200
            assert response.json() == {
                "first_dep": {"my": "override"},
                "second_dep": {"another": "override"},
            }

        # second override is gone - expect that only the first is overridden
        response = client.get("/depends")
        assert response.status_code == 200
        assert response.json() == {
            "first_dep": {"my": "override"},
            "second_dep": {"skip": 20, "limit": 50},
        }

    # back to normal behaviour
    response = client.get("/depends")
    assert response.status_code == 200
    assert response.json() == {
        "first_dep": {"skip": 0, "limit": 100},
        "second_dep": {"skip": 20, "limit": 50},
    }


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
