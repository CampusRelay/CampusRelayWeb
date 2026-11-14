import pytest

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


def create_user(db, email="delete-test@example.com"):
    return db.execute(
        text("""
            INSERT INTO users (email, password_hash, display_name)
            VALUES (:email, 'hash', 'Delete Test')
            RETURNING id
        """),
        {"email": email},
    ).scalar_one()


def create_school(db, code="DELETE-SCHOOL"):
    return db.execute(
        text("""
            INSERT INTO schools (name, code)
            VALUES ('Delete School', :code)
            RETURNING id
        """),
        {"code": code},
    ).scalar_one()


def create_classroom(db, school_id):
    return db.execute(
        text("""
            INSERT INTO classrooms (school_id, name, code)
            VALUES (:school_id, 'Delete Class', 'DELETE-CLASS')
            RETURNING id
        """),
        {"school_id": school_id},
    ).scalar_one()


def create_device(db):
    return db.execute(
        text("""
            INSERT INTO devices (serial_number, name)
            VALUES ('DELETE-DEVICE', 'Delete Device')
            RETURNING id
        """)
    ).scalar_one()


def create_message(db, classroom_id, user_id):
    return db.execute(
        text("""
            INSERT INTO messages (classroom_id, sender_user_id, content)
            VALUES (:classroom_id, :user_id, 'Delete Test')
            RETURNING id
        """),
        {"classroom_id": classroom_id, "user_id": user_id},
    ).scalar_one()


def test_school_deletion_cascades_memberships(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)

    db_session.execute(
        text("""
            INSERT INTO school_memberships (user_id, school_id, role)
            VALUES (:user_id, :school_id, 'student')
        """),
        {"user_id": user_id, "school_id": school_id},
    )

    db_session.execute(
        text("DELETE FROM schools WHERE id = :id"),
        {"id": school_id},
    )

    count = db_session.execute(
        text("""
            SELECT COUNT(*) FROM school_memberships
            WHERE school_id = :id
        """),
        {"id": school_id},
    ).scalar_one()

    assert count == 0


def test_classroom_deletion_cascades_memberships(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)

    db_session.execute(
        text("""
            INSERT INTO classroom_memberships (
                classroom_id, user_id, role
            )
            VALUES (:classroom_id, :user_id, 'student')
        """),
        {"classroom_id": classroom_id, "user_id": user_id},
    )

    db_session.execute(
        text("DELETE FROM classrooms WHERE id = :id"),
        {"id": classroom_id},
    )

    count = db_session.execute(
        text("""
            SELECT COUNT(*) FROM classroom_memberships
            WHERE classroom_id = :id
        """),
        {"id": classroom_id},
    ).scalar_one()

    assert count == 0


def test_message_deletion_cascades_deliveries(db_session):
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
        {"message_id": message_id, "device_id": device_id},
    )

    db_session.execute(
        text("DELETE FROM messages WHERE id = :id"),
        {"id": message_id},
    )

    count = db_session.execute(
        text("""
            SELECT COUNT(*) FROM message_deliveries
            WHERE message_id = :id
        """),
        {"id": message_id},
    ).scalar_one()

    assert count == 0


def test_deleting_binding_user_sets_foreign_key_null(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)
    device_id = create_device(db_session)

    binding_id = db_session.execute(
        text("""
            INSERT INTO device_bindings (
                device_id, classroom_id, bound_by_user_id
            )
            VALUES (:device_id, :classroom_id, :user_id)
            RETURNING id
        """),
        {
            "device_id": device_id,
            "classroom_id": classroom_id,
            "user_id": user_id,
        },
    ).scalar_one()

    db_session.execute(
        text("DELETE FROM users WHERE id = :id"),
        {"id": user_id},
    )

    bound_by = db_session.execute(
        text("""
            SELECT bound_by_user_id
            FROM device_bindings
            WHERE id = :id
        """),
        {"id": binding_id},
    ).scalar_one()

    assert bound_by is None


def test_school_deletion_restricted_by_classroom(db_session):
    school_id = create_school(db_session)
    create_classroom(db_session, school_id)

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("DELETE FROM schools WHERE id = :id"),
            {"id": school_id},
        )


def test_classroom_deletion_restricted_by_device_binding(db_session):
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)
    device_id = create_device(db_session)

    db_session.execute(
        text("""
            INSERT INTO device_bindings (device_id, classroom_id)
            VALUES (:device_id, :classroom_id)
        """),
        {"device_id": device_id, "classroom_id": classroom_id},
    )

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("DELETE FROM classrooms WHERE id = :id"),
            {"id": classroom_id},
        )


def test_device_deletion_restricted_by_binding(db_session):
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)
    device_id = create_device(db_session)

    db_session.execute(
        text("""
            INSERT INTO device_bindings (device_id, classroom_id)
            VALUES (:device_id, :classroom_id)
        """),
        {"device_id": device_id, "classroom_id": classroom_id},
    )

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("DELETE FROM devices WHERE id = :id"),
            {"id": device_id},
        )


def test_user_deletion_restricted_by_sent_message(db_session):
    user_id = create_user(db_session)
    school_id = create_school(db_session)
    classroom_id = create_classroom(db_session, school_id)
    create_message(db_session, classroom_id, user_id)

    with pytest.raises(IntegrityError):
        db_session.execute(
            text("DELETE FROM users WHERE id = :id"),
            {"id": user_id},
        )
