"""Pure, replay-validated question/evidence ledger. No scheduling or tool execution."""

from copy import deepcopy
from datetime import datetime, timezone
import re

SCHEMA_VERSION = 1
ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
RESOLVERS = {"intent": "requester", "fact": "observation", "choice": "policy"}
POLICIES = {"requirements", "decisions", "conventions", "defaults", "contract",
            "language", "instructions", "simplest"}
REVIEW_SCOPE = {"request", "constraints", "permissions", "evidence", "decisions",
                "questions", "design", "checks"}


class LedgerError(ValueError):
    """Invalid input, history, or state transition; nothing should be persisted."""


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value),
            "ID must be 1–64 lowercase letters/digits/underscores/hyphens, starting alphanumeric")
    return value


def obj(value, required, optional=()):
    require(isinstance(value, dict), "expected an object")
    require(all(isinstance(key, str) for key in value), "object keys must be strings")
    require(set(required) <= value.keys(), f"missing fields: {sorted(set(required) - value.keys())}")
    require(value.keys() <= set(required) | set(optional),
            f"unknown fields: {sorted(value.keys() - set(required) - set(optional))}")


def text(value):
    require(isinstance(value, str) and bool(value.strip()), "expected nonempty text")


def boolean(value):
    require(type(value) is bool, "expected a boolean")


def strings(value, nonempty=False):
    require(isinstance(value, list), "expected a list")
    require(not nonempty or bool(value), "list must not be empty")
    for item in value:
        text(item)
    require(len(value) == len(set(value)), "duplicate list entries")


def evidence(value):
    obj(value, {"kind", "authority", "source", "claim"})
    text(value["source"])
    text(value["claim"])
    allowed = {"observed": {"observation", "requester"},
               "documented": {"project", "requester"},
               "inferred": {"inference"}, "unknown": {"unknown"}}
    require(isinstance(value["kind"], str) and value["kind"] in allowed, "invalid evidence kind")
    require(isinstance(value["authority"], str) and value["authority"] in allowed[value["kind"]],
            "evidence kind/authority mismatch")


def witness(value, criteria):
    require(isinstance(value, dict), "witness must be an object")
    form = value.get("form")
    fields = {"pair": {"a", "b", "difference"},
              "defeater": {"claim", "condition", "impact"},
              "check": {"criterion", "failure"}}
    require(isinstance(form, str) and form in fields, "witness must be pair, defeater, or check")
    obj(value, fields[form] | {"form"})
    for key in fields[form]:
        text(value[key])
    if form == "pair":
        require(value["a"] != value["b"], "pair outcomes must differ")
    if form == "check":
        require(value["criterion"] in criteria, "unknown acceptance criterion")


def _task(data):
    obj(data, {"type", "request", "constraints", "permissions", "criteria", "independent_review"})
    require(data["type"] == "task", "first event must create the task")
    text(data["request"])
    strings(data["constraints"])
    strings(data["permissions"])
    boolean(data["independent_review"])
    require(isinstance(data["criteria"], list) and data["criteria"], "at least one design criterion required")
    seen = set()
    for criterion in data["criteria"]:
        obj(criterion, {"id", "text"})
        identifier(criterion["id"])
        text(criterion["text"])
        require(criterion["id"] not in seen, "duplicate criterion ID")
        seen.add(criterion["id"])


def _refs(view, ids, usable=True):
    strings(ids)
    records = []
    for key in ids:
        identifier(key)
        require(key in view["records"], f"unknown reference: {key}; forward/self references forbidden")
        record = view["records"][key]
        require(record["valid"], f"invalidated reference: {key}")
        if usable and record["type"] == "question":
            require(record["status"] in {"resolved", "provisional"}, f"unanswered dependency: {key}")
        records.append(record)
    return records


def _evidence_refs(view, ids):
    require(isinstance(ids, list) and ids, "evidence must not be empty")
    records = _refs(view, ids)
    require(all(r["type"] == "evidence" for r in records), "expected evidence record references")
    return records


def _invalidate(view, targets):
    """A resolution's invalidation also reopens its question and all dependents."""
    affected = set(targets)
    while True:
        before = len(affected)
        for key, record in view["records"].items():
            if not record["valid"]:
                continue
            if affected.intersection(record["depends_on"]):
                affected.add(key)
            if key in affected and record["type"] in {"answer", "defer"}:
                affected.add(record["question"])
        if len(affected) == before:
            break
    for key in affected:
        record = view["records"][key]
        if record["type"] == "question":
            record.update(status="open", resolution=None)
        else:
            record["valid"] = False
    if view["design"] in affected:
        view["design"] = None
    view["checks"] = {c: key for c, key in view["checks"].items() if key not in affected}
    view["completion"] = None


def _review(view, data):
    obj(data, {"revision", "reviewer", "independent", "reviewed", "findings"})
    require(type(data["revision"]) is int and data["revision"] == view["revision"], "stale evaluation revision")
    text(data["reviewer"])
    boolean(data["independent"])
    strings(data["reviewed"])
    require(set(data["reviewed"]) == REVIEW_SCOPE, "review must cover request, authority, evidence, design and checks")
    findings = _refs(view, data["findings"], usable=False)
    require(all(r["type"] == "question" for r in findings), "findings must name recorded questions")


