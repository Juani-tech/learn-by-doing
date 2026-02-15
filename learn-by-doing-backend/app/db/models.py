"""Database models."""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Integer, DateTime, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class LearningPath(Base):
    """Learning path model."""
    __tablename__ = "learning_paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000))
    language = Column(String(100), index=True)
    area = Column(String(100), index=True)
    version = Column(String(50))
    
    # Statistics
    total_tasks = Column(Integer, default=0)
    estimated_hours = Column(Integer, default=0)
    difficulty_level = Column(String(20))
    
    # Full data
    raw_data = Column(JSON, nullable=False)
    
    # Generation metadata
    generation_metadata = Column(JSON, default=dict)
    quality_score = Column(Integer)  # 0-100
    generation_attempts = Column(Integer, default=1)
    
    # Status
    status = Column(String(20), default="active")  # active, archived, draft
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    phases = relationship("Phase", back_populates="path", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="path", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningPath(id={self.id}, title={self.title})>"


class Phase(Base):
    """Phase model."""
    __tablename__ = "phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"))
    phase_id = Column(String(100), nullable=False)  # Original ID from JSON
    order_index = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    
    # Raw data
    raw_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    path = relationship("LearningPath", back_populates="phases")
    tasks = relationship("Task", back_populates="phase", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Phase(id={self.id}, title={self.title})>"


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"))
    phase_id = Column(UUID(as_uuid=True), ForeignKey("phases.id", ondelete="CASCADE"))
    task_id = Column(String(100), nullable=False)  # Original ID from JSON
    
    # Content
    title = Column(String(200), nullable=False)
    description = Column(String(2000))
    difficulty = Column(Integer)  # 1-5
    estimated_hours = Column(Integer)
    
    # Structured data
    requirements = Column(JSON, default=list)
    acceptance_criteria = Column(JSON, default=list)
    prerequisites = Column(JSON, default=list)
    resources = Column(JSON, default=list)
    
    # Raw data
    raw_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    path = relationship("LearningPath", back_populates="tasks")
    phase = relationship("Phase", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title})>"


class GenerationJob(Base):
    """Track generation jobs."""
    __tablename__ = "generation_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    topic = Column(String(200), nullable=False)
    context = Column(String(1000))
    experience_level = Column(String(20))
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # Results
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=True)
    result_data = Column(JSON)
    error_message = Column(String(1000))
    
    # Progress
    current_agent = Column(String(50))
    iteration = Column(Integer, default=0)
    max_iterations = Column(Integer, default=5)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<GenerationJob(id={self.id}, topic={self.topic}, status={self.status})>"
