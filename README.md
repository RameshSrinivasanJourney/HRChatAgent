# HR Chat Agent — Complete Run Sequence

Terminal 1 → Database seed / verification
Terminal 2 → FastAPI backend + Ollama
Terminal 3 → Streamlit frontend


## Open PowerShell and go to project

cd C:\Users\rameshsrinivasan\DataScience\Projects\HRChatAgent

Activate the virtual environment:
.\.venv\Scripts\Activate.ps1

You should see something similar to:
(.venv) (base) PS C:\Users\rameshsrinivasan\DataScience\Projects\HRChatAgent>

## Start Ollama

Before starting the API, make sure Ollama is running.

Your Ollama executable is:
%LOCALAPPDATA%\Programs\Ollama\ollama.exe

Check the model:
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list

You should see:
llama3.2:3b
If Ollama is not already running, start it:

& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
Keep this terminal open.

If Ollama is already running as a Windows process, don't start a second server.

You can test the model:
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" run llama3.2:3b

Then type:
Hello

If it responds, press:
Ctrl+C

## Seed the HR database

Open Terminal 1.
Go to the project:
cd C:\Users\rameshsrinivasan\DataScience\Projects\HRChatAgent
Activate environment:
.\.venv\Scripts\Activate.ps1
Run:
python scripts_seed.py
You should see the seed process complete successfully.
Important
Your seed script is designed to recreate the demo employee data.
It creates:
Employee    Name            Status          EL
EMP1001     Arun Kumar      ACTIVE          14
EMP1002     Priya Sharma    ACTIVE          20
EMP1003     Rahul Menon     NOTICE_PERIOD   20

Password:
Password@123

For the demo, use:
EMP1001
Password@123

All users use:

```text
Password@123
```

Employees:

```text
EMP1001 - Active
EMP1002 - Active
EMP1003 - Notice Period
```

## Verify database schema

Because we previously had the SQLite schema issue, I recommend doing this once before the demo.
Run:
python -c "import app.models; from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('Schema creation completed')"

Expected:
Schema creation completed
This ensures the current models exist in:
hr.db

## Start FastAPI

Open Terminal 2.
cd C:\Users\rameshsrinivasan\DataScience\Projects\HRChatAgent
Activate:
.\.venv\Scripts\Activate.ps1

Start FastAPI:
uvicorn app.main:app --reload

You should see something similar to:
Uvicorn running on http://127.0.0.1:8000
Keep this terminal running.

##  Verify FastAPI

Open another PowerShell tab/window if necessary.

Run:
Invoke-RestMethod http://127.0.0.1:8000/health

Expected:
status service
------ -------
ok     hr-chat-agent
This confirms:
FastAPI
   ↓
Application loaded
   ↓
Database available
   ↓
Routes available

## Optional — open Swagger API documentation

Open this in your browser:
http://127.0.0.1:8000/docs

Don't type /docs into PowerShell.
Open it in Chrome/Edge.

You should see:
HR Chat Agent

with endpoints such as:
POST /auth/login
POST /chat/conversations
POST /chat
GET  /health

## Test login before starting UI

