import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.orchestrator import (
    app,
    LivingCyberSecuritySystem,
    Evidence,
    ThreatLevel,
    ActionType,
    Decision,
)

# ----------------------------
# FIXTURES
# ----------------------------
@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture
def living_system():
    config = {"learning_rate": 0.1, "memory_size": 1000, "evolution_interval": 60}
    return LivingCyberSecuritySystem(config)


# ----------------------------
# UNIT TESTS
# ----------------------------

def test_evidence_to_dict():
    e = Evidence(
        source="sensor-1",
        timestamp=datetime.now(timezone.utc),
        entity_id="host-1",
        threat_level=ThreatLevel.SUSPICIOUS,
        confidence=0.7,
        metrics={"cpu": 50},
    )
    d = e.to_dict()
    assert d["entity_id"] == "host-1"
    assert d["threat_level"] == "suspicious"
    assert "timestamp" in d


def test_decision_to_dict():
    d = Decision(
        decision_id="abc123",
        timestamp=datetime.now(timezone.utc),
        entity_id="host-1",
        action=ActionType.MONITOR,
        confidence=0.8,
        reasoning="test",
        evidence_count=1,
    )
    dd = d.to_dict()
    assert dd["action"] == "monitor"
    assert dd["entity_id"] == "host-1"


@pytest.mark.asyncio
async def test_process_evidence(living_system):
    e = Evidence(
        source="sensor-2",
        timestamp=datetime.now(timezone.utc),
        entity_id="server-db",
        threat_level=ThreatLevel.CRITICAL,
        confidence=0.9,
        metrics={"network": 120},
    )
    decision = await living_system.process_evidence(e)
    assert isinstance(decision, Decision)
    assert decision.entity_id == "server-db"
    assert decision.confidence >= 0.0 and decision.confidence <= 1.0


def test_memory_decay(living_system):
    e = Evidence(
        source="sensor-3",
        timestamp=datetime.now(timezone.utc),
        entity_id="iot-1",
        threat_level=ThreatLevel.BENIGN,
        confidence=0.3,
        metrics={"activity": 5},
    )
    d = Decision(
        decision_id="dec1",
        timestamp=datetime.now(timezone.utc),
        entity_id="iot-1",
        action=ActionType.MONITOR,
        confidence=0.3,
        reasoning="low threat",
        evidence_count=1,
    )
    living_system.memory.remember(e, d)
    assert len(living_system.memory.memories) > 0
    living_system.memory.decay_memories()
    assert "weight" in living_system.memory.memories[-1]


def test_healing_system(living_system):
    health = living_system.healing_system.monitor_health()
    assert "cpu_usage" in health
    problems = living_system.healing_system.diagnose_problems()
    if problems:
        healing = living_system.healing_system.self_heal(problems)
        assert isinstance(healing, list)


# ----------------------------
# API TESTS (FastAPI)
# ----------------------------
def test_api_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()

def test_api_metrics(client):
    r = client.get("/metrics")
    assert r.status_code == 200


def test_api_evidence_batch(client):
    e = {
        "source": "sensor-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entity_id": "api-host",
        "threat_level": "suspicious",
        "confidence": 0.75,
        "metrics": {"cpu": 70},
    }
    r = client.post("/evidence/batch", json={"evidences": [e]})
    assert r.status_code in [200, 503]  # 503 si orchestrator non démarré