def _finish(view, evaluation):
    _review(view, evaluation)
    require(view["status"] == "active", "task is not active")
    require(not evaluation["findings"], "evaluation still has findings")
    require(not view["task"]["independent_review"] or evaluation["independent"], "independent review required")
    require(view["design"] is not None, "candidate design required")
    for record in view["records"].values():
        if record["type"] == "question":
            require(record["status"] != "open", f"unresolved question: {record['id']}")
            require(not record["required"] or record["status"] != "deferred", "required question cannot be deferred")
    for criterion in view["task"]["criteria"]:
        check = view["records"].get(view["checks"].get(criterion["id"]))
        require(check is not None and check["valid"] and check["result"] == "passed",
                f"unsupported design criterion: {criterion['id']}")
    view["completion"] = {"revision": view["revision"] + 1, "certifies": view["revision"],
                          "evaluation": deepcopy(evaluation)}
    view["status"] = "complete"


def _record(view, data):
    require(isinstance(data, dict), "record must be an object")
    kind = data.get("type")
    required = {
        "evidence": {"kind", "authority", "source", "claim"},
        "question": {"text", "kind", "resolver", "witness", "consequence", "required", "next"},
        "answer": {"question", "text", "resolver", "evidence", "mode"},
        "defer": {"question", "boundary", "owner", "reason", "trigger", "evidence"},
        "design": {"text", "verification"},
        "check": {"criterion", "design", "result", "evidence", "explanation"},
        "reopen": {"targets", "trigger", "cause"},
        "pause": {"reason", "needs"},
        "evaluation": {"revision", "reviewer", "independent", "reviewed", "findings"},
    }
    require(isinstance(kind, str) and kind in required, "unknown record type")
    optional = {"depends_on"}
    if kind == "answer":
        optional |= {"policy", "alternatives", "rationale", "tradeoff", "revisit", "reversal", "detect"}
    obj(data, required[kind] | {"id", "type"}, optional)
    key = identifier(data["id"])
    require(key not in view["records"], "record IDs are immutable; choose a new ID")
    require(view["status"] != "complete" or kind == "reopen", "completed task requires explicit reopening")
    _refs(view, data.get("depends_on", []), usable=kind != "question")
    deps = set(data.get("depends_on", []))
    extra = {}

    if kind == "evidence":
        evidence({k: data[k] for k in required[kind]})
    elif kind == "question":
        require(isinstance(data["kind"], str) and data["kind"] in RESOLVERS, "invalid question type")
        require(data["resolver"] == RESOLVERS[data["kind"]], "wrong question resolver")
        for field in ("text", "consequence", "next"):
            text(data[field])
        boolean(data["required"])
        witness(data["witness"], {c["id"] for c in view["task"]["criteria"]})
        require(all(r["type"] == "question" for r in _refs(view, list(deps), usable=False)),
                "question dependencies must name earlier questions (DAG by construction)")
        extra.update(status="open", resolution=None)
    elif kind in {"answer", "defer"}:
        question = _refs(view, [data["question"]], usable=False)[0]
        require(question["type"] == "question", "resolution must name a question")
        if question["resolution"] is not None:
            _invalidate(view, [question["id"]])
        _refs(view, question["depends_on"])
        sources = _evidence_refs(view, data["evidence"])
        deps.update(data["evidence"] + [question["id"]])
        if kind == "defer":
            require(not question["required"], "required question cannot be deferred")
            for field in ("boundary", "owner", "reason", "trigger"):
                text(data[field])
            require(any(s["authority"] == "requester" for s in sources), "deferral needs requester-sourced scope boundary")
            status = "deferred"
        else:
            text(data["text"])
            require(data["resolver"] == question["resolver"], "wrong answer resolver")
            require(isinstance(data["mode"], str) and data["mode"] in {"established", "provisional"}, "invalid answer mode")
            qkind = question["kind"]
            if data["mode"] == "provisional":
                require(qkind != "intent", "intent cannot be assumed")
                for field in ("reversal", "detect", "revisit"):
                    text(data.get(field))
                require(any(s["kind"] == "inferred" for s in sources), "provisional answer needs explicit inferred evidence")
            elif qkind == "intent":
                require(all(s["authority"] == "requester" for s in sources), "intent requires requester evidence")
            elif qkind == "fact":
                require(all(s["kind"] == "observed" for s in sources),
                        "established fact requires observations, not inference")
            require(all(s["kind"] != "unknown" for s in sources), "unknown evidence cannot answer a question")
            for field in ("reversal", "detect", "revisit"):
                if field in data:
                    text(data[field])
            require(data["mode"] == "provisional" or not ({"reversal", "detect"} & data.keys()),
                    "reversal/detect only apply to provisional answers")
            if qkind == "choice":
                require(isinstance(data.get("policy"), str) and data["policy"] in POLICIES, "choice needs a policy level")
                for field in ("rationale", "tradeoff", "revisit"):
                    text(data.get(field))
                alternatives = data.get("alternatives")
                require(isinstance(alternatives, list) and alternatives, "choice needs rejected alternatives")
                for alternative in alternatives:
                    obj(alternative, {"option", "rejected_because"})
                    text(alternative["option"])
                    text(alternative["rejected_because"])
                if data["policy"] == "requirements":
                    require(any(s["authority"] == "requester" for s in sources), "requirements need requester evidence")
                elif data["policy"] != "simplest":
                    require(any(s["kind"] == "documented" and s["authority"] == "project" for s in sources),
                            "policy level needs documented project evidence")
            else:
                require(not ({"policy", "alternatives", "rationale", "tradeoff"} & data.keys()), "choice fields on non-choice answer")
            status = "provisional" if data["mode"] == "provisional" else "resolved"
        question.update(status=status, resolution=key)
    elif kind == "design":
        text(data["text"])
        text(data["verification"])
        if view["design"]:
            _invalidate(view, [view["design"]])
        view["design"] = key
        view["checks"] = {}
    elif kind == "check":
        identifier(data["criterion"])
        require(data["criterion"] in {c["id"] for c in view["task"]["criteria"]}, "unknown criterion")
        require(data["design"] == view["design"] and view["design"] is not None, "check must certify current design")
        require(isinstance(data["result"], str) and data["result"] in {"passed", "failed"}, "invalid check result")
        text(data["explanation"])
        sources = _evidence_refs(view, data["evidence"])
        require(all(s["kind"] != "unknown" for s in sources), "check cannot rely on unknown evidence")
        deps.update(data["evidence"] + [data["design"]])
        old = view["checks"].get(data["criterion"])
        if old:
            _invalidate(view, [old])
        view["checks"][data["criterion"]] = key
    elif kind == "reopen":
        targets = _refs(view, data["targets"], usable=False)
        require(bool(targets), "reopening needs affected records")
        require(all(r["type"] in {"evidence", "question", "answer", "defer", "design", "check"} for r in targets),
                "reopen must target evidence, questions, resolutions, designs or checks")
        require(isinstance(data["trigger"], str) and data["trigger"] in
                {"contradiction", "revisit", "uncheckable", "intent-choice"}, "invalid reopening trigger")
        evidence(data["cause"])
        require(data["cause"]["kind"] in {"observed", "documented"}, "reopening requires a cited observation or document")
        _invalidate(view, data["targets"])
    elif kind == "pause":
        text(data["reason"])
        text(data["needs"])
    elif kind == "evaluation":
        _review(view, {k: data[k] for k in required[kind]})
        deps.update(data["findings"])

    # Automatic replacement can invalidate a dependency supplied earlier in this event.
    _refs(view, sorted(deps), usable=kind not in {"question", "answer", "defer", "evaluation"})
    record = deepcopy(data)
    record.update(extra, valid=True, depends_on=sorted(deps))
    view["records"][key] = record
    view["status"] = "blocked" if kind == "pause" else "active"


