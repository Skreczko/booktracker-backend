from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os, sys
from dotenv import load_dotenv

from settings import get_config

# -------------------------------    IMPORTANT    -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

# used to setup DATABASE_URL from variable
from db.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# this will overwrite the ini-file sqlalchemy.url path
# with the path given in the config of the main code
config.set_main_option("sqlalchemy.url",  get_config().sync_database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

#!!!!!!!!!!!!!!!!!!!       IMPORT ALL YOUR MODELS HERE           !!!!!!!!!!!!!!!!!!
import migrations.import_models
# _________________________________________________________________________________

target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    postgis_tables = (
        "spatial_ref_sys", "geometry_columns", "geography_columns", "pagc_lex",
        "raster_columns", "raster_overviews",
        "zip_state", "zip_state_loc", "direction_lookup", "state_lookup",
        "zip_lookup_all", "edges", "secondary_unit_lookup", "geocode_settings",
        "countysub_lookup", "tabblock", "place_lookup", "addr",
        "county_lookup", "tabblock20", "cousub", "place", "zip_lookup",
        "pagc_gaz", "state", "loader_variables", "tract", "pagc_rules",
        "featnames", "addrfeat", "bg", "street_type_lookup", "county",
        "loader_platform", "geocode_settings_default", "faces",
        "zcta5", "loader_lookuptables", "zip_lookup_base"
    )
    if type_ == "table" and (name in postgis_tables or 'postgis' in name):
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,  # Dodaj tę linię
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
