from kubernetes import client
import logging

log = logging.getLogger("log_collector")

MAX_LINES = 80  # enough context for AI, not too long


def collect_logs(
    v1: client.CoreV1Api,
    pod_name: str,
    namespace: str
) -> str:
    """
    Try to get logs from the pod in this order:

      1. Previous container (if pod restarted)
      2. Current container
      3. Fallback message if both fail
    """

    # 1. Previous container logs
    try:
        logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=MAX_LINES,
            previous=True,
            timestamps=True,
        )

        if logs and logs.strip():
            log.info(
                f"Got previous-container logs for "
                f"{pod_name} ({len(logs)} chars)"
            )

            return (
                "[previous container logs]\n"
                f"{logs}"
            )

    except Exception as e:
        log.debug(
            f"No previous logs for {pod_name}: {e}"
        )

    # 2. Current container logs
    try:
        logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=MAX_LINES,
            timestamps=True,
        )

        if logs and logs.strip():
            log.info(
                f"Got current-container logs for "
                f"{pod_name} ({len(logs)} chars)"
            )

            return (
                "[current container logs]\n"
                f"{logs}"
            )

    except Exception as e:
        log.debug(
            f"No current logs for {pod_name}: {e}"
        )

    # 3. No logs available
    log.warning(
        f"No logs available for {pod_name} "
        f"(image may never have started)"
    )

    return (
        "(no logs — container never started, "
        "likely ImagePullBackOff or bad image)"
    )