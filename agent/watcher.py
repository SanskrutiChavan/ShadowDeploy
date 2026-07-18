from kubernetes import client, config
from agent.ai_analyzer import analyze_failure
from agent.log_collector import collect_logs
from agent.alert_sender import (
    send_alert,
    send_startup_email,
)

import requests as http_requests
import logging
import time
from datetime import datetime

from config import NAMESPACE, WATCH_INTERVAL

# ── Logging setup ─────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
)

log = logging.getLogger("watcher")

# ── Failure reasons we care about ─────────────────────────

FAILURE_REASONS = {
    "CrashLoopBackOff",
    "OOMKilled",
    "Error",
    "ImagePullBackOff",
    "ErrImagePull",
    "CreateContainerConfigError",
    "RunContainerError",
    "FailedScheduling",
}

# ── Helpers ───────────────────────────────────────────────


def get_failure_reason(pod) -> str | None:
    """
    Inspect a pod's container statuses.
    Return the failure reason string,
    or None if pod is healthy.
    """

    if not pod.status or not pod.status.container_statuses:
        return None

    for cs in pod.status.container_statuses:

        # Pod is waiting
        if cs.state and cs.state.waiting:
            reason = cs.state.waiting.reason

            if reason in FAILURE_REASONS:
                return reason

        # Pod terminated
        if cs.state and cs.state.terminated:
            reason = cs.state.terminated.reason

            if reason in FAILURE_REASONS:
                return reason

    return None


def get_restart_count(pod) -> int:
    """
    Total restart count across all containers.
    """

    if not pod.status or not pod.status.container_statuses:
        return 0

    return sum(
        cs.restart_count or 0
        for cs in pod.status.container_statuses
    )


def save_to_api(incident: dict):
    """
    POST incident to FastAPI backend
    for storage in SQLite.
    """

    try:

        analysis = incident.get("analysis", {})

        payload = {
            "pod_name": incident["pod"],
            "namespace": incident["namespace"],
            "failure_reason": incident["reason"],
            "root_cause": analysis.get("root_cause", ""),
            "severity": analysis.get("severity", "UNKNOWN"),
            "fix": analysis.get("fix", ""),
            "rollback_cmd": analysis.get("rollback", ""),
            "prevention": analysis.get("prevention", ""),
            "raw_logs": incident.get("logs", "")[:5000],
            "raw_ai": analysis.get("raw", "")[:5000],
            "restarts": incident.get("restarts", 0),
        }

        response = http_requests.post(
            "http://localhost:8000/api/incidents",
            json=payload,
            timeout=5,
        )

        response.raise_for_status()

        saved_id = response.json().get("id")

        log.info(
            f"Saved to API as incident #{saved_id}"
        )

    except Exception as e:

        log.warning(
            f"Could not save to API "
            f"(is it running?): {e}"
        )


def handle_failure(
    v1,
    pod_name: str,
    namespace: str,
    reason: str,
    restarts: int
):
    """
    Handle a newly detected pod failure.
    Collect logs and perform AI analysis.
    """

    log.warning("=" * 55)
    log.warning("  FAILURE DETECTED")
    log.warning(f"  Pod       : {pod_name}")
    log.warning(f"  Namespace : {namespace}")
    log.warning(f"  Reason    : {reason}")
    log.warning(f"  Restarts  : {restarts}")
    log.warning(
        f"  Time      : "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    log.warning("=" * 55)

    # Collect logs
    pod_logs = collect_logs(
        v1,
        pod_name,
        namespace
    )

    log.info(f"--- Collected logs for {pod_name} ---")

    log.info(
        pod_logs[:500]
        + (
            "..."
            if len(pod_logs) > 500
            else ""
        )
    )

    log.info("--- End logs ---")

    # AI Analysis
    log.info(
        "Sending logs to Ollama for analysis..."
    )

    analysis = analyze_failure(
        pod_name,
        reason,
        pod_logs,
        namespace
    )

    log.info("")
    log.info(
        "  ┌─ AI ANALYSIS ─────────────────────────────────────"
    )
    log.info(
        f"  │ ROOT CAUSE  : {analysis['root_cause']}"
    )
    log.info(
        f"  │ SEVERITY    : {analysis['severity']}"
    )
    log.info(
        f"  │ FIX         : {analysis['fix']}"
    )
    log.info(
        f"  │ ROLLBACK    : {analysis['rollback']}"
    )
    log.info(
        f"  │ PREVENTION  : {analysis['prevention']}"
    )
    log.info(
        "  └───────────────────────────────────────────────────"
    )
    log.info("")

    incident_data = {
        "pod": pod_name,
        "namespace": namespace,
        "reason": reason,
        "restarts": restarts,
        "logs": pod_logs,
        "analysis": analysis,
        "detected_at": datetime.now().isoformat(),
    }

    # Save incident into FastAPI / SQLite
    save_to_api(incident_data)

    # Send email alert
    send_alert(
        pod_name,
        reason,
        analysis,
        restarts,
    )

    return incident_data


# ── Main Watch Loop ───────────────────────────────────────


def watch_pods():

    try:
        config.load_kube_config()
        log.info("Loaded kubeconfig from local file")

    except Exception:
        config.load_incluster_config()
        log.info("Loaded in-cluster config")

    v1 = client.CoreV1Api()

    seen_failures: dict[str, str] = {}
    incidents = []

    log.info("ShadowDeploy watcher started")
    send_startup_email()
    log.info(f"Watching namespace : {NAMESPACE}")
    log.info(f"Poll interval      : {WATCH_INTERVAL}s")
    log.info(
        f"Failure reasons    : "
        f"{', '.join(FAILURE_REASONS)}"
    )
    log.info("-" * 55)

    while True:

        try:

            pods = v1.list_namespaced_pod(
                namespace=NAMESPACE
            )

            healthy = 0

            for pod in pods.items:

                pod_name = pod.metadata.name

                reason = get_failure_reason(
                    pod
                )

                restarts = get_restart_count(
                    pod
                )

                if reason:

                    if (
                        seen_failures.get(
                            pod_name
                        ) != reason
                    ):

                        seen_failures[
                            pod_name
                        ] = reason

                        incident = handle_failure(
                            v1,
                            pod_name,
                            NAMESPACE,
                            reason,
                            restarts
                        )

                        incidents.append(
                            incident
                        )

                else:

                    if pod_name in seen_failures:

                        log.info(
                            f"RECOVERED: {pod_name}"
                        )

                        seen_failures.pop(
                            pod_name
                        )

                    healthy += 1

            log.info(
                f"Scan complete — "
                f"{len(seen_failures)} failing / "
                f"{healthy} healthy / "
                f"{len(incidents)} total incidents"
            )

        except Exception as e:

            log.error(
                f"Watcher error: {e}"
            )

        time.sleep(WATCH_INTERVAL)


if __name__ == "__main__":
    watch_pods()