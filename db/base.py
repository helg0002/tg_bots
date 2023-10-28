from sqlalchemy.orm import as_declarative, relationship, mapped_column, Session, sessionmaker

@as_declarative()

class AbstractModel: pass
