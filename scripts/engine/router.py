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
RESULTS = {
    "draft": {"candidate": ("text",), "need": ("question", "consequence")},
    "resolve": {"resolved": ("text", "basis"), "blocked": ("question", "needs")},
    "review": {"pass": ("basis",), "revise": ("feedback",),
               "need": ("question", "consequence")},
}
FIELDS = {"schema_version", "run_id", "status", "prompt", "ticket", "request",
          "candidate", "basis", "need", "feedback", "blocker", "review", "artifact"}


def new(request):
    require(text(request), "--request must be nonempty text")
    return {"schema_version": 1, "run_id": uuid.uuid4().hex,
            "status": "active", "prompt": "draft", "ticket": uuid.uuid4().hex,
            "request": request, "candidate": "", "basis": "", "need": None,
            "feedback": "", "blocker": None, "review": "", "artifact": ""}


def artifact_path(document):
    return f".agents/artifacts/solution-design-{document['run_id']}.md"


def validate(document):
    require(isinstance(document, dict) and set(document) == FIELDS, "invalid checkpoint fields")
    require(type(document["schema_version"]) is int and document["schema_version"] == 1,
            "unsupported checkpoint schema")
    for key in ("run_id", "ticket"):
        require(isinstance(document[key], str) and re.fullmatch(r"[0-9a-f]{32}", document[key]),
                f"invalid checkpoint {key}")
    require(text(document["request"]), "invalid checkpoint request")
    for key in ("candidate", "basis", "feedback", "review", "artifact"):
        require(isinstance(document[key], str) and "\x00" not in document[key],
                f"invalid checkpoint {key}")
    require(document["status"] in ("active", "blocked", "publishing", "complete"),
            "invalid checkpoint status")
    require(isinstance(document["prompt"], str) and document["prompt"] in RESULTS,
            "invalid checkpoint prompt")
    for key, fields in (("need", {"question", "consequence"}),
                        ("blocker", {"question", "needs"})):
        item = document[key]
        require(item is None or (isinstance(item, dict) and set(item) == fields
                                and all(text(v) for v in item.values())),
                f"invalid checkpoint {key}")
    require((document["prompt"] == "resolve") == (document["need"] is not None),
            "checkpoint need/prompt mismatch")
    require((document["status"] == "blocked") == (document["blocker"] is not None),
            "checkpoint blocker/status mismatch")
    require(document["status"] != "blocked" or document["prompt"] == "resolve",
            "only a resolver can be blocked")
    if document["prompt"] == "review":
        require(text(document["candidate"]), "review requires a candidate")
    if document["status"] in ("publishing", "complete"):
        require(document["prompt"] == "review" and text(document["review"]),
                "completion requires current review")
        require(document["artifact"] == artifact_path(document), "invalid artifact path")
    else:
        require(not document["artifact"] and not document["review"],
                "active checkpoint cannot contain completion")
    return document


def validate_result(prompt, result):
    require(isinstance(result, dict), "result must be a JSON object")
    status = result.get("status")
    require(isinstance(status, str) and status in RESULTS[prompt],
            f"{prompt} status must be {' | '.join(RESULTS[prompt])}")
    fields = RESULTS[prompt][status]
    require(set(result) == {"status", *fields}
            and all(text(result[key]) for key in fields),
            f"{status} requires only status and nonempty {', '.join(fields)}")
    return status


def advance(document, result):
    validate(document)
    require(document["status"] in ("active", "blocked"), "run is not accepting results")
    status = validate_result(document["prompt"], result)
    updated = deepcopy(document)
    updated["status"] = "active"
    updated["blocker"] = None
    if status == "candidate":
        updated.update(candidate=result["text"], prompt="review")
    elif status == "need":
        updated.update(prompt="resolve", need={key: result[key] for key in ("question", "consequence")})
    elif status == "resolved":
        updated.update(prompt="draft", need=None,
                       basis=result["text"] + "\nBasis: " + result["basis"])
    elif status == "blocked":
        updated.update(status="blocked", blocker={key: result[key] for key in ("question", "needs")})
    elif status == "revise":
        updated.update(prompt="draft", feedback=result["feedback"])
    elif status == "pass":
        # Retain the final ticket until publication is durable, allowing exact replay.
        updated.update(status="publishing", review=result["basis"], artifact=artifact_path(document))
    if status != "pass":
        updated["ticket"] = uuid.uuid4().hex
    return validate(updated)
