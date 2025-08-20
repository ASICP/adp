#!/usr/bin/env python3
"""
app.py — ADP Demo Application
Demonstrates Alignment Delegation Protocol (ADP) for three focused domains:
  • Neurology
  • AI Compliance
  • AI Safety

Supports both interactive web UI and console-driven scenarios.
Requires Python 3.7+.
"""

import asyncio
import json
import random
import threading
import time
import uuid

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional
import urllib.parse
import sys

# ----------------------
# Routing Logic & Models
# ----------------------

class NMStatus(Enum):
    HEALTHY     = "healthy"
    DEGRADED    = "degraded"
    UNAVAILABLE = "unavailable"

class Domain(Enum):
    MEDICAL       = "medical"
    CARDIO        = "cardio"
    CANCER        = "cancer"
    NEUROLOGY     = "neurology"
    AI_COMPLIANCE = "ai_compliance"

@dataclass
class NarrowModel:
    id: str
    domain: Domain
    endpoint: str
    capabilities: List[str]
    weight: float                 # 0.1–1.0
    status: NMStatus = NMStatus.HEALTHY
    response_time_avg: float = 500  # ms
    accuracy_score: float = 0.9     # 0.0–1.0
    last_health_check: float = 0
    current_load: int = 0
    max_concurrent: int = 10

@dataclass
class RoutingRequest:
    message_id: str
    domain: Domain
    priority: str = "normal"      # normal, high, urgent
    preferred_nm_id: Optional[str] = None
    require_validation: bool = True

class ADPRouter:
    """Core ADP routing: health checks, round‐robin, weighted selection, validation picks."""
    def __init__(self):
        self.nm_registry: Dict[str, NarrowModel] = {}
        self.domain_pools: Dict[Domain, List[str]] = {}
        self.round_robin_indices: Dict[Domain, int] = {}
        self.health_check_interval = 30.0   # seconds

    def register_nm(self, nm: NarrowModel):
        self.nm_registry[nm.id] = nm
        pool = self.domain_pools.setdefault(nm.domain, [])
        if nm.id not in pool:
            pool.append(nm.id)
            self.round_robin_indices[nm.domain] = 0

    def perform_health_check(self, nm_id: str) -> bool:
        nm = self.nm_registry.get(nm_id)
        if not nm:
            return False
        now = time.time()
        # Simulate random 95% uptime
        healthy = random.random() > 0.05
        if healthy and nm.current_load < nm.max_concurrent:
            nm.status = NMStatus.HEALTHY
        elif healthy:
            nm.status = NMStatus.DEGRADED
        else:
            nm.status = NMStatus.UNAVAILABLE
        nm.last_health_check = now
        return nm.status == NMStatus.HEALTHY

    def get_healthy_nms(self, domain: Domain) -> List[str]:
        ids = self.domain_pools.get(domain, [])
        healthy = []
        for nm_id in ids:
            nm = self.nm_registry[nm_id]
            if time.time() - nm.last_health_check > self.health_check_interval:
                self.perform_health_check(nm_id)
            if nm.status in (NMStatus.HEALTHY, NMStatus.DEGRADED):
                healthy.append(nm_id)
        return healthy

    def calculate_weighted_selection(self, candidates: List[str]) -> Optional[str]:
        weights = []
        for nm_id in candidates:
            nm = self.nm_registry[nm_id]
            w = nm.weight
            # faster avg → higher weight
            if nm.response_time_avg > 0:
                w *= min(1.0, 1000.0 / nm.response_time_avg)
            w *= nm.accuracy_score
            w *= max(0.1, 1 - nm.current_load / nm.max_concurrent)
            if nm.status == NMStatus.DEGRADED:
                w *= 0.5
            weights.append((nm_id, w))
        total = sum(w for _, w in weights)
        if total == 0:
            return random.choice(candidates)
        pick = random.uniform(0, total)
        cum = 0
        for nm_id, w in weights:
            cum += w
            if pick <= cum:
                return nm_id
        return weights[-1][0]

    def round_robin(self, candidates: List[str], domain: Domain) -> Optional[str]:
        idx = self.round_robin_indices.get(domain, 0)
        if not candidates:
            return None
        if idx >= len(candidates):
            idx = 0
        nm_id = candidates[idx]
        self.round_robin_indices[domain] = (idx + 1) % len(candidates)
        return nm_id

    def _select_validation(self, domain: Domain, exclude: List[str], max_validators=1) -> List[str]:
        pool = [nm for nm in self.get_healthy_nms(domain) if nm not in exclude]
        valids = []
        while pool and len(valids) < max_validators:
            sel = self.calculate_weighted_selection(pool)
            valids.append(sel)
            pool.remove(sel)
        return valids

    def route_request(self, req: RoutingRequest) -> Dict:
        available = self.get_healthy_nms(req.domain)
        if not available:
            return {
                "primary": None,
                "validation": [],
                "routing_method": "no_available_nms"
            }

        if req.priority == "urgent":
            primary = self.calculate_weighted_selection(available)
            method = "weighted_urgent"
        elif req.priority == "high":
            rr = self.round_robin(available, req.domain)
            primary = self.calculate_weighted_selection([rr])
            method = "hybrid_high"
        else:
            primary = self.round_robin(available, req.domain)
            method = "round_robin_normal"

        # bump load
        self.nm_registry[primary].current_load += 1

        validation = []
        if req.require_validation:
            validation = self._select_validation(req.domain, [primary], max_validators=1)
            for nm_id in validation:
                self.nm_registry[nm_id].current_load += 1

        return {
            "primary": primary,
            "validation": validation,
            "routing_method": method,
            "total_available": len(available)
        }

    def complete_request(self, nm_id: str):
        if nm_id in self.nm_registry:
            nm = self.nm_registry[nm_id]
            nm.current_load = max(0, nm.current_load - 1)

    def get_routing_stats(self) -> Dict:
        stats = {"total_nms": len(self.nm_registry),
                 "domains": {},
                 "overall_health": 0.0}
        healthy_count = 0
        for domain, pool in self.domain_pools.items():
            h = sum(1 for nm_id in pool if self.nm_registry[nm_id].status == NMStatus.HEALTHY)
            stats["domains"][domain.value] = {
                "total": len(pool),
                "healthy": h,
                "degraded": sum(1 for nm_id in pool if self.nm_registry[nm_id].status == NMStatus.DEGRADED),
                "unavailable": sum(1 for nm_id in pool if self.nm_registry[nm_id].status == NMStatus.UNAVAILABLE)
            }
            healthy_count += h
        if self.nm_registry:
            stats["overall_health"] = healthy_count / len(self.nm_registry)
        return stats

