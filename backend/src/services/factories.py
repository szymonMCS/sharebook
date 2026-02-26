from sqlalchemy.ext.asyncio import AsyncSession
from src.services.interfaces import (
    IRepositoryFactory,
    IServiceFactory,
    IAuthService,
    IUserService,
    IRegistrationService,
    ITokenService,
    IPasswordService,
)
from database.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.registration_service import RegistrationService
from src.services.token_service import TokenService
from src.services.password_service import PasswordService


class RepositoryFactory(IRepositoryFactory):
    def __init__(self, db: AsyncSession):
        self._db = db

    def create_user_repository(self):
        return UserRepository(self._db)


class ServiceFactory(IServiceFactory):
    def __init__(self, db: AsyncSession = None, repo_factory: IRepositoryFactory = None):
        self._db = db
        self._repo_factory = repo_factory or (RepositoryFactory(db) if db else None)
        self._password_service: IPasswordService = None

    def create_password_service(self) -> IPasswordService:
        if not self._password_service:
            self._password_service = PasswordService()
        return self._password_service

    def create_auth_service(self) -> IAuthService:
        return AuthService(
            user_repo=self._repo_factory.create_user_repository(),
            password_service=self.create_password_service()
        )

    def create_user_service(self) -> IUserService:
        return UserService(
            user_repo=self._repo_factory.create_user_repository()
        )

    def create_registration_service(self) -> IRegistrationService:
        return RegistrationService(
            user_repo=self._repo_factory.create_user_repository(),
            password_service=self.create_password_service()
        )

    def create_token_service(self) -> ITokenService:
        return TokenService(
            user_repo=self._repo_factory.create_user_repository()
        )
