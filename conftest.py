import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """Reset cache (DRF throttle counters live here) between tests."""
    cache.clear()
    yield
    cache.clear()
