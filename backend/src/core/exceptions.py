from typing import Any, Optional


class ShareBookException(Exception):  
    status_code: int = 400 

    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None, 
        details: Optional[dict] = None,
        status_code: Optional[int] = None
    ):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class DuplicateEmailException(ShareBookException):
    status_code = 409

    def __init__(self, email: str):
        super().__init__(
            message=f"Email '{email}' is already registered",
            code="DUPLICATE_EMAIL",
            details={"email": email}
        )


class InvalidCredentialsException(ShareBookException):
    status_code = 401

    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS"
        )


class UserNotFoundException(ShareBookException):
    status_code = 404

    def __init__(self, user_id: Any = None):
        details = {}
        if user_id:
            message = f"User with id '{user_id}' not found"
            details["user_id"] = str(user_id)
        else:
            message = "User not found"

        super().__init__(
            message=message,
            code="USER_NOT_FOUND",
            details=details
        )

class RefreshTokenInvalidException(ShareBookException):
    status_code = 401

    def __init__(self):
        super().__init__(
            message="Invalid or expired refresh token",
            code="INVALID_REFRESH_TOKEN"
        )

class PasswordTooWeakException(ShareBookException):
    status_code = 400

    def __init__(self, reason: str):
        super().__init__(
            message=f"Password too weak: {reason}",
            code="PASSWORD_TOO_WEAK",
            details={"reason": reason}
        )


class BookNotFoundException(ShareBookException):
    status_code = 404

    def __init__(self, book_id: Any = None):
        details = {}
        if book_id:
            message = f"Book with id '{book_id}' not found"
            details["book_id"] = str(book_id)
        else:
            message = "Book not found"
        
        super().__init__(
            message=message,
            code="BOOK_NOT_FOUND",
            details=details
        )


class DuplicateISBNException(ShareBookException):
    status_code = 409

    def __init__(self, isbn: str):
        super().__init__(
            message=f"Book with ISBN '{isbn}' already exists",
            code="DUPLICATE_ISBN",
            details={"isbn": isbn}
        )


class NotBookOwnerException(ShareBookException):
    status_code = 403

    def __init__(self):
        super().__init__(
            message="You are not the owner of this book",
            code="NOT_BOOK_OWNER"
        )
