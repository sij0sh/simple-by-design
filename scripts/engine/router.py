"""Fixed prompt transitions; no ledger or agent-selected next step."""

from copy import deepcopy
import re
import uuid


class DispatchError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise DispatchError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip()) and "\x00" not in value


# Required result fields, beside the transitions they support.
NEED = ("type", "question", "witness", "consequence")
RESULTS = {
    "draft": {"candidate": ("summary", "criteria", "decisions"), "need": NEED},
    "resolve": {"resolved": ("answer", "basis"), "blocked": ("question", "needs")},
    "review": {"pass": ("pair", "defeater", "decision", "basis"), "revise": ("gaps",),
               "need": NEED},
}
DECISION = ("id", "choice", "basis", "alternative", "tradeoff", "revisit")
GAP = ("check", "witness", "decision")
CHECKS = ("pair", "defeater", "decision")
TYPES = ("intent", "fact")
FIELDS = {"schema_version", "run_id", "status", "prompt", "ticket", "request",
          "candidate", "resolutions", "need", "feedback", "blocker", "review", "artifact"}


def record(value, keys, name):
    require(isinstance(value, dict) and set(value) == set(keys)
            and all(text(value[key]) for key in keys),
            f"{name} requires only nonempty {', '.join(keys)}")
    return value


def items(value, name, check, empty=False):
    require(isinstance(value, list) and (empty or value), f"{name} must be a{'' if empty else ' nonempty'} list")
    for item in value:
        check(item)
    return value


def decisions(value):
    items(value, "decisions", lambda item: record(item, DECISION, "decision"), empty=True)
    ids = [item["id"] for item in value]
    require(len(ids) == len(set(ids)), "decision ids must be unique")


def gap(value):
    record(value, GAP, "gap")
    require(value["check"] in CHECKS, f"gap check must be {' | '.join(CHECKS)}")


def need(value):
    record(value, NEED, "need")
    require(value["type"] in TYPES, f"need type must be {' | '.join(TYPES)}")


SHAPES = {
    "criteria": lambda value: items(value, "criteria", lambda item: require(text(item), "criteria must be nonempty text")),
    "decisions": decisions,
    "gaps": lambda value: items(value, "gaps", gap),
    "type": lambda value: require(value in TYPES, f"type must be {' | '.join(TYPES)}"),
}


def new(request):
    require(text(request), "--request must be nonempty text")
    return {"schema_version": 2, "run_id": uuid.uuid4().hex,
            "status": "active", "prompt": "draft", "ticket": uuid.uuid4().hex,
            "request": request, "candidate": None, "resolutions": [], "need": None,
            "feedback": [], "blocker": None, "review": None, "artifact": ""}


def artifact_path(document):
    return f".agents/artifacts/solution-design-{document['run_id']}.md"


def validate(document):
    require(isinstance(document, dict), "invalid checkpoint")
    require(document.get("schema_version") != 1,
            "legacy checkpoint (schema 1); move .agents/sbd-adaptive/run.json aside, then start with --request")
    require(set(document) == FIELDS, "invalid checkpoint fields")
    require(type(document["schema_version"]) is int and document["schema_version"] == 2,
            "unsupported checkpoint schema")
    for key in ("run_id", "ticket"):
        require(isinstance(document[key], str) and re.fullmatch(r"[0-9a-f]{32}", document[key]),
                f"invalid checkpoint {key}")
    require(text(document["request"]), "invalid checkpoint request")
    require(isinstance(document["artifact"], str) and "\x00" not in document["artifact"],
            "invalid checkpoint artifact")
    require(document["status"] in ("active", "blocked", "publishing", "complete"),
            "invalid checkpoint status")
    require(isinstance(document["prompt"], str) and document["prompt"] in RESULTS,
            "invalid checkpoint prompt")
    if document["candidate"] is not None:
        require(isinstance(document["candidate"], dict), "invalid checkpoint candidate")
        check_result("draft", {"status": "candidate", **document["candidate"]})
    items(document["resolutions"], "resolutions",
          lambda item: (record(item, ("type", "question", "answer", "basis"), "resolution"),
                        require(item["type"] in TYPES, "invalid resolution type")), empty=True)
    items(document["feedback"], "feedback", gap, empty=True)
    if document["need"] is not None:
        need(document["need"])
    if document["blocker"] is not None:
        record(document["blocker"], ("question", "needs"), "blocker")
    require((document["prompt"] == "resolve") == (document["need"] is not None),
            "checkpoint need/prompt mismatch")
    require((document["status"] == "blocked") == (document["blocker"] is not None),
            "checkpoint blocker/status mismatch")
    require(document["status"] != "blocked" or document["prompt"] == "resolve",
            "only a resolver can be blocked")
    if document["prompt"] == "review":
        require(document["candidate"] is not None, "review requires a candidate")
    if document["status"] in ("publishing", "complete"):
        require(document["prompt"] == "review" and isinstance(document["review"], dict),
                "completion requires current review")
        check_result("review", {"status": "pass", **document["review"]})
        require(document["artifact"] == artifact_path(document), "invalid artifact path")
    else:
        require(not document["artifact"] and document["review"] is None,
                "active checkpoint cannot contain completion")
    return document


def check_result(prompt, result):
    require(isinstance(result, dict), "result must be a JSON object")
    status = result.get("status")
    require(isinstance(status, str) and status in RESULTS[prompt],
            f"{prompt} status must be {' | '.join(RESULTS[prompt])}")
    fields = RESULTS[prompt][status]
    require(set(result) == {"status", *fields}, f"{status} requires only status and {', '.join(fields)}")
    for key in fields:
        if key in SHAPES:
            SHAPES[key](result[key])
        else:
            require(text(result[key]), f"{key} must be nonempty text")
    return status


def body(result):
    return {key: value for key, value in result.items() if key != "status"}


def advance(document, result):
    validate(document)
    require(document["status"] in ("active", "blocked"), "run is not accepting results")
    status = check_result(document["prompt"], result)
    result = deepcopy(result)  # Never alias caller-owned lists into the checkpoint.
    updated = deepcopy(document)
    updated["status"] = "active"
    updated["blocker"] = None
    if status == "candidate":
        updated.update(candidate=body(result), feedback=[], prompt="review")
    elif status == "need":
        updated.update(prompt="resolve", need=body(result))
    elif status == "resolved":
        updated["resolutions"] = updated["resolutions"] + [{
            "type": document["need"]["type"], "question": document["need"]["question"],
            "answer": result["answer"], "basis": result["basis"]}]
        updated.update(prompt="draft", need=None)
    elif status == "blocked":
        updated.update(status="blocked", blocker=body(result))
    elif status == "revise":
        updated.update(prompt="draft", feedback=result["gaps"])
    elif status == "pass":
        # Retain the final ticket until publication is durable, allowing exact replay.
        updated.update(status="publishing", review=body(result), artifact=artifact_path(document))
    if status != "pass":
        updated["ticket"] = uuid.uuid4().hex
    return validate(updated)
