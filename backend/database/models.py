import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector  # Import dla pgvector
from database.config import Base


class User(Base):

    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="reader", nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False       )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc),nullable=False)
    
    user_books: Mapped[List["UserBook"]] = relationship("UserBook", back_populates="user", cascade="all, delete-orphan")
    borrowed_loans: Mapped[List["Loan"]] = relationship("Loan", foreign_keys="Loan.borrower_id", back_populates="borrower")
    lent_loans: Mapped[List["Loan"]] = relationship("Loan", foreign_keys="Loan.lender_id", back_populates="lender")
    outgoing_requests: Mapped[List["LoanRequest"]] = relationship("LoanRequest", foreign_keys="LoanRequest.requester_id", back_populates="requester")
    incoming_requests: Mapped[List["LoanRequest"]] = relationship("LoanRequest", foreign_keys="LoanRequest.owner_id", back_populates="owner")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="sender")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Book(Base):

    __tablename__ = "books" 
    __table_args__ = (UniqueConstraint('isbn', name='uix_book_isbn'),)
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    author: Mapped[Optional[str]] = mapped_column(Text, nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(50), default="pl")
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user_books: Mapped[List["UserBook"]] = relationship("UserBook", back_populates="book", cascade="all, delete-orphan")
    chunks: Mapped[List["BookChunk"]] = relationship("BookChunk", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title={self.title[:30]}..., isbn={self.isbn})>"


class UserBook(Base):

    __tablename__ = "user_books"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="available", nullable=False)
    condition: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_lendable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="user_books")
    book: Mapped["Book"] = relationship("Book", back_populates="user_books")
    active_loan: Mapped[Optional["Loan"]] = relationship(
        "Loan",
        back_populates="user_book",
        uselist=False
    )
    
    def __repr__(self) -> str:
        return f"<UserBook(id={self.id}, book_id={self.book_id}, status={self.status}, condition={self.condition})>"


class Loan(Base):

    __tablename__ = "loans"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id", ondelete="CASCADE"), nullable=False, index=True)
    borrower_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    loan_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    return_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user_book: Mapped["UserBook"] = relationship("UserBook", back_populates="active_loan")
    
    borrower: Mapped["User"] = relationship("User", foreign_keys=[borrower_id], back_populates="borrowed_loans")
    lender: Mapped["User"] = relationship("User", foreign_keys=[lender_id], back_populates="lent_loans")
    
    def __repr__(self) -> str:
        return f"<Loan(id={self.id}, status={self.status}, due={self.due_date})>"
    

class LoanRequest(Base):

    __tablename__ = "loan_requests"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id", ondelete="CASCADE"), nullable=False, index=True)
    requester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id], back_populates="outgoing_requests")
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], back_populates="incoming_requests")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="loan_request", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<LoanRequest(id={self.id}, status={self.status})>"
    

class Message(Base):

    __tablename__ = "messages"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    loan_request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loan_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    loan_request: Mapped["LoanRequest"] = relationship("LoanRequest", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, type={self.message_type}, read={self.is_read})>"

class BookChunk(Base):
    
    __tablename__ = "book_chunks"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    book_title: Mapped[str] = mapped_column(Text, nullable=False)
    book_author: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(1536), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    book: Mapped["Book"] = relationship("Book", back_populates="chunks")
    
    def __repr__(self) -> str:
        return f"<BookChunk(id={self.id}, book={self.book_title[:30]}..., index={self.chunk_index})>"
