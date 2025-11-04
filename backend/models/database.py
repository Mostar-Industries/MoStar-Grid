from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

class AgentStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    TRAINING = "training"
    ERROR = "error"

class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    status = Column(Enum(AgentStatus))
    capabilities = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tasks = relationship("Task", back_populates="agent")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    type = Column(String)
    status = Column(String)
    parameters = Column(JSON)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    agent = relationship("Agent", back_populates="tasks")
    metrics = relationship("Metric", back_populates="task")

class Metric(Base):
    __tablename__ = 'metrics'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    name = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    task = relationship("Task", back_populates="metrics")

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    type = Column(String)
    data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
