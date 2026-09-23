from slowapi import Limiter
from slowapi.util import get_remote_address

# key_func=get_remote_address → identifies each attacker by their IP address
# Every unique IP gets its own separate rate limit counter
limiter = Limiter(key_func=get_remote_address)