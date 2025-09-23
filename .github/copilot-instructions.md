# Arkab - Living Cyber Security System

Arkab is a Python FastAPI application that implements a "Living Cyber Security System" - an adaptive cybersecurity orchestrator that processes evidence from security sensors and makes intelligent decisions about threats. The system includes memory, learning capabilities, and self-healing functionality.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Initial Setup and Dependencies
- Install dependencies: `python -m pip install --upgrade pip`
- Install requirements: `pip install -r requirements.txt --timeout 300`
  - May timeout due to network issues in sandboxed environments. If timeout occurs, retry with longer timeout or document as network limitation.
- Install test coverage: `pip install pytest-cov` (if not already installed)

### Building and Testing
- **NEVER CANCEL** builds or test commands - all operations complete quickly (under 3 seconds)
- Run tests: `python -m pytest tests/ -v` -- completes in ~2 seconds. Set timeout to 30+ seconds for safety.
- Run tests with coverage: `pytest -v --cov=app --cov-report=term` -- completes in ~2 seconds
- Run CI-style tests: `PYTHONPATH=/home/runner/work/arkab/arkab pytest -v --cov=app --cov-report=xml --cov-report=term` -- completes in ~2 seconds

### Running the Application
- Start server: `python -m uvicorn app.orchestrator:app --host 0.0.0.0 --port 8000`
- Alternative start: `python app/orchestrator.py` (runs on port 8000)
- Application starts immediately (< 1 second startup time)

### Validation Scenarios
**ALWAYS manually validate any changes by running these complete scenarios:**

1. **Basic API Health Check:**
   ```bash
   # Start server in background
   python -m uvicorn app.orchestrator:app --host 0.0.0.0 --port 8000 &
   sleep 2
   
   # Test health endpoint
   curl -s http://localhost:8000/health | python -m json.tool
   
   # Should return: {"status": "healthy", "timestamp": "...", "system_health": {...}}
   ```

2. **Evidence Processing Workflow:**
   ```bash
   # Test evidence batch processing
   curl -s -X POST http://localhost:8000/evidence/batch \
     -H "Content-Type: application/json" \
     -d '{
       "evidences": [
         {
           "source": "sensor-1",
           "timestamp": "2025-09-23T15:57:00.000000+00:00",
           "entity_id": "host-1", 
           "threat_level": "critical",
           "confidence": 0.9,
           "metrics": {"cpu": 95, "network": 200}
         }
       ]
     }' | python -m json.tool
   
   # Should return decision with action "isolate" and high confidence
   
   # Verify memory updated
   curl -s http://localhost:8000/metrics | python -m json.tool
   # Should show memory_count: 1, decision_count: 1
   ```

3. **Core System Functionality Test:**
   ```python
   # Run this Python snippet to validate core classes
   python -c "
   import app.orchestrator
   import asyncio
   from datetime import datetime, timezone
   
   system = app.orchestrator.LivingCyberSecuritySystem({'learning_rate': 0.1, 'memory_size': 1000, 'evolution_interval': 60})
   evidence = app.orchestrator.Evidence(
       source='test-sensor',
       timestamp=datetime.now(timezone.utc),
       entity_id='test-host',
       threat_level=app.orchestrator.ThreatLevel.CRITICAL,
       confidence=0.95,
       metrics={'cpu': 95, 'network': 200}
   )
   
   async def test():
       decision = await system.process_evidence(evidence)
       print(f'Decision: {decision.action.value} with confidence {decision.confidence}')
       print(f'Memory count: {len(system.memory.memories)}')
   
   asyncio.run(test())
   "
   ```

### Key Application Components

**Main Files:**
- `app/orchestrator.py` - Core application with FastAPI server and cybersecurity logic
- `tests/test_orchestrator.py` - Comprehensive test suite (8 tests)
- `requirements.txt` - All dependencies (pytest, fastapi, psutil, uvicorn, etc.)
- `.github/workflows/test.yml` - CI pipeline (uses PostgreSQL, Redis, NATS services but app runs standalone)

**API Endpoints:**
- `GET /health` - Health check and system status
- `GET /metrics` - System metrics (memory count, decisions, CPU usage)
- `POST /evidence/batch` - Process cybersecurity evidence and get decisions

**Core Classes:**
- `LivingCyberSecuritySystem` - Main orchestrator class
- `Evidence` - Security event data model
- `Decision` - System decision output
- `ThreatLevel` - Enum: BENIGN, SUSPICIOUS, CRITICAL  
- `ActionType` - Enum: MONITOR, BLOCK, ISOLATE
- `Memory` - Evidence/decision storage with decay
- `HealingSystem` - Self-monitoring and healing

## Common Issues and Solutions

### Network/Installation Issues
- `pip install` may timeout in sandboxed environments. Use `--timeout 300` flag or document as limitation.
- If virtual environments fail, use system Python with `--user` flag: `pip install -r requirements.txt --user`

### Testing
- All tests pass with 85%+ code coverage
- Tests complete in ~2 seconds - if they take longer, investigate environment issues
- PostgreSQL, Redis, NATS services in CI are for future functionality - current app runs standalone

### Application Behavior
- System makes intelligent decisions based on threat level and confidence:
  - CRITICAL + high confidence → ISOLATE action
  - SUSPICIOUS + medium confidence → BLOCK action  
  - Otherwise → MONITOR action
- Memory system stores evidence/decision pairs with decay
- Self-healing monitors CPU/memory usage and suggests mitigations

## Development Workflow
1. ALWAYS run tests first: `pytest -v`
2. Start application for testing: `python app/orchestrator.py`
3. Test endpoints with curl commands above
4. Run full test suite with coverage before committing
5. No additional linting tools configured - only pytest validation required

## Environment Details
- Python 3.11+ required (tested with 3.12.3)
- No environment variables needed
- No external databases required for basic operation
- Application runs on localhost:8000 by default