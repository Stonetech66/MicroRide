"""added drivers table

Revision ID: 406cbebc5895
Revises: 
Create Date: 2023-07-06 02:46:44.924949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '406cbebc5895'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('drivers',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('profile_pic', sa.String(length=40), nullable=True),
    sa.Column('bio', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('date', sa.TIMESTAMP(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('rides',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('driver_id', sa.String(length=36), nullable=True),
    sa.Column('destination', sa.String(length=200), nullable=False),
    sa.Column('pickup_location', sa.String(length=200), nullable=False),
    sa.Column('fare', sa.Float(), server_default='0.0', nullable=True),
    sa.Column('status', sa.Enum('completed', 'in_transit', 'canceled', 'confirmed', 'arrived', name='ride_status'), nullable=False),
    sa.Column('paid', sa.Boolean(), server_default='false', nullable=True),
    sa.Column('date', sa.TIMESTAMP(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rides')
    op.drop_table('drivers')
    # ### end Alembic commands ###
