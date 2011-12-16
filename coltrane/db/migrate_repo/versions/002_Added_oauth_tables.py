from sqlalchemy import *
from migrate import *

meta = MetaData()

users = Table('users', meta,
            Column('id', Integer(), primary_key=True, nullable=False),
        )
users2 = Table('users', meta,
            Column('id', Integer(), primary_key=True, nullable=False),
        )
compute_nodes = Table('compute_nodes', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime(timezone=False)),
        Column('deleted', Boolean(create_constraint=True, name=None)),
        Column('id', Integer(), primary_key=True, nullable=False),
        Column('service_id', Integer(), nullable=False),

        Column('vcpus', Integer(), nullable=False),
        Column('memory_mb', Integer(), nullable=False),
        Column('local_gb', Integer(), nullable=False),
        Column('vcpus_used', Integer(), nullable=False),
        Column('memory_mb_used', Integer(), nullable=False),
        Column('local_gb_used', Integer(), nullable=False),
        Column('hypervisor_type',
               Text(convert_unicode=False, assert_unicode=None,
               unicode_error=None, _warn_on_bytestring=False),
               nullable=False),
        Column('hypervisor_version', Integer(), nullable=False),
        Column('cpu_info',
               Text(convert_unicode=False, assert_unicode=None,
                    unicode_error=None, _warn_on_bytestring=False),
               nullable=False),
        )

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pass


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pass
