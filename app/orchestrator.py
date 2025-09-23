"""
Living Cyber Security System Orchestrator

This is a minimal implementation to understand the build/test flow for creating
GitHub Copilot instructions. This implements the interface expected by the tests.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import psutil
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

# Enums
class ThreatLevel(Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    CRITICAL = "critical"

class ActionType(Enum):
    MONITOR = "monitor"
    ISOLATE = "isolate"
    BLOCK = "block"

# Data Models
@dataclass
class Evidence:
    source: str
    timestamp: datetime
    entity_id: str
    threat_level: ThreatLevel
    confidence: float
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['threat_level'] = self.threat_level.value
        return result

@dataclass
class Decision:
    decision_id: str
    timestamp: datetime
    entity_id: str
    action: ActionType
    confidence: float
    reasoning: str
    evidence_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['action'] = self.action.value
        return result

# Memory System
class MemorySystem:
    def __init__(self, max_size: int = 1000):
        self.memories: List[Dict[str, Any]] = []
        self.max_size = max_size
    
    def remember(self, evidence: Evidence, decision: Decision):
        memory_entry = {
            'evidence': evidence,
            'decision': decision,
            'timestamp': datetime.now(timezone.utc),
            'weight': 1.0
        }
        self.memories.append(memory_entry)
        if len(self.memories) > self.max_size:
            self.memories.pop(0)
    
    def decay_memories(self):
        for memory in self.memories:
            memory['weight'] *= 0.95  # Simple decay factor

# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def diagnose_problems(self) -> List[str]:
        problems = []
        health = self.monitor_health()
        if health['cpu_usage'] > 80:
            problems.append('high_cpu')
        if health['memory_usage'] > 90:
            problems.append('high_memory')
        return problems
    
    def self_heal(self, problems: List[str]) -> List[str]:
        healing_actions = []
        for problem in problems:
            if problem == 'high_cpu':
                healing_actions.append('reduce_processing_threads')
            elif problem == 'high_memory':
                healing_actions.append('clear_old_cache')
        return healing_actions

# Main System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = MemorySystem(config.get('memory_size', 1000))
        self.healing_system = HealingSystem()
        self.learning_rate = config.get('learning_rate', 0.1)
        self.evolution_interval = config.get('evolution_interval', 60)
    
    async def process_evidence(self, evidence: Evidence) -> Decision:
        # Simple decision logic for testing
        if evidence.threat_level == ThreatLevel.CRITICAL:
            action = ActionType.ISOLATE
            confidence = min(0.9, evidence.confidence + 0.1)
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS:
            action = ActionType.MONITOR
            confidence = evidence.confidence
        else:
            action = ActionType.MONITOR
            confidence = max(0.1, evidence.confidence - 0.1)
        
        decision = Decision(
            decision_id=f"dec_{evidence.entity_id}_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=confidence,
            reasoning=f"Processed {evidence.threat_level.value} threat",
            evidence_count=1
        )
        
        self.memory.remember(evidence, decision)
        return decision

# FastAPI Application
app = FastAPI(title="ARKAB Cyber Security System")

# Global system instance (for demonstration)
system_config = {"learning_rate": 0.1, "memory_size": 1000, "evolution_interval": 60}
cyber_system = LivingCyberSecuritySystem(system_config)

# Pydantic models for API
class EvidenceRequest(BaseModel):
    source: str
    timestamp: str
    entity_id: str
    threat_level: str
    confidence: float
    metrics: Dict[str, Any]

class EvidenceBatchRequest(BaseModel):
    evidences: List[EvidenceRequest]

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": cyber_system.healing_system.monitor_health()
    }

@app.get("/metrics")
async def get_metrics():
    return {
        "memory_count": len(cyber_system.memory.memories),
        "system_health": cyber_system.healing_system.monitor_health(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/evidence/batch")
async def process_evidence_batch(request: EvidenceBatchRequest):
    try:
        results = []
        for evidence_data in request.evidences:
            # Convert string timestamp to datetime
            timestamp = datetime.fromisoformat(evidence_data.timestamp.replace('Z', '+00:00'))
            
            # Convert string threat level to enum
            threat_level = ThreatLevel(evidence_data.threat_level)
            
            evidence = Evidence(
                source=evidence_data.source,
                timestamp=timestamp,
                entity_id=evidence_data.entity_id,
                threat_level=threat_level,
                confidence=evidence_data.confidence,
                metrics=evidence_data.metrics
            )
            
            decision = await cyber_system.process_evidence(evidence)
            results.append(decision.to_dict())
        
        return {"decisions": results, "status": "processed"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)