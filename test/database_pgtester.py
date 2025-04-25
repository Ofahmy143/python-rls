# from testing.postgresql import Postgresql  # type: ignore
# from engines import ADMIN_DATABASE_URL
from urllib.parse import urlparse

import sqlalchemy as sa
from pg_tester import SyncTestingPostgreSQL

from test import models

ADMIN_DATABASE_URL = "postgresql://user:password@localhost/session"


class TestPostgres:
    postgresql: SyncTestingPostgreSQL
    admin_engine: sa.engine.Engine
    non_superadmin_engine: sa.engine.Engine

    def __del__(self):
        self.admin_engine.dispose()
        self.non_superadmin_engine.dispose()
        self.postgresql.cleanup()


def test_postgres_instance() -> TestPostgres:
    """Returns a test postgres instance seeded with data."""
    inst = TestPostgres()
    print(f"postgres sync instance: {inst}")
    inst.postgresql = SyncTestingPostgreSQL(admin_conn_url=ADMIN_DATABASE_URL)
    updated_url = inst.postgresql.get_dsn().replace("postgresql", "postgresql+psycopg")
    print(f"Updated URL: {updated_url}")
    inst.admin_engine = sa.create_engine(updated_url)
    connection = inst.admin_engine.connect()
    models.Base.metadata.create_all(bind=inst.admin_engine)

    # Seed data
    user_values = []
    item_values = []
    for user_id in range(1, 3):
        user_values.append({"id": user_id, "username": f"user{user_id}"})
        for item_id in range(1, 3):
            item_values.append(
                {
                    "title": f"Item {item_id} for User {user_id}",
                    "description": f"Description of item {item_id} for User {user_id}",
                    "owner_id": user_id,
                }
            )
    with connection.begin():
        connection.execute(sa.insert(models.User).values(user_values))
        connection.execute(sa.insert(models.Item).values(item_values))
    # Use a non-superadmin user for the test connection
    non_superadmin_user = "test_user"
    password = "test_password"
    parsed_dsn = urlparse(inst.postgresql.get_dsn())
    database = parsed_dsn.path.lstrip("/")
    host = parsed_dsn.hostname
    port = parsed_dsn.port

    with connection.begin():
        connection.execute(
            sa.text(f"""
            CREATE USER {non_superadmin_user} WITH PASSWORD '{password}';
            GRANT CONNECT ON DATABASE {database} TO {non_superadmin_user};
            GRANT USAGE ON SCHEMA public TO {non_superadmin_user};
            ALTER ROLE {non_superadmin_user} WITH LOGIN;
            GRANT SELECT ON ALL TABLES IN SCHEMA public TO {non_superadmin_user};
                                    """)
        )
    connection.close()

    # Create the engine with the non-superadmin user's credentials
    inst.non_superadmin_engine = sa.create_engine(
        f"postgresql+psycopg://{non_superadmin_user}:{password}@{host}:{port}/{database}"
    )
    return inst


if __name__ == "__main__":
    instance = test_postgres_instance()
    print(instance)

    del instance
