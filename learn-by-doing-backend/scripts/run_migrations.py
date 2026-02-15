#!/usr/bin/env python3
"""Run database migrations."""
import sys
sys.path.insert(0, '/app')

from alembic.config import Config
from alembic import command

# Create Alembic config
alembic_cfg = Config('/app/alembic.ini')

# Run migrations
command.upgrade(alembic_cfg, 'head')
print("Migrations complete!")
