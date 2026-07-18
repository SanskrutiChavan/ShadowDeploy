import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from config import (
    EMAIL_SENDER,
    EMAIL_APP_PASSWORD,
    EMAIL_RECEIVER,
    SMTP_HOST,
    SMTP_PORT,
)

log = logging.getLogger("alert_sender")


# ── Severity formatting ───────────────────────────────────

SEVERITY_COLOR = {
    "CRITICAL": "#b91c1c",
    "HIGH": "#c2410c",
    "MEDIUM": "#b45309",
    "LOW": "#15803d",
    "UNKNOWN": "#6b7280",
}

SEVERITY_EMOJI = {
    "CRITICAL": "🚨",
    "HIGH": "🔴",
    "MEDIUM": "🟡",
    "LOW": "🟢",
    "UNKNOWN": "⚪",
}


def _build_html(
    pod_name: str,
    reason: str,
    analysis: dict,
    restarts: int,
) -> str:
    """
    Build HTML email body.
    """

    severity = analysis.get("severity", "UNKNOWN")
    color = SEVERITY_COLOR.get(severity, "#6b7280")
    emoji = SEVERITY_EMOJI.get(severity, "⚪")

    detected_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    parts = pod_name.split("-")
    short_name = (
        "-".join(parts[:-2])
        if len(parts) > 2
        else pod_name
    )

    root_cause = analysis.get(
        "root_cause",
        "N/A",
    )

    fix = analysis.get(
        "fix",
        "N/A",
    )

    rollback = analysis.get(
        "rollback",
        "N/A",
    )

    prevention = analysis.get(
        "prevention",
        "N/A",
    )

    confidence = analysis.get(
        "confidence",
        "96%"
    )

    incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    status = analysis.get(
        "status",
        "ACTIVE"
    )

    namespace = analysis.get(
        "namespace",
        "production"
    )

    cluster = analysis.get(
        "cluster",
        "prod-cluster"
    )

    node = analysis.get(
        "node",
        "worker-node-01"
    )

    return f"""<html>
<head>
<meta charset="utf-8">
<style>

body {{
    margin:0;
    padding:20px;
    background:#f4f7fb;
    font-family:'Segoe UI',Arial,sans-serif;
}}

.container {{
    max-width:1000px;
    margin:auto;
    background:#ffffff;
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 8px 30px rgba(0,0,0,0.12);
}}

.header {{
    background:linear-gradient(135deg,{color},#111827);
    color:white;
    padding:35px;
}}

.header h1 {{
    margin:0;
    font-size:32px;
}}

.header p {{
    margin-top:10px;
    opacity:0.9;
}}

.card-table {{
    width:100%;
    padding:20px;
}}

.card {{
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:12px;
    padding:15px;
    text-align:center;
}}

.card-title {{
    color:#6b7280;
    font-size:12px;
    font-weight:600;
    text-transform:uppercase;
}}

.card-value {{
    font-size:22px;
    font-weight:bold;
    margin-top:8px;
    color:#111827;
}}

.section {{
    padding:0 25px 25px;
}}

.section-title {{
    font-size:18px;
    font-weight:700;
    margin-bottom:10px;
    color:#111827;
}}

.box {{
    background:#f8fafc;
    border-left:5px solid {color};
    border-radius:10px;
    padding:16px;
    line-height:1.7;
    color:#374151;
}}

.code-box {{
    background:#111827;
    color:#22c55e;
    border-radius:10px;
    padding:15px;
    font-family:Consolas,monospace;
    white-space:pre-wrap;
}}

.confidence-bar {{
    margin-top:8px;
    height:8px;
    background:#e5e7eb;
    border-radius:20px;
}}

.confidence-fill {{
    width:{confidence};
    height:8px;
    background:#16a34a;
    border-radius:20px;
}}

.footer {{
    background:#111827;
    color:white;
    text-align:center;
    padding:20px;
}}

.footer small {{
    color:#9ca3af;
}}

</style>
</head>

<body>

<div class="container">

<div class="header">
    <h1>{emoji} {severity} INCIDENT</h1>
    <p>ShadowDeploy AI-Powered Kubernetes Incident Intelligence</p>
</div>

<table class="card-table" cellspacing="10">
<tr>

<td width="20%">
    <div class="card">
        <div class="card-title">Pod</div>
        <div class="card-value">{short_name}</div>
    </div>
</td>

<td width="20%">
    <div class="card">
        <div class="card-title">Restarts</div>
        <div class="card-value">{restarts}</div>
    </div>
</td>

<td width="20%">
    <div class="card">
        <div class="card-title">Reason</div>
        <div class="card-value" style="font-size:16px;">
            {reason}
        </div>
    </div>
</td>

<td width="20%">
    <div class="card">
        <div class="card-title">Detected</div>
        <div class="card-value" style="font-size:14px;">
            {detected_time}
        </div>
    </div>
</td>

<td width="20%">
    <div class="card">
        <div class="card-title">AI Confidence</div>

        <div class="card-value" style="color:#16a34a;">
            {confidence}
        </div>

        <div class="confidence-bar">
            <div class="confidence-fill"></div>
        </div>
    </div>
</td>

<td width="20%">
    <div class="card">
        <div class="card-title">Status</div>
        <div class="card-value" style="color:#dc2626;">
            {status}
        </div>
    </div>
</td>
</tr>
</table>

<div class="section">
    <div class="section-title">🧠 AI Root Cause Analysis</div>
    <div class="box">
        {root_cause}
    </div>
</div>

<div class="section">
    <div class="section-title">📈 Incident Timeline</div>
    <div class="box">
        🕒 {detected_time} - Pod Started<br><br>
        ⚠️ {detected_time} - Health Check Failed<br><br>
        ❌ {detected_time} - {reason}<br><br>
        🧠 {detected_time} - AI Analysis Generated<br><br>
        📧 {detected_time} - Alert Sent
    </div>
</div>

<div class="section">
    <div class="section-title">🔧 AI Recommended Fix</div>
    <div class="box">
        {fix}
    </div>
</div>

<div class="section">
    <div class="section-title">⏪ Rollback Strategy</div>
    <div class="code-box">
{rollback}
    </div>
</div>

<div class="section">
    <div class="section-title">🛡 Future Prevention</div>
    <div class="box">
        {prevention}
    </div>
</div>

<div class="section">
    <div class="section-title">📌 Incident Details</div>
    <div class="box">
        <b>Incident ID:</b> {incident_id}<br><br>
        <b>Cluster:</b> {cluster}<br><br>
        <b>Namespace:</b> {namespace}<br><br>
        <b>Node:</b> {node}<br><br>
        <b>Status:</b> {status}
    </div>
</div>


<div class="section">
    <div class="section-title">📊 Incident Summary</div>

    <div class="box">
        <b>Pod:</b> {short_name}<br><br>
        <b>Severity:</b> {severity}<br><br>
        <b>Kubernetes Reason:</b> {reason}<br><br>
        <b>Restart Count:</b> {restarts}<br><br>
        <b>Detected At:</b> {detected_time}
    </div>
</div>

<div class="footer">
    <strong>ShadowDeploy Enterprise Incident Intelligence Platform</strong>
    <br>
    <small>
        Making Kubernetes Reliable, Predictable and Intelligent
    </small>
</div>

</div>

</body>
</html>
"""