You can verify authentication from PowerShell.
Run:
$login = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/auth/login" `
    -ContentType "application/json" `
    -Body '{"employee_id":"EMP1001","password":"Password@123"}'

$login

You should receive something similar to:

access_token
------------
eyJhbGciOi...
This confirms:
Employee
   ↓
POST /auth/login
   ↓
Credential validation
   ↓
JWT generated

## Start Streamlit

Open Terminal 3.
cd C:\Users\rameshsrinivasan\DataScience\Projects\HRChatAgent
Activate:
.\.venv\Scripts\Activate.ps1

Start Streamlit:
python -m streamlit run frontend\streamlit_app.py

You should see something like:
Local URL: http://localhost:8501

Open:
http://localhost:8501

## Login through UI

Use:
Employee ID
EMP1001

Password:
Password@123

Click:

Login

The flow should be:
Streamlit
   ↓
POST /auth/login
   ↓
FastAPI
   ↓
Validate EMP1001
   ↓
JWT
   ↓
Streamlit stores JWT
   ↓
POST /chat/conversations
   ↓
Conversation ID
   ↓
Chat screen

## First demo question

Ask:
How much EL do I have?

Expected answer:
You have 14 days of EL remaining.

This is dynamic database-backed tool usage, not just RAG.

The internal flow is approximately:
User
 ↓
Streamlit
 ↓
FastAPI /chat
 ↓
HRChatService
 ↓
LangGraph
 ↓
LLM decides tool is required
 ↓
get_specific_leave_balance("EL")
 ↓
SQLite
 ↓
14 days
 ↓
LLM
 ↓
Final response

## Test policy RAG

Ask:
What is the annual leave entitlement?
The agent should retrieve the HR policy rather than querying the employee leave balance.

Then ask:
What is the EL accumulation limit?

Expected policy-grounded answer:
EL accumulation is capped at 20 days.

User question
      ↓
LangGraph Agent
      ↓
search_hr_policy
      ↓
FAISS / Policy RAG
      ↓
Relevant policy
      ↓
LLM response


## Test calculation/tool usage

Ask:
If I have 14 EL and want to take 5 days, how much will remain?
This should demonstrate the deterministic calculation tool.

Expected result:
9 days remaining
This is useful in your video because you can explain:
"The agent does not rely only on the LLM for arithmetic or business calculations. We expose deterministic tools for calculations."

## Test conversation memory

Ask:
How much EL do I have?
Then:
What if I use 5 days?
The second question is deliberately dependent on the first.
The system should maintain the conversation context.

This demonstrates:
Conversation
     ↓
ConversationMemory
     ↓
Database
     ↓
Previous messages
     ↓
LangGraph

## Verify audit trace

After asking a tool-based question, you can inspect the audit table.
Run:
python -c "from app.database import SessionLocal; from app.models import AgentAuditLog; db=SessionLocal(); rows=db.query(AgentAuditLog).order_by(AgentAuditLog.id.desc()).limit(10).all(); [print(r.event_type, r.tool_name, r.status, r.employee_id, r.conversation_id, r.correlation_id, r.duration_ms) for r in rows]; db.close()"

You should see events similar to:
AGENT_COMPLETED None SUCCESS EMP1001 ...
TOOL_COMPLETED get_specific_leave_balance SUCCESS EMP1001 ...
TOOL_STARTED get_specific_leave_balance STARTED EMP1001 ...
AGENT_STARTED None STARTED EMP1001 ...

## Final application architecture while running

At this point you should have:
                 ┌─────────────────────┐
                 │     Streamlit       │
                 │   localhost:8501    │
                 └──────────┬──────────┘
                            │
                            │ HTTP + JWT
                            ▼
                 ┌─────────────────────┐
                 │      FastAPI        │
                 │   localhost:8000    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    HRChatService    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     LangGraph       │
                 │       Agent         │
                 └─────┬─────┬─────┬───┘
                       │     │     │
              ┌────────┘     │     └─────────┐
              ▼              ▼               ▼
         Policy RAG     Leave Tools     Employee Tools
              │              │               │
              ▼              ▼               ▼
            FAISS          SQLite          SQLite
                             
                       + Audit Logs
                       + Conversation Memory
                             
                       Ollama LLM
                       llama3.2:3b

## Three-terminal setup for the demo

recommend keeping the terminals like this:

Terminal 1 — Ollama
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve

Terminal 2 — FastAPI
cd C:\Users\rameshsrinivasan\DataScience\Projects\HRChatAgent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

Terminal 3 — Streamlit
cd C:\Users\rameshsrinivasan\DataScience\Projects\HRChatAgent
.\.venv\Scripts\Activate.ps1
python -m streamlit run frontend\streamlit_app.py

Database seeding is done before these services:
python scripts_seed.py

The complete demo startup checklist
For your video, this is the sequence I'd follow:
1. Open project
       ↓
2. Activate .venv
       ↓
3. Seed database
       ↓
4. Verify/create DB schema
       ↓
5. Start Ollama
       ↓
6. Start FastAPI
       ↓
7. Test /health
       ↓
8. Test JWT login
       ↓
9. Start Streamlit
       ↓
10. Login as EMP1001
       ↓
11. Ask dynamic leave question
       ↓
12. Ask policy/RAG question
       ↓
13. Ask calculation question
       ↓
14. Demonstrate conversation memory
       ↓
15. Show audit trace
       ↓
16. Logout
