"""
Orchestrator module for the Living Cybersecurity System.
Contains the main classes and FastAPI application.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Enums
class ThreatLevel(Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    CRITICAL = "critical"


class ActionType(Enum):
    MONITOR = "monitor"
    BLOCK = "block"
    QUARANTINE = "quarantine"


# Data Classes
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
        result['threat_level'] = self.threat_level.value
        result['timestamp'] = self.timestamp.isoformat()
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
        result['action'] = self.action.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


# Memory System
class Memory:
    def __init__(self):
        self.memories: List[Dict[str, Any]] = []

    def remember(self, evidence: Evidence, decision: Decision):
        memory_entry = {
            'evidence': evidence.to_dict(),
            'decision': decision.to_dict(),
            'weight': 1.0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.memories.append(memory_entry)

    def decay_memories(self):
        """Apply decay to memory weights"""
        for memory in self.memories:
            if 'weight' not in memory:
                memory['weight'] = 1.0
            memory['weight'] *= 0.95  # Decay factor


# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        """Monitor system health metrics"""
        return {
            'cpu_usage': 25.0,
            'memory_usage': 45.0,
            'disk_usage': 30.0,
            'network_latency': 10.0
        }

    def diagnose_problems(self) -> List[str]:
        """Diagnose system problems"""
        health = self.monitor_health()
        problems = []
        
        if health.get('cpu_usage', 0) > 80:
            problems.append('high_cpu')
        if health.get('memory_usage', 0) > 90:
            problems.append('high_memory')
        if health.get('disk_usage', 0) > 95:
            problems.append('high_disk')
            
        return problems

    def self_heal(self, problems: List[str]) -> List[str]:
        """Attempt to heal detected problems"""
        healing_actions = []
        
        for problem in problems:
            if problem == 'high_cpu':
                healing_actions.append('reduced_processing_load')
            elif problem == 'high_memory':
                healing_actions.append('cleared_memory_cache')
            elif problem == 'high_disk':
                healing_actions.append('cleaned_temp_files')
                
        return healing_actions


# Main Living Cybersecurity System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = Memory()
        self.healing_system = HealingSystem()

    async def process_evidence(self, evidence: Evidence) -> Decision:
        """Process evidence and make a decision"""
        # Simple decision logic based on threat level and confidence
        if evidence.threat_level == ThreatLevel.CRITICAL and evidence.confidence > 0.8:
            action = ActionType.QUARANTINE
            confidence = min(evidence.confidence * 1.1, 1.0)
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS and evidence.confidence > 0.5:
            action = ActionType.BLOCK
            confidence = evidence.confidence * 0.9
        else:
            action = ActionType.MONITOR
            confidence = evidence.confidence * 0.8

        decision = Decision(
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=confidence,
            reasoning=f"Based on {evidence.threat_level.value} threat level with {evidence.confidence} confidence",
            evidence_count=1
        )

        # Store in memory
        self.memory.remember(evidence, decision)
        
        return decision


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


# FastAPI Application
app = FastAPI(title="Living Cybersecurity System", version="1.0.0")

# Global system instance
living_system = LivingCyberSecuritySystem({
    "learning_rate": 0.1,
    "memory_size": 1000,
    "evolution_interval": 60
})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": living_system.healing_system.monitor_health()
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "memory_count": len(living_system.memory.memories),
        "system_health": living_system.healing_system.monitor_health(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/evidence/batch")
async def process_evidence_batch(request: EvidenceBatchRequest):
    """Process a batch of evidence"""
    try:
        decisions = []
        
        for evidence_data in request.evidences:
            # Convert string timestamp to datetime
            timestamp = datetime.fromisoformat(evidence_data.timestamp.replace('Z', '+00:00'))
            
            # Convert string threat level to enum
            threat_level = ThreatLevel(evidence_data.threat_level)
            
            # Create Evidence object
            evidence = Evidence(
                source=evidence_data.source,
                timestamp=timestamp,
                entity_id=evidence_data.entity_id,
                threat_level=threat_level,
                confidence=evidence_data.confidence,
                metrics=evidence_data.metrics
            )
            
            # Process evidence
            decision = await living_system.process_evidence(evidence)
            decisions.append(decision.to_dict())
        
        return {
            "status": "success",
            "processed_count": len(decisions),
            "decisions": decisions
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Processing error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)