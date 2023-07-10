"""added payments table

Revision ID: 140fba539419
Revises: 
Create Date: 2023-07-06 02:49:41.414055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '140fba539419'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rides',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('driver_id', sa.String(length=36), nullable=True),
    sa.Column('destination', sa.String(length=200), nullable=False),
    sa.Column('pickup_location', sa.String(length=200), nullable=False),
    sa.Column('fare', sa.Float(), server_default='0.0', nullable=True),
    sa.Column('status', sa.Enum('completed', 'in_transit', 'canceled', 'confirmed', 'arrived', name='ride_status'), nullable=False),
    sa.Column('paid', sa.Boolean(), server_default=sa.text('0'), nullable=True),
    sa.Column('date', sa.TIMESTAMP(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('date', sa.TIMESTAMP(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('ride_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ride_id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_table('rides')
    # ### end Alembic commands ###
