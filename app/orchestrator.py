"""
Arkab Orchestrator - Living Cyber Security System
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
import asyncio
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


# Data Models
class Evidence:
    def __init__(self, source: str, timestamp: datetime, entity_id: str, 
                 threat_level: ThreatLevel, confidence: float, metrics: Dict[str, Any]):
        self.source = source
        self.timestamp = timestamp
        self.entity_id = entity_id
        self.threat_level = threat_level
        self.confidence = confidence
        self.metrics = metrics
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "threat_level": self.threat_level.value,
            "confidence": self.confidence,
            "metrics": self.metrics
        }


class Decision:
    def __init__(self, decision_id: str, timestamp: datetime, entity_id: str,
                 action: ActionType, confidence: float, reasoning: str, evidence_count: int):
        self.decision_id = decision_id
        self.timestamp = timestamp
        self.entity_id = entity_id
        self.action = action
        self.confidence = confidence
        self.reasoning = reasoning
        self.evidence_count = evidence_count
    
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
    
    def remember(self, evidence: Evidence, decision: Decision):
        memory_entry = {
            "evidence": evidence.to_dict(),
            "decision": decision.to_dict(),
            "weight": 1.0,
            "timestamp": datetime.now(timezone.utc)
        }
        self.memories.append(memory_entry)
        
        if len(self.memories) > self.max_size:
            self.memories.pop(0)
    
    def decay_memories(self):
        for memory in self.memories:
            if "weight" not in memory:
                memory["weight"] = 1.0
            memory["weight"] *= 0.99  # Decay factor


# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    def diagnose_problems(self) -> List[str]:
        problems = []
        health = self.monitor_health()
        
        if health["cpu_usage"] > 80:
            problems.append("High CPU usage")
        if health["memory_usage"] > 80:
            problems.append("High memory usage")
        if health["disk_usage"] > 90:
            problems.append("High disk usage")
            
        return problems
    
    def self_heal(self, problems: List[str]) -> List[str]:
        actions = []
        for problem in problems:
            if "CPU" in problem:
                actions.append("Reducing background processes")
            elif "memory" in problem:
                actions.append("Clearing cache")
            elif "disk" in problem:
                actions.append("Cleaning temporary files")
        return actions


# Main System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = Memory(max_size=config.get("memory_size", 1000))
        self.healing_system = HealingSystem()
        self.learning_rate = config.get("learning_rate", 0.1)
        self.evolution_interval = config.get("evolution_interval", 60)
    
    async def process_evidence(self, evidence: Evidence) -> Decision:
        # Simple decision logic based on threat level
        if evidence.threat_level == ThreatLevel.CRITICAL:
            action = ActionType.BLOCK
            confidence = 0.9
            reasoning = "Critical threat detected"
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS:
            action = ActionType.ISOLATE
            confidence = 0.7
            reasoning = "Suspicious activity requires isolation"
        else:
            action = ActionType.MONITOR
            confidence = 0.5
            reasoning = "Benign activity, continue monitoring"
        
        decision = Decision(
            decision_id=f"dec_{evidence.entity_id}_{int(datetime.now(timezone.utc).timestamp())}",
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            evidence_count=1
        )
        
        # Store in memory
        self.memory.remember(evidence, decision)
        
        return decision


# FastAPI Application
app = FastAPI(title="Arkab Orchestrator", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/metrics")
async def get_metrics():
    healing_system = HealingSystem()
    return healing_system.monitor_health()


class EvidenceBatchRequest(BaseModel):
    evidences: List[Dict[str, Any]]


@app.post("/evidence/batch")
async def process_evidence_batch(request: EvidenceBatchRequest):
    # Simple response for testing
    processed_count = len(request.evidences)
    return {
        "processed": processed_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }