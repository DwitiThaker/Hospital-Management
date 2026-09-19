def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: tests requiring external services",
    )
