from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class DatasetType(Enum):
    SYNTHETIC = "synthetic"
    REAL = "real"
    HYBRID = "hybrid"

class TrainingStatus(Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TrainingPipeline(BaseModel):
    pipeline_id: str
    name: str
    description: Optional[str]
    dataset_type: DatasetType
    model_type: str
    status: TrainingStatus
    created_at: datetime
    updated_at: datetime
    config: Dict
    metrics: Dict = {}

class TrainingMetrics(BaseModel):
    accuracy: float
    loss: float
    epoch: int
    timestamp: datetime
    custom_metrics: Dict = {}
