import json
import os
from datetime import datetime

from config import CACHE_DIR

_HISTORY_FILE = os.path.join(CACHE_DIR, "alerts_history.json")

ALERT_THRESHOLDS = {
    "var_95_max":        0.03,
    "volatility_max":    0.30,
    "sharpe_min":        0.5,
    "concentration_max": 0.35,
    "negative_news_max": 3,
}


def check_risk_alerts(risk_data, market_data=None, news_data=None):
    alerts = []
    now = datetime.now().isoformat()

    pm = risk_data.get("portfolio_metrics", {}) if isinstance(risk_data, dict) else {}
    var_95 = risk_data.get("var_95") or pm.get("var_95")
    if var_95 is not None:
        try:
            if abs(float(var_95)) > ALERT_THRESHOLDS["var_95_max"]:
                alerts.append({
                    "type": "risk",
                    "level": "alto",
                    "message": f"VaR 95% elevado: {abs(float(var_95)):.2%} (umbral: {ALERT_THRESHOLDS['var_95_max']:.2%})",
                    "timestamp": now,
                })
        except (ValueError, TypeError):
            pass

    vol = pm.get("annual_volatility")
    if vol is not None:
        try:
            if float(vol) > ALERT_THRESHOLDS["volatility_max"]:
                alerts.append({
                    "type": "volatility",
                    "level": "medio",
                    "message": f"Volatilidad anual alta: {float(vol):.2%} (umbral: {ALERT_THRESHOLDS['volatility_max']:.2%})",
                    "timestamp": now,
                })
        except (ValueError, TypeError):
            pass

    hhi = pm.get("hhi_concentration")
    if hhi is not None:
        try:
            if float(hhi) > ALERT_THRESHOLDS["concentration_max"]:
                alerts.append({
                    "type": "concentration",
                    "level": "medio",
                    "message": f"Portafolio muy concentrado. HHI: {float(hhi):.3f} (umbral: {ALERT_THRESHOLDS['concentration_max']})",
                    "timestamp": now,
                })
        except (ValueError, TypeError):
            pass

    if market_data:
        metrics = market_data.get("metrics", {}) if isinstance(market_data, dict) else {}
        for ticker, m in metrics.items():
            sharpe = m.get("sharpe") or m.get("sharpe_ratio")
            if sharpe is not None:
                try:
                    if float(sharpe) < ALERT_THRESHOLDS["sharpe_min"]:
                        alerts.append({
                            "type": "performance",
                            "level": "bajo",
                            "message": f"{ticker}: Sharpe bajo ({float(sharpe):.2f})",
                            "timestamp": now,
                        })
                except (ValueError, TypeError):
                    pass

    if news_data and isinstance(news_data, list):
        neg_count = sum(1 for n in news_data if n.get("sentiment") == "negativo")
        if neg_count > ALERT_THRESHOLDS["negative_news_max"]:
            alerts.append({
                "type": "sentiment",
                "level": "medio",
                "message": f"{neg_count} noticias negativas detectadas (umbral: {ALERT_THRESHOLDS['negative_news_max']})",
                "timestamp": now,
            })

    _save_alerts(alerts)
    return alerts


def _save_alerts(new_alerts):
    if not new_alerts:
        return
    os.makedirs(CACHE_DIR, exist_ok=True)
    history = get_alerts_history(limit=200)
    combined = new_alerts + history
    with open(_HISTORY_FILE, "w") as f:
        json.dump(combined[:200], f, indent=2)


def send_email_alert(alerts, recipient_email, smtp_config=None):
    if not alerts or not recipient_email:
        return False
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        cfg = smtp_config or {}
        host = cfg.get("host", "smtp.gmail.com")
        port = cfg.get("port", 587)
        user = cfg.get("user", "")
        pwd  = cfg.get("password", "")

        if not user or not pwd:
            print("[AlertManager] SMTP credentials not configured")
            return False

        body = "Alertas de Portfolio Intelligence:\n\n"
        for a in alerts:
            body += f"[{a.get('level','').upper()}] {a.get('message','')}\n"

        msg = MIMEMultipart()
        msg["From"]    = user
        msg["To"]      = recipient_email
        msg["Subject"] = f"Portfolio Alerts — {len(alerts)} alertas activas"
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, pwd)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[AlertManager] Email error: {e}")
        return False


def get_alerts_history(limit=20):
    if not os.path.exists(_HISTORY_FILE):
        return []
    try:
        with open(_HISTORY_FILE) as f:
            return json.load(f)[:limit]
    except Exception:
        return []
