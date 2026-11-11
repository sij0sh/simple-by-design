"""Small job-specific instructions and bounded current context."""

import json
import shlex

from .router import RESULTS

DRAFT = """Propose the simplest adequate solution design, not implementation. Inspect only as authorized by the request; do not edit a report-only target. Include material basis/citations, consequential choices with a serious alternative and tradeoff, assumptions/revisit conditions, and verification still needed. Preserve relevant prior resolutions in the design. Ask only when uncertainty could materially change it; ordinary reversible choices are yours. Return candidate, or need with one question and its consequence."""

RESOLVE = """Resolve this one material uncertainty within the request's authority. Intent needs the requester; facts need observation, otherwise remain assumptions. Compare serious engineering choices yourself; cheap reversible assumptions need a revisit condition. Do not invent answers or perform unauthorized actions. Return resolved with the answer and its basis, or blocked with the question and what/who is needed. After asking, pause until the answer is available."""

REVIEW = """Challenge this candidate against the original request, scope, material failure modes and cited basis. Distinguish observation from inference and tests actually run from planned verification. Prefer the simplest adequate choice; do not invent gaps. Review is local unless genuinely delegated: disclose that in your basis. If required independent review is unavailable, return need, not pass. Return pass only if the current design is adequate with honest limits; otherwise revise with actionable feedback, or need for one consequential uncertainty. Do not silently rewrite and approve."""

INSTRUCTIONS = {"draft": DRAFT, "resolve": RESOLVE, "review": REVIEW}
FOOTER = "Return results through the printed command; design only."


def contract(prompt):
    return "Return JSON: " + " OR ".join(
        json.dumps({"status": status, **{key: "..." for key in fields}})
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
    for key in ("candidate", "basis"):
        if document[key]:
            context[key] = document[key]
    if prompt == "draft" and document["feedback"]:
        context["feedback"] = document["feedback"]
    if prompt == "resolve":
        context["need"] = document["need"]
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
