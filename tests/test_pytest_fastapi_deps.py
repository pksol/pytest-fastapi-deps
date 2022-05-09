def pytest_run_verify(testdir, test_functions):
    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    if test_functions:
        test_functions = (
            test_functions if isinstance(test_functions, list) else [test_functions]
        )
        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [f"*::{test_function} PASSED*" for test_function in test_functions]
        )

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_fastapi_dep_fixture_exists(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile(
        """
        def test_sth(fastapi_dep):
            assert fastapi_dep
    """
    )

    pytest_run_verify(testdir, "test_sth")


def test_public_api(testdir):
    testdir.copy_example("test_public_api.py")
    testdir.runpytest()
    pytest_run_verify(testdir, [])
