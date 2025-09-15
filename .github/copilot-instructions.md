# Arkab - Living Cybersecurity System

Arkab is a Python-based living cybersecurity system built with FastAPI that provides adaptive threat detection, memory-based learning, and self-healing capabilities. The system processes cybersecurity evidence and makes automated decisions on threat mitigation.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap, Build, and Test the Repository

**CRITICAL: NEVER CANCEL long-running operations. Use these exact timeout values:**

- **Install Dependencies**: 
  - `python -m pip install --upgrade pip` (5 seconds)
  - `pip install -r requirements.txt` (30 seconds - NEVER CANCEL: Can take up to 45 seconds on slow networks)
  - `pip install pytest pytest-cov` (15 seconds)

- **Run Tests**:
  - `PYTHONPATH=/home/runner/work/arkab/arkab pytest -v --cov=app --cov-report=xml --cov-report=term` 
  - **NEVER CANCEL: Test suite takes 3-5 seconds normally, set timeout to 30+ seconds minimum**

- **Linting** (optional tools):
  - `pip install black flake8` (10 seconds)
  - `python -m black --check .` (1 second)
  - `python -m flake8 .` (1 second)

### Run the Application

**CRITICAL MISSING COMPONENT**: The repository is missing the core `app/orchestrator.py` file. Tests expect this module but it does not exist. You MUST create this file before the application will function.

**Required orchestrator.py structure** (based on test expectations):
```python
from fastapi import FastAPI
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any
import asyncio

app = FastAPI(title="Arkab Cybersecurity System")

class ThreatLevel(Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious" 
    CRITICAL = "critical"

class ActionType(Enum):
    MONITOR = "monitor"
    BLOCK = "block"
    ALERT = "alert"

@dataclass
class Evidence:
    source: str
    timestamp: datetime
    entity_id: str
    threat_level: ThreatLevel
    confidence: float
    metrics: Dict[str, Any]
    
    def to_dict(self):
        return {
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "threat_level": self.threat_level.value,
            "confidence": self.confidence,
            "metrics": self.metrics
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
    
    def to_dict(self):
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "action": self.action.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "evidence_count": self.evidence_count
        }

class LivingCyberSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = Memory()
        self.healing_system = HealingSystem()
    
    async def process_evidence(self, evidence: Evidence) -> Decision:
        # Implementation required
        pass

# FastAPI endpoints required:
# GET /health - returns {"status": "healthy", "timestamp": "..."}
# GET /metrics - returns system metrics
# POST /evidence/batch - accepts {"evidences": [...]}
```

**To run the server**:
- `pip install uvicorn` (5 seconds)
- `uvicorn app.orchestrator:app --host 0.0.0.0 --port 8000`

## Service Dependencies (CI Environment)

The CI pipeline (.github/workflows/test.yml) defines these service dependencies:

- **PostgreSQL 15**: Port 5432, DB: test_db, User: postgres, Password: postgres
- **Redis 7**: Port 6379  
- **NATS 2.9-alpine**: Port 4222

**NEVER CANCEL: Services can take 30-60 seconds to start in CI environment**

Health check configuration:
- Health interval: 10s
- Health timeout: 5s  
- Health retries: 5

## Validation

**ALWAYS run these validation scenarios after making changes to ensure the cybersecurity system works correctly:**

### Core Functionality Validation
1. **System Initialization**: Create LivingCyberSecuritySystem with config
2. **Threat Processing**: Test all threat levels (BENIGN, SUSPICIOUS, CRITICAL)
3. **Memory System**: Verify evidence storage and memory decay
4. **Self-Healing**: Test health monitoring and problem diagnosis
5. **API Endpoints**: Validate /health, /metrics, /evidence/batch endpoints

### Example Validation Script
```python
# Test different threat scenarios
evidence = Evidence(
    source="endpoint-monitor",
    timestamp=datetime.now(timezone.utc),
    entity_id="workstation-001", 
    threat_level=ThreatLevel.CRITICAL,
    confidence=0.95,
    metrics={"malware_detected": True}
)

decision = await system.process_evidence(evidence)
assert decision.action == ActionType.BLOCK  # Critical threats should be blocked
```

**Expected validation timing**: Complete validation should take under 1 second

## Build and Test Timing Expectations

**NEVER CANCEL these operations - always wait for completion:**

- **Fresh pip install**: 30-45 seconds (network dependent)
- **Test execution**: 3-5 seconds (set 30+ second timeout)
- **Coverage reporting**: Additional 1-2 seconds 
- **Linting with black**: Under 1 second
- **Linting with flake8**: Under 1 second
- **Service startup in CI**: 30-60 seconds (PostgreSQL, Redis, NATS)

## Common Tasks

### Repository Structure
```
arkab/
├── .github/workflows/test.yml  # CI pipeline with service dependencies
├── app/
│   ├── __init__.py            # Empty init file
│   └── orchestrator.py        # MISSING - Core application (create this!)
├── tests/
│   └── test_orchestrator.py   # Complete test suite (8 tests)
├── requirements.txt           # Core dependencies: pytest, pytest-asyncio, httpx, fastapi
├── requirements-dev.txt       # Dev dependencies: pytest==7.4.0, pytest-asyncio==0.21.0, httpx==0.24.0
└── pytest.ini               # Test configuration: pythonpath = .
```

### Key Dependencies
- **Python**: 3.11+ (CI uses 3.11)
- **FastAPI**: Web framework
- **pytest**: Testing (v7.4.0 in dev requirements)
- **pytest-asyncio**: Async testing (v0.21.0)
- **httpx**: HTTP client (v0.24.0)
- **uvicorn**: ASGI server (install separately)

### Common Issues and Solutions

1. **ModuleNotFoundError: No module named 'app.orchestrator'**
   - Create the missing `app/orchestrator.py` file with required classes
   - Follow the structure outlined above

2. **Import errors during testing**
   - Set `PYTHONPATH=/path/to/arkab` before running pytest
   - Verify pytest.ini has `pythonpath = .`

3. **CI service connection issues**  
   - Services take 30-60 seconds to start - NEVER CANCEL
   - Use health checks: PostgreSQL (pg_isready), Redis (redis-cli ping), NATS (nats-server --help)

4. **Test failures**
   - Ensure all required classes exist in orchestrator.py
   - Verify async methods use proper async/await syntax
   - Check FastAPI endpoints return expected JSON structure

## CRITICAL REMINDERS

- **NEVER CANCEL builds or tests** - Set 60+ minute timeouts for safety
- **The app/orchestrator.py file is MISSING** - you must create it for functionality
- **Always validate with complete threat scenarios** after changes
- **Use exact Python 3.11** to match CI environment
- **Service dependencies take 30-60 seconds to start** in CI - be patient