from typing import Any, Optional


class ShareBookException(Exception):
    status_code: int = 400

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict] = None,
        status_code: Optional[int] = None,
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(ShareBookException):
    status_code = 404

    def __init__(self, entity: str = "Resource", entity_id: Any = None):
        details = {}
        if entity_id:
            message = f"{entity} with id '{entity_id}' not found"
            details[f"{entity.lower()}_id"] = str(entity_id)
        else:
            message = f"{entity} not found"
        super().__init__(message=message, code=f"{entity.upper()}_NOT_FOUND", details=details)


class BusinessLogicException(ShareBookException):
    status_code = 422

    def __init__(self, message: str = "Business logic error"):
        super().__init__(message=message, code="BUSINESS_LOGIC_ERROR")


class DuplicateEmailException(ShareBookException):
    status_code = 409

    def __init__(self, email: str):
        super().__init__(message=f"Email '{email}' is already registered", code="DUPLICATE_EMAIL", details={"email": email},)


class InvalidCredentialsException(ShareBookException):
    status_code = 401

    def __init__(self):
        super().__init__(message="Invalid email or password", code="INVALID_CREDENTIALS")


class UserNotFoundException(ShareBookException):
    status_code = 404

    def __init__(self, user_id: Any = None):
        details = {}
        if user_id:
            message = f"User with id '{user_id}' not found"
            details["user_id"] = str(user_id)
        else:
            message = "User not found"
        super().__init__(message=message, code="USER_NOT_FOUND", details=details)


class RefreshTokenInvalidException(ShareBookException):
    status_code = 401

    def __init__(self):
        super().__init__(message="Invalid or expired refresh token", code="INVALID_REFRESH_TOKEN")


class PasswordTooWeakException(ShareBookException):
    status_code = 400

    def __init__(self, reason: str):
        super().__init__(message=f"Password too weak: {reason}", code="PASSWORD_TOO_WEAK", details={"reason": reason},)


class BookNotFoundException(ShareBookException):
    status_code = 404

    def __init__(self, book_id: Any = None):
        details = {}
        if book_id:
            message = f"Book with id '{book_id}' not found"
            details["book_id"] = str(book_id)
        else:
            message = "Book not found"
        super().__init__(message=message, code="BOOK_NOT_FOUND", details=details)


class DuplicateISBNException(ShareBookException):
    status_code = 409

    def __init__(self, isbn: str):
        super().__init__(
            message=f"Book with ISBN '{isbn}' already exists",
            code="DUPLICATE_ISBN",
            details={"isbn": isbn},
        )


class NotBookOwnerException(ShareBookException):
    status_code = 403

    def __init__(self):
        super().__init__(message="You are not the owner of this book", code="NOT_BOOK_OWNER")


class NotAuthorizedException(ShareBookException):
    status_code = 403

    def __init__(self, message: str = "Action not authorized"):
        super().__init__(message=message, code="NOT_AUTHORIZED")


class LoanRequestNotFoundException(ShareBookException):
    status_code = 404

    def __init__(self, request_id: Any = None):
        details = {}
        if request_id:
            message = f"Loan request with id '{request_id}' not found"
            details["request_id"] = str(request_id)
        else:
            message = "Loan request not found"
        super().__init__(message=message, code="LOAN_REQUEST_NOT_FOUND", details=details)


class SelfModificationException(ShareBookException):
    status_code = 400

    def __init__(self, action: str = "modify"):
        messages = {
            "role": "You cannot change your own role",
            "password": "Use password change endpoint to change your own password",
            "delete": "You cannot delete your own account",
            "modify": "You cannot modify your own account",
        }
        super().__init__(message=messages.get(action, messages["modify"]), code="SELF_MODIFICATION_NOT_ALLOWED")


class InvalidRoleException(ShareBookException):
    status_code = 400

    def __init__(self, role: str, allowed_roles: list[str] = None):
        allowed = allowed_roles or ["reader", "admin"]
        super().__init__(
            message=f"Invalid role '{role}'. Use: {', '.join(allowed)}",
            code="INVALID_ROLE",
            details={"role": role, "allowed_roles": allowed},
        )


class DuplicateEntryError(ShareBookException):
    status_code = 409

    def __init__(self, message: str = "Entity already exists"):
        super().__init__(message=message, code="DUPLICATE_ENTRY")


class DatabaseError(ShareBookException):
    status_code = 500

    def __init__(self, message: str = "Database error"):
        super().__init__(message=message, code="DATABASE_ERROR")


class DatabaseLockError(ShareBookException):
    status_code = 503

    def __init__(self, message: str = "Database lock error"):
        super().__init__(message=message, code="DATABASE_LOCK_ERROR")


class LoanNotFoundException(ShareBookException):
    status_code = 404

    def __init__(self, loan_id: Any = None):
        details = {}
        if loan_id:
            message = f"Loan with id '{loan_id}' not found"
            details["loan_id"] = str(loan_id)
        else:
            message = "Loan not found"
        super().__init__(message=message, code="LOAN_NOT_FOUND", details=details)


class ValidationException(ShareBookException):
    status_code = 400

    def __init__(self, message: str = "Validation failed", field: Optional[str] = None):
        details = {}
        if field:
            details["field"] = field
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class InvalidBookStatusException(ShareBookException):
    status_code = 400

    def __init__(self, message: str = "Invalid book status"):
        super().__init__(message=message, code="INVALID_BOOK_STATUS")


class DuplicateLoanRequestException(ShareBookException):
    status_code = 409

    def __init__(self):
        super().__init__(message="You already have a pending request for this book", code="DUPLICATE_LOAN_REQUEST")


class InvalidLoanRequestStatusException(ShareBookException):
    status_code = 400

    def __init__(self, message: str = "Invalid loan request status"):
        super().__init__(message=message, code="INVALID_LOAN_REQUEST_STATUS")


class AuthenticationException(ShareBookException):
    status_code = 401

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class ServiceUnavailableException(ShareBookException):
    status_code = 503

    def __init__(self, message: str = "Service unavailable"):
        super().__init__(message=message, code="SERVICE_UNAVAILABLE")


class CSRFTokenMissingException(ShareBookException):
    status_code = 403

    def __init__(self):
        super().__init__(message="CSRF token missing", code="CSRF_TOKEN_MISSING")


class CSRFTokenInvalidException(ShareBookException):
    status_code = 403

    def __init__(self):
        super().__init__(message="CSRF token invalid", code="CSRF_TOKEN_INVALID")


class InactiveUserException(ShareBookException):
    status_code = 403

    def __init__(self):
        super().__init__(message="User account is inactive", code="INACTIVE_USER")
