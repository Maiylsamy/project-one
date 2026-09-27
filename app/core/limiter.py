# app/core/limiter.py
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

def get_key(request):
    # Return fixed key during tests → all requests share one "slot"
    # but since limit is per-key, unique key = no limit effectively
    if os.getenv("TESTING") == "true":
        return f"test-{id(request)}"
        # ↑ Each request gets unique key → never accumulates toward limit
    return get_remote_address(request)

limiter = Limiter(key_func=get_key)