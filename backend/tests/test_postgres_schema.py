from sqlalchemy import inspect, text


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


def test_connected_to_test_database(test_engine):
    with test_engine.connect() as connection:
        database = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

    assert database == "campusrelay_test"


def test_all_expected_tables_exist(test_engine):
    inspector = inspect(test_engine)

    actual_tables = set(inspector.get_table_names())

    assert EXPECTED_TABLES.issubset(actual_tables)


def test_all_tables_have_primary_keys(test_engine):
    inspector = inspect(test_engine)

    for table_name in EXPECTED_TABLES:
        primary_key = inspector.get_pk_constraint(table_name)

        assert primary_key["constrained_columns"], (
            f"{table_name} 缺少主键"
        )


def test_unique_constraints_exist(test_engine):
    inspector = inspect(test_engine)

    expected = {
        "users": {"email"},
        "schools": {"code"},
        "devices": {"serial_number"},
        "school_memberships": {"user_id", "school_id"},
        "classrooms": {"school_id", "code"},
        "classroom_memberships": {"classroom_id", "user_id"},
        "message_deliveries": {"message_id", "device_id"},
    }

    for table_name, expected_columns in expected.items():
        constraints = inspector.get_unique_constraints(table_name)

        unique_column_sets = {
            frozenset(item["column_names"])
            for item in constraints
        }

        assert frozenset(expected_columns) in unique_column_sets, (
            f"{table_name} 缺少唯一约束：{expected_columns}"
        )


def test_device_active_binding_partial_index_exists(test_engine):
    inspector = inspect(test_engine)

    indexes = inspector.get_indexes("device_bindings")

    matching_indexes = [
        index
        for index in indexes
        if index["name"] == "uq_device_one_active_binding"
    ]

    assert len(matching_indexes) == 1

    index = matching_indexes[0]

    assert index["unique"] is True
    assert index["column_names"] == ["device_id"]
    assert index["dialect_options"].get(
        "postgresql_where"
    ) is not None


def test_foreign_keys_exist(test_engine):
    inspector = inspect(test_engine)

    expected = {
        "school_memberships": {"users", "schools"},
        "classrooms": {"schools"},
        "classroom_memberships": {"users", "classrooms"},
        "device_bindings": {"devices", "classrooms", "users"},
        "messages": {"classrooms", "users"},
        "message_deliveries": {"messages", "devices"},
    }

    for table_name, expected_references in expected.items():
        foreign_keys = inspector.get_foreign_keys(table_name)

        actual_references = {
            item["referred_table"]
            for item in foreign_keys
        }

        assert expected_references.issubset(actual_references), (
            f"{table_name} 外键不完整"
        )


def test_role_check_constraints_exist(test_engine):
    inspector = inspect(test_engine)

    school_constraints = inspector.get_check_constraints(
        "school_memberships"
    )

    classroom_constraints = inspector.get_check_constraints(
        "classroom_memberships"
    )

    assert any(
        "owner" in str(item["sqltext"])
        and "admin" in str(item["sqltext"])
        and "teacher" in str(item["sqltext"])
        and "student" in str(item["sqltext"])
        and "parent" in str(item["sqltext"])
        for item in school_constraints
    )

    assert any(
        "teacher" in str(item["sqltext"])
        and "student" in str(item["sqltext"])
        and "parent" in str(item["sqltext"])
        for item in classroom_constraints
    )


def test_message_delivery_unique_constraint_exists(test_engine):
    inspector = inspect(test_engine)

    constraints = inspector.get_unique_constraints(
        "message_deliveries"
    )

    assert any(
        set(item["column_names"]) == {"message_id", "device_id"}
        for item in constraints
    )