# ----------------------
# Messaging & Demo Logic
# ----------------------

class ADPMessageType(Enum):
    DELEGATION_REQUEST  = "delegation_request"
    DELEGATION_RESPONSE = "delegation_response"
    CA_LOG_ENTRY        = "ca_log_entry"
    ALIGNMENT_FLAG      = "alignment_flag"

@dataclass
class ADPMessage:
    message_type: str
    adp_header: Dict
    payload: Dict
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)

class MockNarrowModel:
    """Simulate a specialized NM for demo."""
    def __init__(self, cfg: NarrowModel):
        self.config = cfg
        self.specializations = {
            "med-neurology-01": "neurology and brain disorders",
            "ai-compliance-01":   "AI compliance & regulatory frameworks",
            "ai-safety-01":       "AI safety, robustness, adversarial defenses"
        }

    async def process_request(self, req: ADPMessage) -> ADPMessage:
        # simulate latency
        await asyncio.sleep(self.config.response_time_avg / 1000.0)

        query = req.payload.get("original_query", "")
        spec = self.specializations.get(self.config.id, "general analysis")
        conf = max(0.1, min(1.0, self.config.accuracy_score + random.uniform(-0.1, 0.05)))

        content = (
            f"Based on specialization in {spec}:\n\n"
            f"Query: {query}\n\n"
            f"Analysis: {self._domain_response(query)}\n\n"
            f"Confidence: {conf:.2f}\n"
            f"Recommendations: {self._recommendations()}\n"
        )

        flags = self._check_alignment(query)
        msg = ADPMessage(
            message_type=ADPMessageType.DELEGATION_RESPONSE.value,
            adp_header={
                "protocol_version": "1.0",
                "message_id": str(uuid.uuid4()),
                "response_to": req.adp_header["message_id"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": {
                    "type": "narrow_model",
                    "id": self.config.id,
                    "domain": self.config.domain.value
                },
                "destination": req.adp_header["source"]
            },
            payload={
                "response_content": content,
                "confidence_metrics": {
                    "overall_confidence": conf,
                    "domain_match": 0.95,
                    "factual_confidence": conf * 0.9
                },
                "alignment_assessment": flags,
                "metadata": {
                    "processing_time_ms": int(self.config.response_time_avg),
                    "tokens_used": len(content.split()),
                    "human_review_recommended": flags["safety_check"] != "passed"
                }
            }
        )
        return msg

    def _domain_response(self, q: str) -> str:
        responses = {
            "cancer":        "Suggest MRI follow-up; consult specialst.",
            "neurology":     "Suggest MRI follow-up; consult neurologist.",
            "ai_compliance": "Review HIPAA & NIST AI RMF clauses.",
            "medical":     "Check adversarial robustness; apply safety guardrails."
        }
        return responses.get(self.config.domain.value, "Standard protocol response.")

    def _recommendations(self) -> str:
        return f"Follow best practices for {self.config.domain.value}."

    def _check_alignment(self, q: str) -> Dict:
        flags = {"safety_check": "passed", "bias_evaluation": "low", 
                 "hallucination_risk": "low", "harm_potential": "none"}
        if "harm" in q.lower():
            flags["safety_check"] = "flagged"
            flags["harm_potential"] = "moderate"
        return flags

