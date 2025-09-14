"""
Orchestrator module for the Living Cyber Security System
"""
import asyncio
import psutil
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

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
        """Convert Evidence to dictionary"""
        return {
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "threat_level": self.threat_level.value,
            "confidence": self.confidence,
            "metrics": self.metrics,
        }


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
        """Convert Decision to dictionary"""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "action": self.action.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "evidence_count": self.evidence_count,
        }


# Memory System
class MemorySystem:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.memories: List[Dict[str, Any]] = []

    def remember(self, evidence: Evidence, decision: Decision):
        """Store evidence and decision in memory"""
        memory_entry = {
            "evidence": evidence.to_dict(),
            "decision": decision.to_dict(),
            "weight": 1.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.memories.append(memory_entry)
        
        # Keep memory size under limit
        if len(self.memories) > self.max_size:
            self.memories.pop(0)

    def decay_memories(self):
        """Apply decay to memory weights"""
        for memory in self.memories:
            memory["weight"] *= 0.95  # Decay factor


# Healing System
class HealingSystem:
    def __init__(self):
        self.last_check = time.time()

    def monitor_health(self) -> Dict[str, Any]:
        """Monitor system health metrics"""
        try:
            return {
                "cpu_usage": psutil.cpu_percent(interval=0.1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception:
            # Fallback if psutil not available
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def diagnose_problems(self) -> List[str]:
        """Diagnose system problems"""
        problems = []
        health = self.monitor_health()
        
        if health["cpu_usage"] > 90:
            problems.append("high_cpu")
        if health["memory_usage"] > 90:
            problems.append("high_memory")
        if health["disk_usage"] > 90:
            problems.append("high_disk")
            
        return problems

    def self_heal(self, problems: List[str]) -> List[str]:
        """Attempt self-healing actions"""
        healing_actions = []
        for problem in problems:
            if problem == "high_cpu":
                healing_actions.append("reduce_background_tasks")
            elif problem == "high_memory":
                healing_actions.append("clear_cache")
            elif problem == "high_disk":
                healing_actions.append("cleanup_logs")
        return healing_actions


# Living Cyber Security System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = MemorySystem(config.get("memory_size", 1000))
        self.healing_system = HealingSystem()
        
    async def process_evidence(self, evidence: Evidence) -> Decision:
        """Process evidence and make a decision"""
        # Simple decision logic based on threat level and confidence
        if evidence.threat_level == ThreatLevel.CRITICAL and evidence.confidence > 0.8:
            action = ActionType.BLOCK
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS and evidence.confidence > 0.6:
            action = ActionType.MONITOR
        else:
            action = ActionType.MONITOR
            
        decision = Decision(
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=min(evidence.confidence * 0.9, 1.0),
            reasoning=f"Based on {evidence.threat_level.value} threat level",
            evidence_count=1,
        )
        
        # Store in memory
        self.memory.remember(evidence, decision)
        
        return decision


# FastAPI app instance
app = FastAPI(title="Living Cyber Security System", version="1.0.0")

# Global system instance
system_config = {"learning_rate": 0.1, "memory_size": 1000, "evolution_interval": 60}
living_system = LivingCyberSecuritySystem(system_config)


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


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": living_system.healing_system.monitor_health(),
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "memory_count": len(living_system.memory.memories),
        "system_health": living_system.healing_system.monitor_health(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/evidence/batch")
async def process_evidence_batch(request: EvidenceBatchRequest):
    """Process a batch of evidence"""
    try:
        decisions = []
        for evidence_data in request.evidences:
            # Convert string threat level to enum
            threat_level = ThreatLevel(evidence_data.threat_level)
            
            # Create Evidence object
            evidence = Evidence(
                source=evidence_data.source,
                timestamp=datetime.fromisoformat(evidence_data.timestamp.replace('Z', '+00:00')),
                entity_id=evidence_data.entity_id,
                threat_level=threat_level,
                confidence=evidence_data.confidence,
                metrics=evidence_data.metrics,
            )
            
            # Process evidence
            decision = await living_system.process_evidence(evidence)
            decisions.append(decision.to_dict())
        
        return {
            "status": "processed",
            "decisions": decisions,
            "count": len(decisions),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Processing error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)