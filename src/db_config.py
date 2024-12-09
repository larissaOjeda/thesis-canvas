import logging
import os
import time
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from utils.constants import APP_NAME, DEFAULT_STATEMENT_TIMEOUT
from sqlalchemy import text
from dotenv import load_dotenv


log = logging.getLogger(__name__)


Base = declarative_base()
load_dotenv()

# Database Engine Factory
class DatabaseEngineFactory:
    _instance: Optional[create_engine] = None
    db_uri_env_var: str = None
    with_composites: bool = False
    default_statement_timeout: Optional[int] = DEFAULT_STATEMENT_TIMEOUT.total_seconds()

    @classmethod
    def get_db_uri(cls):
        db_uri = os.getenv("DATABASE_URL")
        if not db_uri:
            raise RuntimeError(f"No {cls.db_uri_env_var} defined")
        return db_uri

    @classmethod
    def get_application_name(cls, application_name):
        return {"application_name": APP_NAME or application_name}

    @classmethod
    def get_statement_timeout(cls, statement_timeout):
        stmt_timeout = statement_timeout or cls.default_statement_timeout
        if stmt_timeout is not None:
            return {"options": f"-c statement_timeout={int(stmt_timeout * 1000)}"}
        return {}

    @classmethod
    def get_search_path(cls): 
        return {"options": "-c search_path=canvas"}
    
    @classmethod
    def get_connection_args(cls, application_name, statement_timeout):
        return {
            **cls.get_application_name(application_name),
            **cls.get_statement_timeout(statement_timeout),
            **cls.get_search_path(),
        }

    @classmethod
    def create(cls, application_name, statement_timeout: Optional[int] = None) -> Engine:
        if not cls._instance:
            cls._create_engine(application_name, statement_timeout)
        return cls._instance

    @classmethod
    def _create_engine(cls, application_name, statement_timeout):
        cls._instance = create_engine(
            cls.get_db_uri(),
            pool_pre_ping=True,
            pool_size=4,
            max_overflow=28,
            connect_args=cls.get_connection_args(application_name, statement_timeout),
        )
        # if cls.with_composites:
        #     register_composites(cls._instance.connect())

    @classmethod
    def generate_session(
        cls, application_name=APP_NAME, statement_timeout: Optional[int] = DEFAULT_STATEMENT_TIMEOUT.total_seconds()
    ) -> Session:
        engine = cls.create(application_name=application_name, statement_timeout=statement_timeout)
        return sessionmaker(autocommit=False, expire_on_commit=False, autoflush=False, bind=engine)()


def clean_dirty_instances(db):
    dirty_instances = db.dirty
    while dirty_instances:
        if os.getenv("ENVIRONMENT", "local") == "local":
            instance = dirty_instances.pop()
            db.expunge(instance)

@contextmanager
def SessionManager(
    application_name=APP_NAME, statement_timeout: Optional[int] = DEFAULT_STATEMENT_TIMEOUT.total_seconds()
) -> Generator[Session, None, None]:  # noqa
    db = DatabaseEngineFactory.generate_session(application_name=application_name, statement_timeout=statement_timeout)
    try:
        clean_dirty_instances(db)
        start_time = time.time()
        yield db
        log.info(f"Session started at {start_time}")
    finally:
        db.close()