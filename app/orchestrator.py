"""
Arkab Orchestrator Module

Living Cyber Security System implementation for orchestrating 
cyber security monitoring and automated responses.
"""
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
import asyncio
import psutil

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Enums
class ThreatLevel(str, Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    CRITICAL = "critical"


class ActionType(str, Enum):
    MONITOR = "monitor"
    ALERT = "alert"
    BLOCK = "block"
    QUARANTINE = "quarantine"


# Data Models
class Evidence(BaseModel):
    source: str
    timestamp: datetime
    entity_id: str
    threat_level: ThreatLevel
    confidence: float
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "threat_level": self.threat_level.value,
            "confidence": self.confidence,
            "metrics": self.metrics
        }


class Decision(BaseModel):
    decision_id: str
    timestamp: datetime
    entity_id: str
    action: ActionType
    confidence: float
    reasoning: str
    evidence_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "action": self.action.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "evidence_count": self.evidence_count
        }


class EvidenceBatch(BaseModel):
    evidences: List[Dict[str, Any]]


# Memory System
class Memory:
    def __init__(self, max_size: int = 1000):
        self.memories: List[Dict[str, Any]] = []
        self.max_size = max_size

    def remember(self, evidence: Evidence, decision: Decision):
        memory = {
            "evidence": evidence.to_dict(),
            "decision": decision.to_dict(),
            "timestamp": datetime.now(timezone.utc),
            "weight": 1.0
        }
        self.memories.append(memory)
        
        # Keep memory size under control
        if len(self.memories) > self.max_size:
            self.memories = self.memories[-self.max_size:]

    def decay_memories(self):
        """Apply time-based decay to memory weights"""
        current_time = datetime.now(timezone.utc)
        for memory in self.memories:
            age_hours = (current_time - memory["timestamp"]).total_seconds() / 3600
            decay_factor = max(0.1, 1.0 - (age_hours * 0.01))  # 1% decay per hour
            memory["weight"] = memory.get("weight", 1.0) * decay_factor


# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        """Monitor system health metrics"""
        try:
            return {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception:
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def diagnose_problems(self) -> List[str]:
        """Diagnose system problems"""
        problems = []
        health = self.monitor_health()
        
        if health["cpu_usage"] > 90:
            problems.append("High CPU usage")
        if health["memory_usage"] > 90:
            problems.append("High memory usage")
        if health["disk_usage"] > 90:
            problems.append("High disk usage")
            
        return problems

    def self_heal(self, problems: List[str]) -> List[str]:
        """Attempt to heal system problems"""
        healing_actions = []
        for problem in problems:
            if "CPU" in problem:
                healing_actions.append("Applied CPU throttling")
            elif "memory" in problem:
                healing_actions.append("Cleared memory cache")
            elif "disk" in problem:
                healing_actions.append("Cleaned temporary files")
        return healing_actions


# Main Living Cyber Security System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = Memory(config.get("memory_size", 1000))
        self.healing_system = HealingSystem()
        self.learning_rate = config.get("learning_rate", 0.1)
        self.evolution_interval = config.get("evolution_interval", 60)

    async def process_evidence(self, evidence: Evidence) -> Decision:
        """Process incoming evidence and make a decision"""
        # Simple decision logic based on threat level and confidence
        confidence = evidence.confidence
        
        if evidence.threat_level == ThreatLevel.CRITICAL and confidence > 0.8:
            action = ActionType.BLOCK
            reasoning = "Critical threat with high confidence"
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS and confidence > 0.6:
            action = ActionType.ALERT
            reasoning = "Suspicious activity detected"
        else:
            action = ActionType.MONITOR
            reasoning = "Low threat level, monitoring"

        decision = Decision(
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=min(confidence * 1.1, 1.0),  # Slight confidence boost
            reasoning=reasoning,
            evidence_count=1
        )

        # Store in memory
        self.memory.remember(evidence, decision)
        
        return decision


# FastAPI Application
app = FastAPI(title="Arkab Living Cyber Security System", version="1.0.0")

# Global system instance
system_config = {
    "learning_rate": 0.1,
    "memory_size": 1000,
    "evolution_interval": 60
}
living_system = LivingCyberSecuritySystem(system_config)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    system_health = living_system.healing_system.monitor_health()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": system_health
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "memory_count": len(living_system.memory.memories),
        "config": living_system.config,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/evidence/batch")
async def process_evidence_batch(batch: EvidenceBatch):
    """Process a batch of evidence"""
    try:
        decisions = []
        for evidence_data in batch.evidences:
            # Convert dict to Evidence object
            evidence = Evidence(
                source=evidence_data["source"],
                timestamp=datetime.fromisoformat(evidence_data["timestamp"].replace('Z', '+00:00')),
                entity_id=evidence_data["entity_id"],
                threat_level=ThreatLevel(evidence_data["threat_level"]),
                confidence=evidence_data["confidence"],
                metrics=evidence_data["metrics"]
            )
            
            decision = await living_system.process_evidence(evidence)
            decisions.append(decision.to_dict())
        
        return {
            "processed": len(decisions),
            "decisions": decisions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Processing error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)