class ADPMasterController:
    """Master controller for delegating and aggregating NM responses."""
    def __init__(self, mc_id: str):
        self.mc_id = mc_id
        self.router = ADPRouter()
        self.mock_nms: Dict[str, MockNarrowModel] = {}
        self.ca_logs: List[ADPMessage] = []
        self._setup()

    def _setup(self):
        # Register exactly three focused NMs
        configs = [
            NarrowModel("med-neurology-01", Domain.NEUROLOGY,     "http://localhost:8011",
                        ["brain_imaging","clinical_eval"], 0.9, 700, 0.94),
            NarrowModel("ai-compliance-01",   Domain.AI_COMPLIANCE, "http://localhost:8012",
                        ["regulations","ethics"],        0.85,800, 0.92),
            NarrowModel("ai-safety-01",       Domain.AI_SAFETY,     "http://localhost:8013",
                        ["robustness","adversarial"],    0.9, 750, 0.95),
        ]
        for cfg in configs:
            self.router.register_nm(cfg)
            self.mock_nms[cfg.id] = MockNarrowModel(cfg)

    async def process_user_query(self, query: str, domain: str, priority: str) -> Dict:
        try:
            dom = Domain(domain)
        except ValueError:
            dom = Domain.NEUROLOGY
        req = RoutingRequest(str(uuid.uuid4()), dom, priority, require_validation=True)
        route = self.router.route_request(req)
        # build ADPMessage request
        msg_req = ADPMessage(
            message_type=ADPMessageType.DELEGATION_REQUEST.value,
            adp_header={
                "protocol_version": "1.0",
                "message_id": req.message_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": {"type":"master_controller","id":self.mc_id},
                "destination": {"type":"narrow_model","domain":dom.value}
            },
            payload={"original_query": query}
        )
        # primary
        primary_id = route["primary"]
        primary_resp = await self.mock_nms[primary_id].process_request(msg_req)
        # validation
        val_resps = []
        for vid in route["validation"]:
            val_resps.append(await self.mock_nms[vid].process_request(msg_req))

        # log to CA (simplified)
        self.ca_logs.append(primary_resp)

        # complete
        self.router.complete_request(primary_id)
        for vid in route["validation"]:
            self.router.complete_request(vid)

        return {
            "routing": route,
            "primary_response": json.loads(primary_resp.to_json()),
            "validation_responses":[json.loads(v.to_json()) for v in val_resps]
        }

    def get_system_status(self) -> Dict:
        stats = self.router.get_routing_stats()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "master_controller": self.mc_id,
            "routing_stats": stats,
            "ca_logs": len(self.ca_logs),
            "system_health": "🟢 HEALTHY" if stats["overall_health"]>0.8 else "🟡 DEGRADED"
        }

