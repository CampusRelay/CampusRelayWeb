import pytest

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def create_user(db: Session, email="test@example.com"):
    return db.execute(
        text("""
            INSERT INTO users (email, password_hash, display_name)
            VALUES (:email, 'test_hash', 'Test User')
            RETURNING id
        """),
        {"email": email},
    ).scalar_one()


def create_school(db: Session, code="TEST-SCHOOL"):
    return db.execute(
        text("""
            INSERT INTO schools (name, code)
            VALUES ('Test School', :code)
            RETURNING id
        """),
        {"code": code},
    ).scalar_one()


def create_classroom(db: Session, school_id, code="CLASS-01"):
    return db.execute(
        text("""
            INSERT INTO classrooms (school_id, name, code)
            VALUES (:school_id, 'Test Classroom', :code)
            RETURNING id
        """),
        {"school_id": school_id, "code": code},
    ).scalar_one()


def create_device(db: Session, serial="TEST-DEVICE-001"):
    return db.execute(
        text("""
            INSERT INTO devices (serial_number, name)
            VALUES (:serial, 'Test Device')
            RETURNING id
        """),
        {"serial": serial},
    ).scalar_one()


def create_message(db: Session, classroom_id, sender_id):
    return db.execute(
        text("""
            INSERT INTO messages (
                classroom_id, sender_user_id, content
            )
            VALUES (:classroom_id, :sender_id, 'Test message')
            RETURNING id
        """),
        {
            "classroom_id": classroom_id,
            "sender_id": sender_id,
        },
    ).scalar_one()


def test_duplicate_user_email_rejected(db_session):
    create_user(db_session)

    with pytest.raises(IntegrityError):
        create_user(db_session)


def test_duplicate_school_code_rejected(db_session):
    create_school(db_session)

    with pytest.raises(IntegrityError):
        create_school(db_session)


def test_invalid_school_membership_role_rejected(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("""
                INSERT INTO school_memberships (
                    user_id, school_id, role
                )
                VALUES (:user_id, :school_id, 'superadmin')
            """),
            {
                "user_id": user_id,
                "school_id": school_id,
            },
        )


def test_invalid_classroom_membership_role_rejected(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("""
                INSERT INTO classroom_memberships (
                    classroom_id, user_id, role
                )
                VALUES (:classroom_id, :user_id, 'owner')
            """),
            {
                "classroom_id": classroom_id,
                "user_id": user_id,
            },
        )


def test_nonexistent_foreign_key_rejected(db_session):
    with pytest.raises(IntegrityError):
        db_session.execute(
            text("""
                INSERT INTO school_memberships (
                    user_id, school_id, role
                )
                VALUES (999999999, 999999999, 'student')
            """)
        )


def test_device_cannot_have_two_active_bindings(db_session):
    school_id = create_school(db_session)
    classroom_a = create_classroom(
        db_session, school_id, "CLASS-A"
    )
    classroom_b = create_classroom(
        db_session, school_id, "CLASS-B"
    )
    device_id = create_device(db_session)

    db_session.execute(
        text("""
            INSERT INTO device_bindings (device_id, classroom_id)
            VALUES (:device_id, :classroom_id)
        """),
        {
            "device_id": device_id,
            "classroom_id": classroom_a,
        },
    )

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("""
                INSERT INTO device_bindings (device_id, classroom_id)
                VALUES (:device_id, :classroom_id)
            """),
            {
                "device_id": device_id,
                "classroom_id": classroom_b,
            },
        )


def test_device_can_have_historical_and_active_bindings(db_session):
    school_id = create_school(db_session)
    classroom_a = create_classroom(
        db_session, school_id, "CLASS-A"
    )
    classroom_b = create_classroom(
        db_session, school_id, "CLASS-B"
    )
    device_id = create_device(db_session)

    db_session.execute(
        text("""
            INSERT INTO device_bindings (
                device_id,
                classroom_id,
                bound_at,
                unbound_at
            )
            VALUES (
                :device_id,
                :classroom_id,
                CURRENT_TIMESTAMP - INTERVAL '2 hours',
                CURRENT_TIMESTAMP - INTERVAL '1 hour'
            )
        """),
        {
            "device_id": device_id,
            "classroom_id": classroom_a,
        },
    )

    db_session.execute(
        text("""
            INSERT INTO device_bindings (device_id, classroom_id)
            VALUES (:device_id, :classroom_id)
        """),
        {
            "device_id": device_id,
            "classroom_id": classroom_b,
        },
    )

    count = db_session.execute(
        text("""
            SELECT COUNT(*)
            FROM device_bindings
            WHERE device_id = :device_id
        """),
        {"device_id": device_id},
    ).scalar_one()

    assert count == 2


def test_invalid_device_binding_time_rejected(db_session):
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)
    device_id = create_device(db_session)

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("""
                INSERT INTO device_bindings (
                    device_id,
                    classroom_id,
                    bound_at,
                    unbound_at
                )
                VALUES (
                    :device_id,
                    :classroom_id,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP - INTERVAL '1 hour'
                )
            """),
            {
                "device_id": device_id,
                "classroom_id": classroom_id,
            },
        )


def test_duplicate_message_delivery_rejected(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)
    device_id = create_device(db_session)
    message_id = create_message(
        db_session, classroom_id, user_id
    )

    db_session.execute(
        text("""
            INSERT INTO message_deliveries (message_id, device_id)
            VALUES (:message_id, :device_id)
        """),
        {
            "message_id": message_id,
            "device_id": device_id,
        },
    )

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("""
                INSERT INTO message_deliveries (message_id, device_id)
                VALUES (:message_id, :device_id)
            """),
            {
                "message_id": message_id,
                "device_id": device_id,
            },
        )


def test_database_server_defaults(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)
    device_id = create_device(db_session)
    message_id = create_message(
        db_session, classroom_id, user_id
    )

    delivery = db_session.execute(
        text("""
            INSERT INTO message_deliveries (message_id, device_id)
            VALUES (:message_id, :device_id)
            RETURNING status, attempts, created_at
        """),
        {
            "message_id": message_id,
            "device_id": device_id,
        },
    ).mappings().one()

    assert delivery["status"] == "pending"
    assert delivery["attempts"] == 0
    assert delivery["created_at"] is not None
