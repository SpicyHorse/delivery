"""game url, bt infohash

Revision ID: 173de5bbe259
Revises: 141348f489f
Create Date: 2013-01-31 00:38:32.200448

"""

# revision identifiers, used by Alembic.
revision = '173de5bbe259'
down_revision = '141348f489f'

from alembic import op
import database as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Game', sa.Column('url', sa.String(length=512), nullable=True))
    op.add_column('GameBuild', sa.Column('state', sa.Enum('INIT', 'READY'), nullable=False))
    op.add_column('GameBuild', sa.Column('infohash', sa.String(length=40), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('GameBuild', 'infohash')
    op.drop_column('GameBuild', 'state')
    op.drop_column('Game', 'url')
    ### end Alembic commands ###
