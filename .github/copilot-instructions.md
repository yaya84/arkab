# ARKAB - Living Cyber Security System

ARKAB is a Python-based living cyber security system built with FastAPI that processes security evidence and makes automated threat response decisions. The system features memory decay, self-healing capabilities, and RESTful API endpoints for evidence processing.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Initial Setup and Dependencies
- **CRITICAL**: Install Python dependencies using `pip install -r requirements.txt` - NEVER use requirements-dev.txt directly as it has network timeout issues
- Required Python version: 3.11+ (tested with 3.12.3)
- Install additional dependencies: `pip install psutil uvicorn pytest-cov`
- **NETWORK LIMITATION**: `pip install -r requirements-dev.txt` fails due to PyPI connection timeouts - use individual package installation instead

### Build and Test Commands
- **Bootstrap the repository**:
  ```bash
  cd /home/runner/work/arkab/arkab
  pip install -r requirements.txt
  pip install psutil uvicorn pytest-cov
  ```

- **Run tests**: `python -m pytest tests/ -v` - takes ~2 seconds, NEVER CANCEL
- **Run tests with coverage**: `python -m pytest tests/ -v --cov=app --cov-report=term` - takes ~2 seconds, NEVER CANCEL  
- **Test timeout setting**: Use 60 seconds minimum for any test commands (though they complete in 2 seconds)

### Running the Application
- **Start FastAPI server**: `python -m uvicorn app.orchestrator:app --host 0.0.0.0 --port 8000`
- **Alternative start method**: `python app/orchestrator.py` 
- **Server startup time**: ~1 second, NEVER CANCEL before 30 seconds
- **Default port**: 8000
- **Health check**: GET http://localhost:8000/health
- **Metrics endpoint**: GET http://localhost:8000/metrics
- **Evidence processing**: POST http://localhost:8000/evidence/batch

### External Service Dependencies (CI Environment)
The GitHub Actions CI pipeline requires these services which are automatically provided in CI but need manual setup for local development:

- **PostgreSQL 15**: `docker run --name postgres-test -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=test_db -p 5432:5432 -d postgres:15`
- **Redis 7**: `docker run --name redis-test -p 6379:6379 -d redis:7`  
- **NATS 2.9**: `docker run --name nats-test -p 4222:4222 -d nats:2.9-alpine`
- **Service startup time**: 10-30 seconds each, NEVER CANCEL before 60 seconds
- **Connection testing**:
  - PostgreSQL: `echo "SELECT 1;" | docker exec -i postgres-test psql -U postgres -d test_db`
  - Redis: `docker exec redis-test redis-cli ping`
  - NATS: `telnet localhost 4222` (connection test only)

## Validation and Testing

### Mandatory Manual Testing Scenarios
**ALWAYS run these validation scenarios after making changes:**

1. **Basic API Health Check**:
   ```bash
   # Start server
   python -m uvicorn app.orchestrator:app --host 0.0.0.0 --port 8000 &
   sleep 3
   
   # Test health endpoint
   curl -s http://localhost:8000/health | python -m json.tool
   
   # Stop server
   pkill -f uvicorn
   ```

2. **Evidence Processing Workflow**:
   ```bash
   # Start server in background
   python -m uvicorn app.orchestrator:app --host 0.0.0.0 --port 8000 &
   sleep 3
   
   # Process suspicious evidence
   curl -s -X POST http://localhost:8000/evidence/batch \
     -H "Content-Type: application/json" \
     -d '{
       "evidences": [
         {
           "source": "firewall-sensor",
           "timestamp": "2024-09-23T16:00:00Z",
           "entity_id": "web-server-01", 
           "threat_level": "suspicious",
           "confidence": 0.8,
           "metrics": {"failed_logins": 15}
         }
       ]
     }' | python -m json.tool
   
   # Verify decision was "monitor"
   # Check memory count increased: curl -s http://localhost:8000/metrics
   
   # Process critical evidence  
   curl -s -X POST http://localhost:8000/evidence/batch \
     -H "Content-Type: application/json" \
     -d '{
       "evidences": [
         {
           "source": "network-sensor",
           "timestamp": "2024-09-23T16:01:00Z",
           "entity_id": "db-server-01",
           "threat_level": "critical", 
           "confidence": 0.95,
           "metrics": {"anomalous_queries": 50}
         }
       ]
     }' | python -m json.tool
   
   # Verify decision was "isolate"
   # Verify memory count is now 2
   
   pkill -f uvicorn
   ```

