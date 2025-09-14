"""
Cybersecurity Orchestrator Module

This module provides a living cybersecurity system with evidence processing,
memory management, and self-healing capabilities.
"""

import uuid
import asyncio
import psutil
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from fastapi import FastAPI


# Enums
class ThreatLevel(Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    CRITICAL = "critical"


class ActionType(Enum):
    MONITOR = "monitor"
    ISOLATE = "isolate"
    BLOCK = "block"


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
        data = asdict(self)
        data['threat_level'] = self.threat_level.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


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
        data = asdict(self)
        data['action'] = self.action.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


# Memory Management System
class MemorySystem:
    def __init__(self, max_size: int = 1000):
        self.memories: List[Dict[str, Any]] = []
        self.max_size = max_size

    def remember(self, evidence: Evidence, decision: Decision):
        """Store evidence and decision in memory"""
        memory_entry = {
            'evidence': evidence.to_dict(),
            'decision': decision.to_dict(),
            'weight': 1.0,
            'timestamp': datetime.now(timezone.utc)
        }
        self.memories.append(memory_entry)
        
        # Keep memory within size limit
        if len(self.memories) > self.max_size:
            self.memories.pop(0)

    def decay_memories(self):
        """Apply decay to memory weights"""
        for memory in self.memories:
            memory['weight'] *= 0.95  # Decay factor


# Healing System
class HealingSystem:
    def monitor_health(self) -> Dict[str, Any]:
        """Monitor system health metrics"""
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now(timezone.utc)
        }

    def diagnose_problems(self) -> List[str]:
        """Diagnose system problems"""
        problems = []
        health = self.monitor_health()
        
        if health['cpu_usage'] > 80:
            problems.append('high_cpu_usage')
        if health['memory_usage'] > 80:
            problems.append('high_memory_usage')
        if health['disk_usage'] > 90:
            problems.append('high_disk_usage')
            
        return problems

    def self_heal(self, problems: List[str]) -> List[str]:
        """Attempt to heal detected problems"""
        healing_actions = []
        for problem in problems:
            if problem == 'high_cpu_usage':
                healing_actions.append('throttled_processing')
            elif problem == 'high_memory_usage':
                healing_actions.append('memory_cleanup')
            elif problem == 'high_disk_usage':
                healing_actions.append('log_rotation')
        return healing_actions


# Main Living Cybersecurity System
class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = MemorySystem(config.get('memory_size', 1000))
        self.healing_system = HealingSystem()
        self.learning_rate = config.get('learning_rate', 0.1)
        self.evolution_interval = config.get('evolution_interval', 60)

    async def process_evidence(self, evidence: Evidence) -> Decision:
        """Process evidence and make a decision"""
        # Simple decision logic based on threat level and confidence
        confidence = evidence.confidence
        
        if evidence.threat_level == ThreatLevel.CRITICAL and confidence > 0.8:
            action = ActionType.ISOLATE
            reasoning = "High confidence critical threat detected"
        elif evidence.threat_level == ThreatLevel.SUSPICIOUS and confidence > 0.6:
            action = ActionType.MONITOR
            reasoning = "Suspicious activity requires monitoring"
        else:
            action = ActionType.MONITOR
            reasoning = "Low threat level, monitoring recommended"

        decision = Decision(
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            entity_id=evidence.entity_id,
            action=action,
            confidence=min(confidence + 0.1, 1.0),  # Slightly increase confidence
            reasoning=reasoning,
            evidence_count=1
        )

        # Remember this evidence and decision
        self.memory.remember(evidence, decision)
        
        return decision


# FastAPI Application
app = FastAPI(title="Living Cybersecurity System", version="1.0.0")

# Global system instance
living_system = None


@app.on_event("startup")
async def startup_event():
    global living_system
    config = {"learning_rate": 0.1, "memory_size": 1000, "evolution_interval": 60}
    living_system = LivingCyberSecuritySystem(config)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}


@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    if living_system:
        health = living_system.healing_system.monitor_health()
        return {
            "system_health": health,
            "memory_count": len(living_system.memory.memories),
            "config": living_system.config
        }
    return {"error": "System not initialized"}


@app.post("/evidence/batch")
async def process_evidence_batch(data: Dict[str, List[Dict[str, Any]]]):
    """Process a batch of evidence"""
    if not living_system:
        return {"error": "System not initialized"}, 503
    
    results = []
    evidences = data.get("evidences", [])
    
    for evidence_data in evidences:
        # Convert string threat_level to enum
        threat_level_str = evidence_data.get("threat_level", "benign")
        try:
            threat_level = ThreatLevel(threat_level_str)
        except ValueError:
            threat_level = ThreatLevel.BENIGN
        
        # Create Evidence object
        evidence = Evidence(
            source=evidence_data.get("source", "unknown"),
            timestamp=datetime.fromisoformat(evidence_data.get("timestamp", datetime.now(timezone.utc).isoformat())),
            entity_id=evidence_data.get("entity_id", "unknown"),
            threat_level=threat_level,
            confidence=float(evidence_data.get("confidence", 0.5)),
            metrics=evidence_data.get("metrics", {})
        )
        
        # Process evidence
        decision = await living_system.process_evidence(evidence)
        results.append(decision.to_dict())
    
    return {"decisions": results}