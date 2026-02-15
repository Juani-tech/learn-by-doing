"""Initial migration - create learning paths tables.

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create learning_paths table
    op.create_table(
        'learning_paths',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(2000)),
        sa.Column('language', sa.String(100), index=True),
        sa.Column('area', sa.String(100), index=True),
        sa.Column('version', sa.String(50)),
        sa.Column('total_tasks', sa.Integer, default=0),
        sa.Column('estimated_hours', sa.Integer, default=0),
        sa.Column('difficulty_level', sa.String(20)),
        sa.Column('raw_data', sa.JSON, nullable=False),
        sa.Column('generation_metadata', sa.JSON, default=dict),
        sa.Column('quality_score', sa.Integer),
        sa.Column('generation_attempts', sa.Integer, default=1),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create phases table
    op.create_table(
        'phases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('path_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_paths.id', ondelete='CASCADE')),
        sa.Column('phase_id', sa.String(100), nullable=False),
        sa.Column('order_index', sa.Integer, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1000)),
        sa.Column('raw_data', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('path_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_paths.id', ondelete='CASCADE')),
        sa.Column('phase_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('phases.id', ondelete='CASCADE')),
        sa.Column('task_id', sa.String(100), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(2000)),
        sa.Column('difficulty', sa.Integer),
        sa.Column('estimated_hours', sa.Integer),
        sa.Column('requirements', sa.JSON, default=list),
        sa.Column('acceptance_criteria', sa.JSON, default=list),
        sa.Column('prerequisites', sa.JSON, default=list),
        sa.Column('resources', sa.JSON, default=list),
        sa.Column('raw_data', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create generation_jobs table
    op.create_table(
        'generation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('topic', sa.String(200), nullable=False),
        sa.Column('context', sa.String(1000)),
        sa.Column('experience_level', sa.String(20)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('path_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('learning_paths.id'), nullable=True),
        sa.Column('result_data', sa.JSON),
        sa.Column('error_message', sa.String(1000)),
        sa.Column('current_agent', sa.String(50)),
        sa.Column('iteration', sa.Integer, default=0),
        sa.Column('max_iterations', sa.Integer, default=5),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True))
    )
    
    # Create indexes
    op.create_index('idx_paths_language', 'learning_paths', ['language'])
    op.create_index('idx_paths_area', 'learning_paths', ['area'])
    op.create_index('idx_paths_status', 'learning_paths', ['status'])
    op.create_index('idx_phases_path_id', 'phases', ['path_id'])
    op.create_index('idx_tasks_path_id', 'tasks', ['path_id'])
    op.create_index('idx_tasks_phase_id', 'tasks', ['phase_id'])


def downgrade() -> None:
    op.drop_table('generation_jobs')
    op.drop_table('tasks')
    op.drop_table('phases')
    op.drop_table('learning_paths')