3. **System Self-Healing Test**:
   ```bash
   python -c "
   from app.orchestrator import LivingCyberSecuritySystem
   config = {'learning_rate': 0.1, 'memory_size': 1000, 'evolution_interval': 60}
   system = LivingCyberSecuritySystem(config)
   health = system.healing_system.monitor_health()
   print('Health metrics:', health)
   problems = system.healing_system.diagnose_problems()
   print('Problems detected:', problems)
   "
   ```

### Expected Test Results
- **All 8 tests MUST pass** in test suite
- **Coverage should be 87%** for app/orchestrator.py
- **Health endpoint** returns status "healthy" with system metrics
- **Suspicious threats** result in "monitor" action
- **Critical threats** result in "isolate" action  
- **Memory system** increments count after evidence processing

## Code Structure and Key Components

### Repository Structure
```
/home/runner/work/arkab/arkab/
├── app/
│   ├── __init__.py
│   └── orchestrator.py          # Main application logic
├── tests/
│   └── test_orchestrator.py     # All tests (8 test cases)
├── .github/
│   └── workflows/
│       └── test.yml             # CI pipeline with service dependencies
├── requirements.txt             # Core dependencies (ALWAYS works)
├── requirements-dev.txt         # Dev dependencies (FAILS due to timeouts)  
├── pytest.ini                  # Pytest configuration
└── README.md                    # Minimal documentation
```

### Key Classes and Components
- **LivingCyberSecuritySystem**: Main orchestrator class with learning, memory, and healing
- **Evidence**: Data model for security events with threat levels (BENIGN, SUSPICIOUS, CRITICAL)
- **Decision**: Response model with actions (MONITOR, ISOLATE, BLOCK)
- **MemorySystem**: Stores and decays security memories over time
- **HealingSystem**: Monitors system health and performs self-healing
- **FastAPI app**: REST endpoints at /health, /metrics, /evidence/batch

### Import Structure
```python
from app.orchestrator import (
    app,                          # FastAPI application
    LivingCyberSecuritySystem,    # Main system class
    Evidence,                     # Evidence data model  
    ThreatLevel,                  # Enum: BENIGN, SUSPICIOUS, CRITICAL
    ActionType,                   # Enum: MONITOR, ISOLATE, BLOCK
    Decision,                     # Decision response model
)
```

## Known Issues and Limitations
- **requirements-dev.txt installation fails** due to PyPI network timeouts - install packages individually
- **No linting tools** are configured (black, flake8, mypy not available)
- **No CI build validation** beyond running tests
- **Docker services not required** for basic functionality but needed for full CI compatibility
- **Server runs on all interfaces** (0.0.0.0) - appropriate for containerized environments

## Common Commands Reference

### Quick Start Commands
```bash
# Full setup and test
pip install -r requirements.txt && pip install psutil uvicorn pytest-cov
python -m pytest tests/ -v
python -m uvicorn app.orchestrator:app --host 0.0.0.0 --port 8000

# Quick health check
curl http://localhost:8000/health

# Clean shutdown
pkill -f uvicorn
```

### Development Workflow
```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install psutil uvicorn pytest-cov

# 2. Run tests
python -m pytest tests/ -v --cov=app

# 3. Start development server  
python app/orchestrator.py

# 4. Validate with evidence processing (see validation scenarios above)

# 5. Stop server
# Ctrl+C or pkill -f uvicorn
```

**REMINDER**: Always validate changes with the complete evidence processing workflow before committing code changes.