from typing import Type

from sqlalchemy import event, text
from sqlalchemy.ext.declarative import DeclarativeMeta

from .create_policies import create_policies


def set_metadata_info(Base: Type[DeclarativeMeta]):
    """RLS policies are first added to the Metadata before applied."""
    Base.metadata.info.setdefault("rls_policies", dict())
    for mapper in Base.registry.mappers:
        if not hasattr(mapper.class_, "__rls_policies__"):
            continue

        Base.metadata.info["rls_policies"][
            mapper.tables[0].fullname
        ] = mapper.class_.__rls_policies__




def register_rls(Base: Type[DeclarativeMeta]):

    # required for `alembic revision --autogenerate``
    set_metadata_info(Base)

    @event.listens_for(Base.metadata, "after_create")
    def receive_after_create(target, connection, tables, **kw):

        # required for `Base.metadata.create_all()`
        set_metadata_info(Base)
        create_policies(Base, connection)
