import time


class RateLimiterMiddleware:
    """
    Мидл для ограничения числа запросов
    """
    def __init__(self, limit=10):
        self.connections = {}
        self.limit = limit

    async def __call__(self, sid, environ):
        now = time.time()
        if sid not in self.connections:
            self.connections[sid] = {'timestamp': now, 'count': 1}
        else:
            conn = self.connections[sid]
            if now - conn['timestamp'] > 1:
                conn['timestamp'] = now
                conn['count'] = 1
            else:
                conn['count'] += 1
                if conn['count'] > self.limit:
                    return False  # Disconnect, если превышен лимит
        return True
