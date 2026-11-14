import os
from pathlib import Path

import pytest

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.database import Base, database_url
from app import models  # noqa: F401


@pytest.fixture(scope="session")
def test_engine():
    test_url = make_url(database_url).set(
        database="campusrelay_test"
    )

    if test_url.database != "campusrelay_test":
        raise RuntimeError("测试数据库名称错误，拒绝执行")

    engine = create_engine(
        test_url,
        pool_pre_ping=True,
    )

    if engine.url.database != "campusrelay_test":
        engine.dispose()
        raise RuntimeError("测试数据库安全检查失败")

    # 清理之前使用 create_all 创建的旧测试表
    Base.metadata.drop_all(engine)

    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS alembic_version")
        )

    config_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    alembic_config = Config(str(config_path))

    previous_database_url = os.environ.get("DATABASE_URL")

    try:
        # 只将 Alembic 的连接指向专用测试数据库
        os.environ["DATABASE_URL"] = test_url.render_as_string(
            hide_password=False
        )

        # 使用正式迁移文件创建数据库结构
        command.upgrade(alembic_config, "head")

        yield engine

    finally:
        engine.dispose()

        # 迁移回退也只针对 campusrelay_test
        command.downgrade(alembic_config, "base")

        cleanup_engine = create_engine(test_url)

        try:
            with cleanup_engine.begin() as connection:
                connection.execute(
                    text("DROP TABLE IF EXISTS alembic_version")
                )
        finally:
            cleanup_engine.dispose()

        if previous_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_database_url


@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
