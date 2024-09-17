from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from rls.schemas import Permissive
from rls.register_rls import register_rls
Base = declarative_base()

# Register RLS policies
register_rls(Base)

    
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User")

    __rls_policies__ = [
            Permissive(expr=f"owner_id = current_setting('app.current_user_id')::integer", cmd=["SELECT","INSERT", "UPDATE", "DELETE"])
]
