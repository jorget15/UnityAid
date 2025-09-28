# app.py — UnityAid MVP (single file)
import asyncio, uuid, math, json
from collections import deque
from contextlib import asynccontextmanager
from typing import Optional, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, RedirectResponse
from pydantic import BaseModel, Field

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    seed_resources()
    task = asyncio.create_task(loop_agent())
    yield
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# ---------- FastAPI app (single instance!) ----------
app = FastAPI(title="UnityAid", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"])
app.mount("/static", StaticFiles(directory=".", html=True), name="static")  # serve static files under /static

# ---------- Models ----------
Category = Literal["food","water","medical","shelter","other"]

class ReportIn(BaseModel):
    description: str = Field(..., example="Elderly person needs insulin")
    lat: float = Field(..., example=25.7617)
    lon: float = Field(..., example=-80.1918)
    urgency: int = Field(2, ge=1, le=5)

class Report(ReportIn):
    id: str
    category: Category
    matched_resource_id: Optional[str] = None

class Resource(BaseModel):
    id: str
    name: str
    type: Category
    lat: float
    lon: float
    capacity: int
    notes: Optional[str] = None

# ---------- In-memory state ----------
REPORTS: dict[str, Report] = {}
RESOURCES: dict[str, Resource] = {}
QUEUE: "deque[str]" = deque(maxlen=1000)
SUBSCRIBERS: list[asyncio.Queue] = []
A2A_SUBSCRIBERS: list[asyncio.Queue] = []


async def broadcast_event(event: dict) -> None:
    """Broadcast a JSON-serializable event to all connected SSE subscribers."""
    data = event
    # copy to avoid mutation issues
    for q in list(SUBSCRIBERS):
        try:
            await q.put(data)
        except Exception:
            # ignore subscriber errors
            pass


async def a2a_broadcast(message: dict) -> None:
  """Broadcast a JSON-serializable A2A message to all connected A2A SSE subscribers."""
  for q in list(A2A_SUBSCRIBERS):
    try:
      await q.put(message)
    except Exception:
      pass

def seed_resources():
    for r in [
        Resource(id="rc1", name="NGO Food Hub",        type="food",    lat=25.775, lon=-80.20, capacity=150),
        Resource(id="rc2", name="Water Station North",  type="water",   lat=25.810, lon=-80.19, capacity=300),
        Resource(id="rc3", name="Shelter @ HighSchool", type="shelter", lat=25.740, lon=-80.22, capacity=120),
        Resource(id="rc4", name="Pop-up Clinic",        type="medical", lat=25.770, lon=-80.18, capacity=40, notes="Basic meds"),
    ]:
        RESOURCES[r.id] = r

# ---------- Parallel steps ----------
KEYWORDS = {
    "medical":["insulin","injury","bleeding","medicine","asthma","diabetes","clinic","doctor"],
    "water":  ["water","thirst","dehydrated","bottles"],
    "food":   ["food","hungry","meal","grocery","hunger"],
    "shelter":["shelter","roof","evacuate","evacuation","homeless"],
}
def categorize(text: str) -> Category:
    t=text.lower()
    for cat, words in KEYWORDS.items():
        if any(w in t for w in words): return cat  # type: ignore
    return "other"

def haversine(a, b, c, d):
    R=6371; p1, p2 = math.radians(a), math.radians(c)
    dphi = math.radians(c-a); dl = math.radians(d-b)
    h = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

def match_resource(rep: Report) -> Optional[Resource]:
    cand = [r for r in RESOURCES.values() if r.capacity>0 and (r.type==rep.category or rep.category=="other")]
    if not cand: cand = [r for r in RESOURCES.values() if r.capacity>0]
    if not cand: return None
    return min(cand, key=lambda r: haversine(rep.lat, rep.lon, r.lat, r.lon))

def build_geojson() -> dict:
    feats=[]
    for rep in REPORTS.values():
        feats.append({"type":"Feature","geometry":{"type":"Point","coordinates":[rep.lon,rep.lat]},
            "properties":{"id":rep.id,"kind":"report","category":rep.category,"urgency":rep.urgency,
                          "matched_resource":rep.matched_resource_id,"description":rep.description}})
    for res in RESOURCES.values():
        feats.append({"type":"Feature","geometry":{"type":"Point","coordinates":[res.lon,res.lat]},
            "properties":{"id":res.id,"kind":"resource","category":res.type,"capacity":res.capacity,
                          "name":res.name,"notes":res.notes}})
    return {"type":"FeatureCollection","features":feats}

# ---------- Loop agent ----------
async def loop_agent(poll: float = 0.5):
  while True:
    if QUEUE:
      rid = QUEUE.popleft()
      rep = REPORTS.get(rid)
      if rep:
        rep.category = categorize(rep.description)
        res = match_resource(rep)
        if res:
          rep.matched_resource_id = res.id
          res.capacity = max(res.capacity - 1, 0)
          # publish match event
          try:
            asyncio.create_task(
              broadcast_event(
                {
                  "type": "match",
                  "report_id": rep.id,
                  "resource_id": res.id,
                  "capacity": res.capacity,
                }
              )
            )
          except Exception:
            pass
    await asyncio.sleep(poll)

def enqueue(data: ReportIn) -> Report:
  rid = str(uuid.uuid4())[:8]
  rep = Report(id=rid, **data.model_dump(), category="other", matched_resource_id=None)
  REPORTS[rid] = rep
  QUEUE.append(rid)
  # publish report event to SSE subscribers (fire-and-forget)
  try:
    asyncio.create_task(broadcast_event({"type": "report", "report": rep.model_dump()}))
  except Exception:
    pass
  # publish A2A ReportCreated so other agents can pick it up
  try:
    asyncio.create_task(a2a_broadcast({"type": "ReportCreated", "report": rep.model_dump()}))
  except Exception:
    pass
  return rep


@app.get("/stream")
@app.get("/api/stream")
def stream():
    """Server-Sent Events stream endpoint. Clients receive JSON events."""

    async def event_generator():
        q: asyncio.Queue = asyncio.Queue()
        SUBSCRIBERS.append(q)
        try:
            while True:
                data = await q.get()
                payload = json.dumps(data, default=str)
                yield f"data: {payload}\n\n"
        except asyncio.CancelledError:
            return
        finally:
            try:
                SUBSCRIBERS.remove(q)
            except ValueError:
                pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post('/a2a/send')
async def a2a_send(payload: dict):
  """Accept an A2A message and broadcast it to subscribers. If the message is a ResourceMatched event, apply it to state."""
  # Broadcast to A2A subscribers
  try:
    await a2a_broadcast(payload)
  except Exception:
    pass

  # Handle certain event types locally
  typ = payload.get('type')
  if typ == 'ResourceMatched':
    body = payload.get('body') or payload.get('resource_match') or payload
    # expected keys: report_id, resource_id
    rid = body.get('report_id')
    rcid = body.get('resource_id')
    if rid and rcid:
      rep = REPORTS.get(rid)
      res = RESOURCES.get(rcid)
      if rep and res and res.capacity>0:
        rep.matched_resource_id = res.id
        res.capacity = max(res.capacity-1, 0)
        # broadcast map update
        try:
          asyncio.create_task(broadcast_event({"type":"match","report_id":rid,"resource_id":res.id,"capacity":res.capacity}))
        except Exception:
          pass
  return {"ok": True}


@app.get('/a2a/subscribe')
def a2a_subscribe():
  async def gen():
    q: asyncio.Queue = asyncio.Queue()
    A2A_SUBSCRIBERS.append(q)
    try:
      while True:
        msg = await q.get()
        payload = json.dumps(msg, default=str)
        yield f"data: {payload}\n\n"
    except asyncio.CancelledError:
      return
    finally:
      try:
        A2A_SUBSCRIBERS.remove(q)
      except ValueError:
        pass

  return StreamingResponse(gen(), media_type='text/event-stream')

# ---------- API routes ----------
@app.get("/")
def root():
  """Redirect root to the UI dashboard."""
  return RedirectResponse(url="/ui/dashboard")

@app.get("/health")
@app.get("/api/health")
def health(): return {"ok": True, "reports": len(REPORTS), "resources": len(RESOURCES)}

@app.post("/report", response_model=Report)
@app.post("/api/report", response_model=Report)
def post_report(payload: ReportIn): return enqueue(payload)

@app.get("/reports", response_model=list[Report])
@app.get("/api/reports", response_model=list[Report])
def list_reports(): return list(REPORTS.values())

@app.get("/resources", response_model=list[Resource])
@app.get("/api/resources", response_model=list[Resource])
def list_resources(): return list(RESOURCES.values())

@app.get("/map.geojson")
@app.get("/api/map.geojson")
def map_geojson(): return build_geojson()

# ---------- Inline form page (no filesystem dependency) ----------
FORM_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>UnityAid — Submit Report</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto; background:#0f172a; color:#e2e8f0; display:flex; align-items:center; justify-content:center; height:100vh; margin:0}
    .card{background:#111827; padding:28px; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,.4); width:420px}
    h1{margin:0 0 12px; font-size:22px}
    label{font-size:14px; color:#94a3b8}
    input,select,button{width:100%; padding:12px 14px; border-radius:12px; border:1px solid #334155; background:#0b1220; color:#e2e8f0; margin-top:6px; outline:none}
    input:focus,select:focus{border-color:#60a5fa}
    button{background:#2563eb; border:none; margin-top:16px; font-weight:600; cursor:pointer}
    button:hover{filter:brightness(1.1)}
    .row{display:flex; gap:12px}
    .row .col{flex:1}
    .ok{color:#22c55e; margin-top:10px; display:none}
    .err{color:#ef4444; margin-top:10px; display:none}
  </style>
</head>
<body>
  <div class="card">
    <h1>Submit Disaster Report</h1>
    <form id="f">
      <label>Description</label>
      <input id="desc" placeholder="Injured person needs insulin"/>
      <div class="row">
        <div class="col"><label>Latitude</label><input id="lat" type="number" step="any" value="25.77"/></div>
        <div class="col"><label>Longitude</label><input id="lon" type="number" step="any" value="-80.19"/></div>
      </div>
      <label>Urgency</label>
      <select id="urg">
        <option value="5">5 - Critical</option>
        <option value="4" selected>4 - High</option>
        <option value="3">3 - Medium</option>
        <option value="2">2 - Low</option>
        <option value="1">1 - Minimal</option>
      </select>
      <button type="submit">Submit Report</button>
      <div class="ok" id="ok">✅ Report submitted!</div>
      <div class="err" id="err">❌ Failed to submit.</div>
    </form>
  </div>
<script>
const F=document.getElementById('f'), ok=document.getElementById('ok'), err=document.getElementById('err');
F.addEventListener('submit', async (e)=>{
  e.preventDefault(); ok.style.display='none'; err.style.display='none';
  const payload={description:desc.value, lat:parseFloat(lat.value), lon:parseFloat(lon.value), urgency:parseInt(urg.value)};
  try{
    const r=await fetch('/api/report',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    if(!r.ok) throw new Error();
    ok.style.display='block'; F.reset(); lat.value=25.77; lon.value=-80.19; urg.value=4;
  }catch{ err.style.display='block'; }
});
</script>
</body>
</html>
"""
@app.get("/ui/form", response_class=HTMLResponse)
def ui_form_inline():
    return HTMLResponse(FORM_HTML)


@app.get("/ui/dashboard")
def ui_dashboard():
  """Serve the dashboard page (dashboard.html) at /ui/dashboard."""
  return FileResponse("dashboard.html")
