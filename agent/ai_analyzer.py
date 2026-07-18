import requests
import logging
import time

from config import OLLAMA_URL, OLLAMA_MODEL

log = logging.getLogger("ai_analyzer")

# ── Prompt template ───────────────────────────────────────

PROMPT_TEMPLATE = """
You are a senior Site Reliability Engineer (SRE) analyzing a Kubernetes pod failure.

Analyze the following failure and respond in EXACTLY this format with no extra text:

ROOT CAUSE:
[One clear sentence explaining what went wrong and why]

SEVERITY:
[Must be exactly one of: CRITICAL / HIGH / MEDIUM / LOW]

PROBABLE FIX:
[2-3 specific, actionable steps to fix this right now]

ROLLBACK COMMAND:
[The exact kubectl command to rollback, or "N/A" if not applicable]

PREVENTION:
[One sentence on how to prevent this in future deployments]

---
POD NAME: {pod_name}
FAILURE REASON: {reason}
NAMESPACE: {namespace}

POD LOGS (last 80 lines):
{logs}
---

Respond ONLY with the 5 sections above. No markdown, no extra explanation.
"""


def analyze_failure(
    pod_name: str,
    reason: str,
    logs: str,
    namespace: str = "default"
) -> dict:
    """
    Send pod failure data to Ollama and get structured RCA back.
    Returns a dictionary containing analysis results.
    """

    log.info(
        f"Sending {pod_name} to Ollama ({OLLAMA_MODEL})..."
    )

    start = time.time()

    prompt = PROMPT_TEMPLATE.format(
        pod_name=pod_name,
        reason=reason,
        namespace=namespace,
        logs=logs[:3000],
    )

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 400,
                    "top_p": 0.9,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        raw = response.json().get(
            "response",
            ""
        ).strip()

        elapsed = round(
            time.time() - start,
            1
        )

        log.info(
            f"Ollama responded in {elapsed}s "
            f"for {pod_name}"
        )

        result = _parse_response(raw)

        result["pod"] = pod_name
        result["reason"] = reason
        result["namespace"] = namespace
        result["raw"] = raw

        return result

    except requests.exceptions.ConnectionError:
        log.error(
            "Cannot connect to Ollama — "
            "is it running?"
        )

        return _fallback(
            pod_name,
            reason,
            "Ollama not running"
        )

    except requests.exceptions.Timeout:
        log.error(
            "Ollama timed out"
        )

        return _fallback(
            pod_name,
            reason,
            "Ollama timed out"
        )

    except Exception as e:
        log.error(
            f"AI analysis failed: {e}"
        )

        return _fallback(
            pod_name,
            reason,
            str(e)
        )


def _parse_response(raw: str) -> dict:
    """
    Extract sections from Ollama response.
    """

    sections = {
        "root_cause": _extract(
            raw,
            "ROOT CAUSE"
        ),
        "severity": _extract(
            raw,
            "SEVERITY"
        ),
        "fix": _extract(
            raw,
            "PROBABLE FIX"
        ),
        "rollback": _extract(
            raw,
            "ROLLBACK COMMAND"
        ),
        "prevention": _extract(
            raw,
            "PREVENTION"
        ),
    }

    sev = sections["severity"].upper()

    for level in (
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW"
    ):
        if level in sev:
            sections["severity"] = level
            break
    else:
        sections["severity"] = "UNKNOWN"

    return sections


def _extract(
    text: str,
    label: str
) -> str:
    """
    Pull content after a label.
    """

    lines = text.split("\n")

    result = []
    inside = False

    for line in lines:

        stripped = line.strip()

        if stripped.upper().startswith(
            label.upper() + ":"
        ):
            inside = True

            after = stripped[
                len(label) + 1:
            ].strip()

            if after:
                result.append(after)

            continue

        if inside:

            if any(
                stripped.upper().startswith(h)
                for h in [
                    "ROOT CAUSE:",
                    "SEVERITY:",
                    "PROBABLE FIX:",
                    "ROLLBACK COMMAND:",
                    "PREVENTION:",
                    "---",
                ]
            ):
                break

            if stripped:
                result.append(stripped)

    return (
        " ".join(result).strip()
        or "N/A"
    )


def _fallback(
    pod_name: str,
    reason: str,
    error: str
) -> dict:
    """
    Safe fallback if AI fails.
    """

    dep_name = "-".join(
        pod_name.split("-")[:-2]
    )

    return {
        "pod": pod_name,
        "reason": reason,
        "root_cause":
            f"AI unavailable ({error}). "
            f"K8s reason: {reason}",
        "severity": "UNKNOWN",
        "fix":
            "Manually inspect logs: "
            f"kubectl logs {pod_name} --previous",
        "rollback":
            f"kubectl rollout undo deployment/{dep_name}",
        "prevention": "N/A",
        "raw": "",
        "namespace": "default",
    }