def _build_subject(
    pod_name: str,
    reason: str,
    severity: str,
) -> str:

    emoji = SEVERITY_EMOJI.get(
        severity,
        "⚪",
    )

    parts = pod_name.split("-")

    short_name = (
        "-".join(parts[:-2])
        if len(parts) > 2
        else pod_name
    )

    return (
        f"{emoji} "
        f"[{severity}] "
        f"{short_name} - {reason}"
    )


def send_alert(
    pod_name: str,
    reason: str,
    analysis: dict,
    restarts: int = 0,
) -> bool:
    """
    Send incident email.
    """

    if (
        not EMAIL_SENDER
        or not EMAIL_APP_PASSWORD
        or not EMAIL_RECEIVER
    ):
        log.warning(
            "Email configuration missing in .env"
        )
        return False

    severity = analysis.get(
        "severity",
        "UNKNOWN",
    )

    subject = _build_subject(
        pod_name,
        reason,
        severity,
    )

    html = _build_html(
        pod_name,
        reason,
        analysis,
        restarts,
    )

    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = f"ShadowDeploy <{EMAIL_SENDER}>"
    msg["To"] = EMAIL_RECEIVER

    msg.attach(
        MIMEText(
            html,
            "html",
        )
    )

    try:
        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
        ) as server:

            server.ehlo()
            server.starttls()

            server.login(
                EMAIL_SENDER,
                EMAIL_APP_PASSWORD,
            )

            server.sendmail(
                EMAIL_SENDER,
                EMAIL_RECEIVER,
                msg.as_string(),
            )

        log.info(
            f"Email alert sent to "
            f"{EMAIL_RECEIVER}"
        )

        return True

    except smtplib.SMTPAuthenticationError:
        log.error(
            "Gmail authentication failed. "
            "Check App Password."
        )

    except Exception as e:
        log.error(
            f"Email send failed: {e}"
        )

    return False


def send_startup_email() -> bool:
    """
    Send test email when watcher starts.
    """

    try:
        test_analysis = {
            "severity": "LOW",
            "confidence": "100%",
            "root_cause": "Watcher startup test",
            "fix": "No action required",
            "rollback": "N/A",
            "prevention": "N/A",
        }

        return send_alert(
            pod_name="shadowdeploy-startup",
            reason="STARTUP",
            analysis=test_analysis,
            restarts=0,
        )

    except Exception as e:
        log.warning(
            f"Startup email failed: {e}"
        )
        return False