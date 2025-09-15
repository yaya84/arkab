from fastapi import FastAPI
from datetime import datetime, timezone
from enum import Enum

app = FastAPI()

class ThreatLevel(Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    CRITICAL = "critical"

class ActionType(Enum):
    MONITOR = "monitor"
    BLOCK = "block"
    ALERT = "alert"

class Evidence:
    def __init__(self, source, timestamp, entity_id, threat_level, confidence, metrics):
        self.source = source
        self.timestamp = timestamp
        self.entity_id = entity_id
        self.threat_level = threat_level
        self.confidence = confidence
        self.metrics = metrics
    
    def to_dict(self):
        return {
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "threat_level": self.threat_level.value,
            "confidence": self.confidence,
            "metrics": self.metrics,
        }

class Decision:
    def __init__(self, decision_id, timestamp, entity_id, action, confidence, reasoning, evidence_count):
        self.decision_id = decision_id
        self.timestamp = timestamp
        self.entity_id = entity_id
        self.action = action
        self.confidence = confidence
        self.reasoning = reasoning
        self.evidence_count = evidence_count
    
    def to_dict(self):
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "action": self.action.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "evidence_count": self.evidence_count,
        }

class Memory:
    def __init__(self):
        self.memories = []
    
    def remember(self, evidence, decision):
        self.memories.append({"evidence": evidence, "decision": decision, "weight": 1.0})
    
    def decay_memories(self):
        for memory in self.memories:
            memory["weight"] *= 0.9

class HealingSystem:
    def monitor_health(self):
        return {"cpu_usage": 10, "memory_usage": 20}
    
    def diagnose_problems(self):
        return []
    
    def self_heal(self, problems):
        return []

class LivingCyberSecuritySystem:
    def __init__(self, config):
        self.config = config
        self.memory = Memory()
        self.healing_system = HealingSystem()
    
    async def process_evidence(self, evidence):
        # Simulate processing and decision
        return Decision(
            decision_id="dec-test",
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=ActionType.MONITOR,
            confidence=evidence.confidence,
            reasoning="Test reasoning",
            evidence_count=1,
        )

# FastAPI endpoints
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return {"metrics": "data"}

@app.post("/evidence/batch")
async def evidence_batch(data: dict):
    return {"processed": len(data.get("evidences", []))}