def _apply(view, data):
    if isinstance(data, dict) and data.get("type") == "completion":
        obj(data, {"type", "evaluation"})
        _finish(view, data["evaluation"])
    else:
        _record(view, data)
    view["revision"] += 1


def project(document):
    """Replay all events, rejecting corrupted or invalid historical transitions."""
    obj(document, {"schema_version", "task_id", "events"})
    require(type(document["schema_version"]) is int and document["schema_version"] == SCHEMA_VERSION,
            "unsupported schema version")
    identifier(document["task_id"])
    events = document["events"]
    require(isinstance(events, list) and events, "empty history")
    view = None
    for revision, event in enumerate(events, 1):
        obj(event, {"revision", "time", "data"})
        require(type(event["revision"]) is int and event["revision"] == revision, "noncontiguous history revision")
        text(event["time"])
        try:
            stamp = datetime.fromisoformat(event["time"])
            require(stamp.tzinfo is not None, "event timestamp must include timezone")
        except ValueError as error:
            raise LedgerError("invalid event timestamp") from error
        if revision == 1:
            _task(event["data"])
            view = {"task_id": document["task_id"], "revision": 1, "status": "active",
                    "task": deepcopy(event["data"]), "records": {}, "design": None,
                    "checks": {}, "completion": None}
        else:
            _apply(view, event["data"])
    return view


def _event(revision, data):
    return {"revision": revision, "time": datetime.now(timezone.utc).isoformat(), "data": deepcopy(data)}


def create(task_id, task):
    identifier(task_id)
    obj(task, {"request", "constraints", "permissions", "criteria", "independent_review"})
    document = {"schema_version": SCHEMA_VERSION, "task_id": task_id,
                "events": [_event(1, {"type": "task", **task})]}
    project(document)
    return document


def append(document, data, at, finish=False):
    view = project(document)
    require(type(at) is int and at == view["revision"], f"stale revision: expected {at}, current {view['revision']}")
    require(finish or not (isinstance(data, dict) and data.get("type") in ("task", "completion")),
            "use new/finish for task creation/completion")
    event_data = {"type": "completion", "evaluation": data} if finish else data
    _apply(view, event_data)
    updated = deepcopy(document)
    updated["events"].append(_event(view["revision"], event_data))
    return updated
