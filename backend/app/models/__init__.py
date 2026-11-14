from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    school_memberships: Mapped[list["SchoolMembership"]] = relationship(
        back_populates="user"
    )
    classroom_memberships: Mapped[list["ClassroomMembership"]] = relationship(
        back_populates="user"
    )
    sent_messages: Mapped[list["Message"]] = relationship(
        back_populates="sender"
    )


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    memberships: Mapped[list["SchoolMembership"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )
    classrooms: Mapped[list["Classroom"]] = relationship(
        back_populates="school"
    )


class SchoolMembership(Base):
    __tablename__ = "school_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "school_id", name="uq_school_membership"),
        CheckConstraint(
            "role IN ('owner', 'admin', 'teacher', 'student', 'parent')",
            name="ck_school_membership_role"
        ),
        Index("ix_school_memberships_school_id", "school_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="school_memberships")
    school: Mapped["School"] = relationship(back_populates="memberships")


class Classroom(Base):
    __tablename__ = "classrooms"
    __table_args__ = (
        UniqueConstraint("school_id", "code", name="uq_classroom_school_code"),
        Index("ix_classrooms_school_id", "school_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    school: Mapped["School"] = relationship(back_populates="classrooms")
    memberships: Mapped[list["ClassroomMembership"]] = relationship(
        back_populates="classroom", cascade="all, delete-orphan"
    )
    device_bindings: Mapped[list["DeviceBinding"]] = relationship(
        back_populates="classroom"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="classroom"
    )


class ClassroomMembership(Base):
    __tablename__ = "classroom_memberships"
    __table_args__ = (
        UniqueConstraint(
            "classroom_id", "user_id", name="uq_classroom_membership"
        ),
        CheckConstraint(
            "role IN ('teacher', 'student', 'parent')",
            name="ck_classroom_membership_role"
        ),
        Index("ix_classroom_memberships_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    classroom: Mapped["Classroom"] = relationship(
        back_populates="memberships"
    )
    user: Mapped["User"] = relationship(
        back_populates="classroom_memberships"
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    serial_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="display", server_default="display"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="inactive", server_default="inactive"
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

    bindings: Mapped[list["DeviceBinding"]] = relationship(
        back_populates="device"
    )
    deliveries: Mapped[list["MessageDelivery"]] = relationship(
        back_populates="device"
    )


class DeviceBinding(Base):
    __tablename__ = "device_bindings"
    __table_args__ = (
        CheckConstraint(
            "unbound_at IS NULL OR unbound_at >= bound_at",
            name="ck_device_binding_time"
        ),
        Index(
            "uq_device_one_active_binding",
            "device_id",
            unique=True,
            sqlite_where=text("unbound_at IS NULL"),
            postgresql_where=text("unbound_at IS NULL"),
        ),
        Index("ix_device_bindings_classroom_id", "classroom_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False
    )
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.id", ondelete="RESTRICT"), nullable=False
    )
    bound_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    bound_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    unbound_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    device: Mapped["Device"] = relationship(back_populates="bindings")
    classroom: Mapped["Classroom"] = relationship(
        back_populates="device_bindings"
    )
    bound_by: Mapped["User | None"] = relationship()


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_classroom_created", "classroom_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.id", ondelete="RESTRICT"), nullable=False
    )
    sender_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="text", server_default="text"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="queued", server_default="queued"
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    classroom: Mapped["Classroom"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship(back_populates="sent_messages")
    deliveries: Mapped[list["MessageDelivery"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class MessageDelivery(Base):
    __tablename__ = "message_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "message_id", "device_id", name="uq_message_device_delivery"
        ),
        Index("ix_message_deliveries_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", server_default="pending"
    )
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    message: Mapped["Message"] = relationship(back_populates="deliveries")
    device: Mapped["Device"] = relationship(back_populates="deliveries")