# ----------------------
# Web Server Demo
# ----------------------

class ADPDemoWebServer:
    def __init__(self, mc: ADPMasterController, port:int=8000):
        self.mc = mc
        self.port = port

    def start(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    return self._serve_form()
                if self.path.startswith("/status"):
                    return self._serve_status()
                if self.path.startswith("/query"):
                    return self._serve_query()
                self.send_error(404)

            def _serve_form(self):
                html = f"""<!DOCTYPE html>
<html><head><title>ADP Demo</title></head>
<body>
  <h1>ADP Focused Demo</h1>
  <form action="/query" method="get">
    <input name="q" required placeholder="Enter query…"/><br/>
    <select name="domain">
      <option value="neurology">Neurology</option>
      <option value="ai_compliance">AI Compliance</option>
      <option value="ai_safety">AI Safety</option>
    </select><br/>
    <select name="priority">
      <option>normal</option><option>high</option><option>urgent</option>
    </select><br/>
    <button type="submit">Delegate</button>
  </form>
  <button onclick="loadStatus()">Refresh Status</button>
  <pre id="status"></pre>
  <script>
    function loadStatus(){fetch('/status').then(r=>r.json()).then(j=>document.getElementById('status').innerText=JSON.stringify(j,null,2))}
  </script>
</body>
</html>"""
                self.send_response(200)
                self.send_header("Content-Type","text/html")
                self.end_headers()
                self.wfile.write(html.encode())

            def _serve_status(self):
                st = self.server.mc.get_system_status()
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.end_headers()
                self.wfile.write(json.dumps(st,indent=2).encode())

            def _serve_query(self):
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                q       = qs.get("q",[""])[0]
                domain  = qs.get("domain",["neurology"])[0]
                priority= qs.get("priority",["normal"])[0]
                if not q:
                    self.send_error(400,"Missing query")
                    return
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.server.mc.process_user_query(q,domain,priority))
                loop.close()

                html = f"<html><body><h1>Result</h1><pre>{json.dumps(result,indent=2)}</pre><a href='/'>Back</a></body></html>"
                self.send_response(200)
                self.send_header("Content-Type","text/html")
                self.end_headers()
                self.wfile.write(html.encode())

        # attach mc to server
        httpd = HTTPServer(("localhost", self.port), Handler)
        httpd.mc = self.mc
        print(f"🚀 Web demo running at http://localhost:{self.port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("🛑 Stopped web demo")

# ----------------------
# Console Demo
# ----------------------

async def run_console_demo(mc: ADPMasterController):
    print("🚀 Console Demo Starting\n")
    queries = [
        ("Assess early signs of Parkinson’s disease?", "neurology", "high"),
        ("Check compliance of AI hiring tool under GDPR", "ai_compliance", "urgent"),
        ("Evaluate model robustness against adversarial inputs", "ai_safety", "high")
    ]
    for q, d, p in queries:
        print(f">>> Query: {q} [{d}, {p}]")
        res = await mc.process_user_query(q,d,p)
        print(json.dumps(res, indent=2), "\n")
    print("✅ Console demo complete")
    print("System status:", json.dumps(mc.get_system_status(),indent=2))

# ----------------------
# Main Entry
# ----------------------

def main():
    print("ADP Demo Launcher")
    print("1) Web Server Demo")
    print("2) Console Demo")
    print("3) Status Only")
    choice = input("Choose (1-3): ").strip()

    mc = ADPMasterController("demo-mc-001")

    if choice == "1":
        ADPDemoWebServer(mc, port=8000).start()
    elif choice == "2":
        asyncio.run(run_console_demo(mc))
    elif choice == "3":
        print(json.dumps(mc.get_system_status(), indent=2))
    else:
        print("Invalid choice, exiting.")

if __name__ == "__main__":
    main()
