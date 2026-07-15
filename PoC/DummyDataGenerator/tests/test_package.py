import dummygen


def test_package_exposes_version():
    assert dummygen.__version__ == "0.1.0"
