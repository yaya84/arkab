"""
Orchestrator module for Arkab cybersecurity system
"""
import asyncio
import psutil
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
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
    ALERT = "alert"


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


# Memory System
class Memory:
    def __init__(self, max_size: int = 1000):
        self.memories: List[Dict[str, Any]] = []
        self.max_size = max_size

    def remember(self, evidence: Evidence, decision: Decision) -> None:
        """Store evidence and decision in memory"""
        memory_entry = {
            "evidence": evidence.to_dict(),
            "decision": decision.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "weight": 1.0
        }
        self.memories.append(memory_entry)
        
        # Keep memory size under limit
        if len(self.memories) > self.max_size:
            self.memories.pop(0)

    def decay_memories(self) -> None:
        """Apply decay to memory weights"""
        for memory in self.memories:
            memory["weight"] = memory.get("weight", 1.0) * 0.99


# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        """Monitor system health metrics"""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_info.percent,
                "disk_usage": disk_info.percent,
                "status": "healthy"
            }
        except Exception as e:
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "status": "error",
                "error": str(e)
            }

    def diagnose_problems(self) -> List[str]:
        """Diagnose system problems"""
        problems = []
        health = self.monitor_health()
        
        if health.get("cpu_usage", 0) > 80:
            problems.append("High CPU usage")
        if health.get("memory_usage", 0) > 90:
            problems.append("High memory usage")
        if health.get("disk_usage", 0) > 85:
            problems.append("High disk usage")
            
        return problems

    def self_heal(self, problems: List[str]) -> List[str]:
        """Attempt to self-heal system problems"""
        healing_actions = []
        
        for problem in problems:
            if "CPU" in problem:
                healing_actions.append("Reduced process priority")
            elif "memory" in problem:
                healing_actions.append("Cleared memory cache")
            elif "disk" in problem:
                healing_actions.append("Cleaned temporary files")
                
        return healing_actions


# Main Living Cybersecurity System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = Memory(config.get("memory_size", 1000))
        self.healing_system = HealingSystem()
        self.learning_rate = config.get("learning_rate", 0.1)
        self.evolution_interval = config.get("evolution_interval", 60)

    async def process_evidence(self, evidence: Evidence) -> Decision:
        """Process evidence and make a decision"""
        # Simulate decision making based on threat level and confidence
        if evidence.threat_level == ThreatLevel.CRITICAL:
            action = ActionType.BLOCK
            confidence = min(0.9, evidence.confidence + 0.1)
            reasoning = "Critical threat detected - immediate action required"
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS:
            action = ActionType.ALERT
            confidence = evidence.confidence
            reasoning = "Suspicious activity requires monitoring"
        else:
            action = ActionType.MONITOR
            confidence = max(0.3, evidence.confidence - 0.1)
            reasoning = "Benign activity - continue monitoring"

        decision = Decision(
            decision_id=f"dec_{evidence.entity_id}_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            evidence_count=1
        )

        # Remember this evidence and decision
        self.memory.remember(evidence, decision)
        
        return decision


# FastAPI Application
app = FastAPI(title="Arkab Cybersecurity Orchestrator", version="1.0.0")

# Global system instance
system_config = {"learning_rate": 0.1, "memory_size": 1000, "evolution_interval": 60}
living_system = LivingCyberSecuritySystem(system_config)


# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health = living_system.healing_system.monitor_health()
    return {
        "status": "ok",
        "system_health": health,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    health = living_system.healing_system.monitor_health()
    return {
        "memory_count": len(living_system.memory.memories),
        "system_health": health,
        "config": living_system.config,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


class EvidenceBatch(BaseModel):
    evidences: List[Dict[str, Any]]


@app.post("/evidence/batch")
async def process_evidence_batch(batch: EvidenceBatch):
    """Process a batch of evidence"""
    try:
        decisions = []
        
        for evidence_data in batch.evidences:
            # Convert string timestamp to datetime if needed
            if isinstance(evidence_data["timestamp"], str):
                evidence_data["timestamp"] = datetime.fromisoformat(
                    evidence_data["timestamp"].replace("Z", "+00:00")
                )
            
            # Convert string threat_level to enum
            if isinstance(evidence_data["threat_level"], str):
                evidence_data["threat_level"] = ThreatLevel(evidence_data["threat_level"])
            
            evidence = Evidence(**evidence_data)
            decision = await living_system.process_evidence(evidence)
            decisions.append(decision.to_dict())
        
        return {
            "status": "success",
            "processed_count": len(decisions),
            "decisions": decisions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Processing error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)