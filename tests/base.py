import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from src.db.tables.base import BaseSQLModel
from src.settings import settings

engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_admin_engine():
    url = make_url(settings.database_url).set(database="postgres")
    return create_engine(url, isolation_level="AUTOCOMMIT")


class BaseTestCase(unittest.TestCase):
    """Base class for setting up the test database and a shared session."""

    @classmethod
    def setUpClass(cls):
        cls.create_test_database()
        BaseSQLModel.metadata.drop_all(bind=engine)
        BaseSQLModel.metadata.create_all(bind=engine)
        cls.connection = engine.connect()
        cls.transaction = cls.connection.begin()
        cls.session = TestingSessionLocal(bind=cls.connection)

    @classmethod
    def create_test_database(cls):
        """Create the test database if it doesn't exist."""
        db_name = settings.database_url.split("/")[-1]
        admin_engine = get_admin_engine()
        with admin_engine.connect() as connection:
            exists_query = "SELECT 1 FROM pg_database WHERE datname = :db_name"
            db_exists = connection.execute(
                text(exists_query), {"db_name": db_name}
            ).scalar()
            if not db_exists:
                connection.execute(text(f'CREATE DATABASE "{db_name}"'))
        admin_engine.dispose()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class."""
        cls.session.close()
        if cls.transaction.is_active:
            cls.transaction.rollback()
        cls.connection.close()

    def setUp(self):
        """Reuse the shared session for the current test."""
        self.session = self.__class__.session

    def tearDown(self):
        """Clear all data from tables and reset the session."""
        for table in reversed(BaseSQLModel.metadata.sorted_tables):
            self.session.execute(table.delete())
        self.session.commit()
        self.session.expire_all()
