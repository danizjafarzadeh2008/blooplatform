import time
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.conf import settings

class GlobalRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = getattr(settings, "RATE_LIMIT_DEFAULT", 100)
        self.window = getattr(settings, "RATE_LIMIT_WINDOW_SECONDS", 60)

    def __call__(self, request):
        if request.path in ("/health", "/healthz", "/ping"):
            return HttpResponse("ok")

        ip = self._client_ip(request)
        key = f"rate:{ip}:{int(time.time() // self.window)}"
        count = cache.get(key, 0)

        if count >= self.limit:
            return JsonResponse({"detail": "Too Many Requests"}, status=429)

        cache.incr(key) if cache.get(key) is not None else cache.set(key, 1, timeout=self.window)
        response = self.get_response(request)
        remaining = max(self.limit - (count + 1), 0)
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(self.window)
        return response

    def _client_ip(self, request) -> str:
        hdr = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("HTTP_X_REAL_IP")
        if hdr:
            return hdr.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")
