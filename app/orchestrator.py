"""
Orchestrator module for the Arkab Living Cyber Security System.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
import psutil

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
    def __init__(self):
        self.memories: List[Dict[str, Any]] = []

    def remember(self, evidence: Evidence, decision: Decision):
        memory = {
            "evidence": evidence.to_dict(),
            "decision": decision.to_dict(),
            "weight": 1.0,
            "timestamp": datetime.now(timezone.utc)
        }
        self.memories.append(memory)

    def decay_memories(self):
        """Apply memory decay to reduce weight of old memories"""
        for memory in self.memories:
            memory["weight"] *= 0.95  # Decay factor


# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        """Monitor system health metrics"""
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
        }

    def diagnose_problems(self) -> List[str]:
        """Diagnose system problems"""
        problems = []
        health = self.monitor_health()
        
        if health.get("cpu_usage", 0) > 80:
            problems.append("high_cpu_usage")
        if health.get("memory_usage", 0) > 90:
            problems.append("high_memory_usage")
        
        return problems

    def self_heal(self, problems: List[str]) -> List[str]:
        """Attempt to self-heal identified problems"""
        healing_actions = []
        for problem in problems:
            if problem == "high_cpu_usage":
                healing_actions.append("reduced_processing_load")
            elif problem == "high_memory_usage":
                healing_actions.append("cleared_memory_cache")
        return healing_actions


# Main Living Cyber Security System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = Memory()
        self.healing_system = HealingSystem()
        self.learning_rate = config.get("learning_rate", 0.1)
        self.memory_size = config.get("memory_size", 1000)
        self.evolution_interval = config.get("evolution_interval", 60)

    async def process_evidence(self, evidence: Evidence) -> Decision:
        """Process evidence and make a decision"""
        # Simple decision logic based on threat level and confidence
        if evidence.threat_level == ThreatLevel.CRITICAL and evidence.confidence > 0.8:
            action = ActionType.BLOCK
            decision_confidence = 0.9
            reasoning = "Critical threat with high confidence"
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS:
            action = ActionType.MONITOR
            decision_confidence = evidence.confidence * 0.8
            reasoning = "Suspicious activity detected"
        else:
            action = ActionType.MONITOR
            decision_confidence = evidence.confidence * 0.5
            reasoning = "Benign activity"

        decision = Decision(
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=decision_confidence,
            reasoning=reasoning,
            evidence_count=1
        )

        # Store in memory
        self.memory.remember(evidence, decision)
        
        return decision


# FastAPI App
app = FastAPI(title="Arkab Living Cyber Security System")

# Global system instance (in a real application, this would be properly managed)
living_system = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    global living_system
    if living_system:
        health = living_system.healing_system.monitor_health()
        return {
            "system_health": health,
            "memory_count": len(living_system.memory.memories),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    return {"error": "System not initialized"}


@app.post("/evidence/batch")
async def process_evidence_batch(request: Dict[str, List[Dict]]):
    """Process a batch of evidence"""
    global living_system
    
    if not living_system:
        # Initialize if not already done
        config = {"learning_rate": 0.1, "memory_size": 1000, "evolution_interval": 60}
        living_system = LivingCyberSecuritySystem(config)
    
    evidences = request.get("evidences", [])
    results = []
    
    for evidence_data in evidences:
        try:
            # Convert timestamp string to datetime if needed
            if isinstance(evidence_data.get("timestamp"), str):
                evidence_data["timestamp"] = datetime.fromisoformat(
                    evidence_data["timestamp"].replace("Z", "+00:00")
                )
            
            # Convert threat_level string to enum
            if isinstance(evidence_data.get("threat_level"), str):
                evidence_data["threat_level"] = ThreatLevel(evidence_data["threat_level"])
            
            evidence = Evidence(**evidence_data)
            decision = await living_system.process_evidence(evidence)
            results.append(decision.to_dict())
        except Exception as e:
            results.append({"error": str(e)})
    
    return {"decisions": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)