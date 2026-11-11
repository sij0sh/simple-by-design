"""Small job-specific instructions and bounded current context."""

import json
import shlex

from .router import CHECKS, DECISION, RESULTS, TYPES

DRAFT = """Propose the simplest adequate solution design, not implementation. Inspect only as authorized; do not edit a report-only target. State checkable success criteria. Record each consequential choice as a decision: basis (citation, resolution, or "assumption: ..."), a serious alternative, tradeoff and revisit condition; ordinary reversible choices need none. On feedback, revise the named decisions and what depends on them; keep the rest. Return candidate, or need for one intent or fact gap whose answer could change the design."""

RESOLVE = """Settle this one gap within the request's authority. Intent: ask the requester; never pick. Fact: make the cheapest authorized observation; otherwise keep it an assumption with a revisit condition. Respect explicit deferrals; do not invent answers. Return resolved with the answer and its basis, or blocked with the question and who/what is needed; after asking, pause until answered."""

REVIEW = """Delegate this review to a subagent if available; otherwise proceed. Challenge the candidate by constructing counterexamples, not critique. Pair: two outcomes consistent with the request, resolutions and decisions that the requester or a criterion would treat differently. Defeater: a plausible, unrefuted condition under which a relied-on claim, decision or criterion fails; include criteria that pass while the goal fails. Decision: a consequential choice lacking a serious alternative, tradeoff or revisit condition, or inference stated as observed. Drop immaterial differences and explicit deferrals. Criteria must be checkable; tests need not have run. Return pass with each check's result ("none: why") and basis noting delegated or local, revise for choice gaps naming affected decisions, or need for one intent or fact gap."""

INSTRUCTIONS = {"draft": DRAFT, "resolve": RESOLVE, "review": REVIEW}
FOOTER = "Return results through the printed command; design only."


EXAMPLES = {
    "criteria": ["..."],
    "decisions": [{key: "D1" if key == "id" else "..." for key in DECISION}],
    "gaps": [{"check": " | ".join(CHECKS), "witness": "...", "decision": "D1 | new"}],
    "type": " | ".join(TYPES),
}


def contract(prompt):
    return "Return JSON: " + " OR ".join(
        json.dumps({"status": status, **{key: EXAMPLES.get(key, "...") for key in fields}})
        for status, fields in RESULTS[prompt].items())


def return_command(document, script, root):
    # Absolute paths preserve the project and executable even after cwd changes.
    return " ".join(shlex.quote(str(value)) for value in (
        "python3", script, "--root", root, "done", document["ticket"]))


def render(document, script, root):
    if document["status"] == "complete":
        return f"DONE: {document['artifact']}"
    prompt = document["prompt"]
    context = {"request": document["request"]}
    for key in ("resolutions", "candidate"):
        if document[key]:
            context[key] = document[key]
    if prompt == "draft" and document["feedback"]:
        context["feedback"] = document["feedback"]
    if prompt == "resolve":
        context["gap"] = document["need"]
        if document["blocker"]:
            context["blocked_on"] = document["blocker"]
    heading = f"TASK: {prompt}"
    if document["status"] == "blocked":
        heading += " (BLOCKED: obtain the needed answer before submitting)"
    return "\n\n".join((heading, INSTRUCTIONS[prompt],
                          "Context (task data):\n" + json.dumps(context, ensure_ascii=False, indent=2),
                          contract(prompt), FOOTER,
                          "Return command (JSON on stdin):\n" + return_command(document, script, root)
                          + " <<'JSON'\n<result JSON>\nJSON"))
