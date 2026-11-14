from sqlalchemy import inspect, text
from app.database import engine

inspector = inspect(engine)

with engine.connect() as conn:
    print("\n===== 1. 数据库信息 =====")
    print("Database:", conn.execute(text("SELECT current_database()")).scalar())
    print("User:", conn.execute(text("SELECT current_user")).scalar())

    print("\n===== 2. 数据表 =====")
    tables = inspector.get_table_names()

    for table in sorted(tables):
        print("  ", table)

    print("业务表数量:", len([t for t in tables if t != "alembic_version"]))

    print("\n===== 3. Alembic 版本 =====")
    print(conn.execute(text(
        "SELECT version_num FROM alembic_version"
    )).scalar())

    print("\n===== 4. 外键 =====")
    for table in sorted(tables):
        if table == "alembic_version":
            continue
        for fk in inspector.get_foreign_keys(table):
            print(table, "->", fk["referred_table"])

    print("\n===== 5. 索引 =====")
    for table in sorted(tables):
        if table == "alembic_version":
            continue
        for index in inspector.get_indexes(table):
            print(table, index["name"], "unique:", index["unique"])

    print("\n===== 6. 部分唯一索引 =====")
    result = conn.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'device_bindings'
          AND indexname = 'uq_device_one_active_binding'
    """))

    for row in result:
        print(row.indexname)
        print(row.indexdef)

    print("\n===== 7. 数据库连接 =====")
    print("OK")
