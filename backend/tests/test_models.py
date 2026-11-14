from sqlalchemy.orm import configure_mappers

from app.database import Base
from app import models


EXPECTED_TABLES = {
    "users",
    "schools",
    "school_memberships",
    "classrooms",
    "classroom_memberships",
    "devices",
    "device_bindings",
    "messages",
    "message_deliveries",
}


def test_all_models_are_registered():
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLES


def test_all_tables_have_primary_keys():
    for table in Base.metadata.tables.values():
        assert len(table.primary_key.columns) > 0, table.name


def test_unique_constraints():
    expected = {
        "users": {("email",)},
        "schools": {("code",)},
        "devices": {("serial_number",)},
        "school_memberships": {("user_id", "school_id")},
        "classrooms": {("school_id", "code")},
        "classroom_memberships": {("classroom_id", "user_id")},
        "message_deliveries": {("message_id", "device_id")},
    }

    for table_name, expected_constraints in expected.items():
        table = Base.metadata.tables[table_name]

        actual_constraints = {
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if constraint.__class__.__name__ == "UniqueConstraint"
        }

        assert expected_constraints.issubset(actual_constraints), table_name


def test_foreign_keys_have_delete_rules():
    expected = {
        "school_memberships": {
            ("user_id", "users.id", "CASCADE"),
            ("school_id", "schools.id", "CASCADE"),
        },
        "classrooms": {
            ("school_id", "schools.id", "RESTRICT"),
        },
        "classroom_memberships": {
            ("classroom_id", "classrooms.id", "CASCADE"),
            ("user_id", "users.id", "CASCADE"),
        },
        "device_bindings": {
            ("device_id", "devices.id", "RESTRICT"),
            ("classroom_id", "classrooms.id", "RESTRICT"),
            ("bound_by_user_id", "users.id", "SET NULL"),
        },
        "messages": {
            ("classroom_id", "classrooms.id", "RESTRICT"),
            ("sender_user_id", "users.id", "RESTRICT"),
        },
        "message_deliveries": {
            ("message_id", "messages.id", "CASCADE"),
            ("device_id", "devices.id", "RESTRICT"),
        },
    }

    for table_name, expected_keys in expected.items():
        table = Base.metadata.tables[table_name]

        actual_keys = {
            (
                foreign_key.parent.name,
                foreign_key.target_fullname,
                foreign_key.ondelete,
            )
            for foreign_key in table.foreign_keys
        }

        assert expected_keys.issubset(actual_keys), table_name


def test_membership_role_constraints():
    school_table = Base.metadata.tables["school_memberships"]
    classroom_table = Base.metadata.tables["classroom_memberships"]

    school_checks = {
        constraint.name
        for constraint in school_table.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }

    classroom_checks = {
        constraint.name
        for constraint in classroom_table.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }

    assert "ck_school_membership_role" in school_checks
    assert "ck_classroom_membership_role" in classroom_checks


def test_device_binding_constraints_and_partial_index():
    table = Base.metadata.tables["device_bindings"]

    check_names = {
        constraint.name
        for constraint in table.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }

    assert "ck_device_binding_time" in check_names

    index = next(
        index
        for index in table.indexes
        if index.name == "uq_device_one_active_binding"
    )

    assert index.unique is True
    assert str(index.dialect_options["postgresql"]["where"]) == (
        "unbound_at IS NULL"
    )


def test_expected_indexes_exist():
    expected = {
        "school_memberships": {"ix_school_memberships_school_id"},
        "classrooms": {"ix_classrooms_school_id"},
        "classroom_memberships": {"ix_classroom_memberships_user_id"},
        "device_bindings": {"ix_device_bindings_classroom_id"},
        "messages": {"ix_messages_classroom_created"},
        "message_deliveries": {"ix_message_deliveries_status"},
    }

    for table_name, expected_indexes in expected.items():
        table = Base.metadata.tables[table_name]
        actual_indexes = {
            index.name for index in table.indexes
        }

        assert expected_indexes.issubset(actual_indexes), table_name


def test_all_model_relationships_are_configured():
    configure_mappers()
