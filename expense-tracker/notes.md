### Migrations
- DB migrations are version controlled scripts that manage incremental, reversible changes to a database schema(such as creating tables,adding cols, or dropping indexes).
- Instead of relying on `Base.metadata.create_all()` - which only creates tables if they dont exist and ccannot handle modifications like renaming or altering data types 
- migrations treat your db schema like code. they allow dev teams to sync tracct n safely rollback schema modifications across local, staging and prod envs

### ex : manual vs migrations
- users table with id n usrname, later u add is_active column
- manual approach :
```sql
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
```
  - problem : if another dev pulls code their local db won't have this col
  - unless they run sql statement again
  - n if smtg go wrong reversing it requires writing another SQL `DROP COLUMN` script from memory
  
- instead u write funtions : 
    + upgrade() - how to apply change
    + downgrade() how to undo it
- every env runs this script in order and a tracking rable in db records which migration versions have already been executed

## Alembic Workflow
- define ur db with **SQLAlchemy**, alembic bridges sqlalchemy models n actual db by autogenerating migration scripts for u
- workflow :
  - initialise alembic : `$ alembic init alembic` once in ur project
  - link models : point alembic's env.py to sqlalechemy Base model metadata so it knows what ur schema shud look like
  - modify model : 
    ```python
     class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        username = Column(String)
        is_active = Column(Boolean, default=True)  # <-- Added field
    ```
  - generate migration : `alembic revision --autogenerate -m "add is_active column"`
    - it compares ur current models againts current db n automatically writes script in py:
    - ```python
        def upgrade():
        op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))

        def downgrade():
            op.drop_column('users', 'is_active')
        ```
  -  review and apply : `alembic upgrade head`



--- 

### Few things to know : 
- after running alembic init alembic , creates
```plaintext
expense-tracker/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── app/
```
- alembic.ini : alembics config
- alembic/env.py : connects alembic to app n ORM metadata
- alembic/versions/: stores migrations scripts
