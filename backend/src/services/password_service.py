from src.services.interfaces import IPasswordService
from src.core.security import get_password_hash, verify_password as verify_pwd


class PasswordService(IPasswordService):
    def hash(self, password: str) -> str:
        return get_password_hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_pwd(plain_password, hashed_password)
