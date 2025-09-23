"""
Arkab - Living Cyber Security System Orchestrator
A FastAPI application for processing cybersecurity evidence and making decisions.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
import asyncio
import psutil
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Enums
class ThreatLevel(str, Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious" 
    CRITICAL = "critical"


class ActionType(str, Enum):
    MONITOR = "monitor"
    BLOCK = "block" 
    ISOLATE = "isolate"


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


# Request/Response Models  
class EvidenceBatchRequest(BaseModel):
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
            "weight": 1.0,
            "timestamp": datetime.now(timezone.utc)
        }
        self.memories.append(memory)
        
        if len(self.memories) > self.max_size:
            self.memories.pop(0)
    
    def decay_memories(self):
        for memory in self.memories:
            if "weight" not in memory:
                memory["weight"] = 1.0
            memory["weight"] *= 0.99  # Simple decay


# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def diagnose_problems(self) -> List[str]:
        problems = []
        health = self.monitor_health()
        
        if health["cpu_usage"] > 90:
            problems.append("high_cpu")
        if health["memory_usage"] > 90:
            problems.append("high_memory")
            
        return problems
    
    def self_heal(self, problems: List[str]) -> List[str]:
        actions = []
        for problem in problems:
            if problem == "high_cpu":
                actions.append("throttle_processing")
            elif problem == "high_memory":
                actions.append("clear_cache")
        return actions


# Main Living Cyber Security System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = Memory(max_size=config.get("memory_size", 1000))
        self.healing_system = HealingSystem()
        self.decision_counter = 0
    
    async def process_evidence(self, evidence: Evidence) -> Decision:
        self.decision_counter += 1
        
        # Simple decision logic based on threat level and confidence
        if evidence.threat_level == ThreatLevel.CRITICAL and evidence.confidence > 0.8:
            action = ActionType.ISOLATE
            confidence = min(evidence.confidence + 0.1, 1.0)
            reasoning = "High confidence critical threat"
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS and evidence.confidence > 0.5:
            action = ActionType.BLOCK  
            confidence = evidence.confidence
            reasoning = "Suspicious activity detected"
        else:
            action = ActionType.MONITOR
            confidence = evidence.confidence * 0.8
            reasoning = "Low threat level or confidence"
        
        decision = Decision(
            decision_id=f"dec_{self.decision_counter}",
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            evidence_count=1
        )
        
        self.memory.remember(evidence, decision)
        return decision


# FastAPI Application
app = FastAPI(title="Arkab - Living Cyber Security System", version="1.0.0")

# Global system instance
living_system = LivingCyberSecuritySystem({
    "learning_rate": 0.1,
    "memory_size": 1000, 
    "evolution_interval": 60
})


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_health": living_system.healing_system.monitor_health()
    }


@app.get("/metrics")
async def get_metrics():
    return {
        "memory_count": len(living_system.memory.memories),
        "decision_count": living_system.decision_counter,
        "system_health": living_system.healing_system.monitor_health(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/evidence/batch")
async def process_evidence_batch(request: EvidenceBatchRequest):
    try:
        results = []
        for evidence_data in request.evidences:
            # Convert dict to Evidence object
            evidence_data["timestamp"] = datetime.fromisoformat(evidence_data["timestamp"].replace("Z", "+00:00"))
            evidence_data["threat_level"] = ThreatLevel(evidence_data["threat_level"])
            
            evidence = Evidence(**evidence_data)
            decision = await living_system.process_evidence(evidence)
            results.append(decision.to_dict())
        
        return {"decisions": results, "processed": len(results)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Processing error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)