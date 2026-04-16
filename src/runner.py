import time
import yaml
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from src.alerting import send_slack
from src.detector import HybridDetector


load_dotenv(find_dotenv())

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def format_alert(prefix, row, det, labels, channel_hint):
    svc = labels.get("service","unknown")
    env = labels.get("env","unknown")
    ts = row[0]
    loss = row[1]
    mean = det.get("rolling_mean")
    std = det.get("rolling_std")
    ath = det.get("adaptive_threshold")

    msg = f"""
{prefix} – *{svc}* ({env})
*Timestamp:* {ts}
*Loss:* {loss:.6f}
"""
    if mean is not None:
        msg += f"*Rolling Mean:* {mean:.6f}, *Rolling Std:* {std:.6f}\n"
    if ath is not None:
        msg += f"*Adaptive Threshold:* {ath:.6f}\n"

    msg += f"_Channel: {channel_hint}_"
    return msg.strip()

def run_csv(cfg):
    file = cfg["input"]["file"]
    detcfg = cfg["detection"]
    labels = cfg.get("labels", {})
    alertcfg = cfg.get("alerting", {})
    debounce_seconds = int(alertcfg.get("debounce_seconds", 0))
    channel_hint = alertcfg.get("slack", {}).get("channel_hint", "#alerts")

    det = HybridDetector(
        fixed_threshold=float(detcfg["fixed_threshold"]),
        window_size=int(detcfg["window_size"]),
        z_limit=float(detcfg["z_limit"]),
        min_warmup=int(detcfg["min_warmup"])
    )

    last_lines = 0
    print("👀 Watching live_losses.csv for new values... Leave this terminal running.\n")

    while True:
        try:
            df = pd.read_csv(file, header=None)
            if len(df) > last_lines:
                new_rows = df.iloc[last_lines:]
                for _, row in new_rows.iterrows():
                    loss = float(row[1])
                    det_result = det.update(loss)

                    if det_result["is_anomaly"]:
                        send_slack(format_alert("🚨 *ANOMALY DETECTED*", row, det_result, labels, channel_hint),
                                   debounce_key="anomaly", debounce_seconds=debounce_seconds)

                    elif det_result["is_spike"]:
                        send_slack(format_alert("⚠️ *SPIKE DETECTED*", row, det_result, labels, channel_hint),
                                   debounce_key="spike", debounce_seconds=debounce_seconds)

                last_lines = len(df)

        except Exception as e:
            print(f"⚠️ Error reading file: {e}")

        time.sleep(2)  # check again every 2 seconds

def main():
    cfg = load_config()
    run_csv(cfg)

if __name__ == "__main__":
    main()
