"""Token blacklist for revoked tokens."""

import asyncio
from collections import OrderedDict
from datetime import datetime, timedelta


class TokenBlacklist:
    """In-memory token blacklist with automatic cleanup of expired entries."""
    
    def __init__(self, max_size: int = 10000):
        self._tokens = OrderedDict()
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def revoke_token(self, token: str, expires_in_hours: int = 168) -> None:
        """Revoke a token."""
        async with self._lock:
            now = datetime.utcnow()
            
            # Clean up expired tokens
            expired = [t for t, exp in self._tokens.items() if exp < now]
            for t in expired:
                del self._tokens[t]
            
            # Add token with expiration
            expires_at = now + timedelta(hours=expires_in_hours)
            self._tokens[token] = expires_at
            
            # Remove oldest tokens if over max size
            while len(self._tokens) > self._max_size:
                self._tokens.popitem(last=False)
    
    def is_token_revoked(self, token: str) -> bool:
        """Check if a token is revoked."""
        if token not in self._tokens:
            return False
        
        expires_at = self._tokens[token]
        if expires_at < datetime.utcnow():
            # Token expired, remove from blacklist
            del self._tokens[token]
            return False
        
        return True


# Global instance
_token_blacklist = TokenBlacklist()


async def revoke_token(token: str, expires_in_hours: int = 168) -> None:
    """Revoke a token."""
    await _token_blacklist.revoke_token(token, expires_in_hours)


def is_token_revoked(token: str) -> bool:
    """Check if a token is revoked."""
    return _token_blacklist.is_token_revoked(token)
