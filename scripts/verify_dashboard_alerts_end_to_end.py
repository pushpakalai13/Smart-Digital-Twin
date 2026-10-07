import sys
import os
import urllib.request
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db
from app.core.security import create_access_token

def main():
    db = get_db()
    token = create_access_token({"sub": "admin@smartcampus.edu", "role": "admin", "name": "System Admin"})
    headers = {"Authorization": f"Bearer {token}"}

    print("=== VERIFYING /api/dashboard ===")
    url_dash = "http://127.0.0.1:8000/api/dashboard"
    req_dash = urllib.request.Request(url_dash, headers=headers)
    try:
        with urllib.request.urlopen(req_dash) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"Active Data Source: {data.get('source')}")
            print(f"Campus Efficiency Score: {data.get('efficiency_score')}%")
            print(f"Active Alerts Count KPI: {data.get('kpis', {}).get('alerts', {}).get('active_count')}")
            
            print("\nRecent Active Alerts (Top 5 on Dashboard):")
            recent_alerts = data.get("recent_alerts", [])
            print(f"Total recent alerts returned: {len(recent_alerts)}")
            for a in recent_alerts:
                print(f"  - [{a.get('alert_id')}] {a.get('building_name')} | Metric: {a.get('metric')} ({a.get('value')}) | Created At: {a.get('created_at')} | Severity: {a.get('severity')}")

            print("\nTop AI Optimization Recommendations:")
            top_recs = data.get("top_recommendations", [])
            print(f"Total top recommendations returned: {len(top_recs)}")
            for r in top_recs:
                print(f"  - [{r.get('rec_id')}] {r.get('title')} | Building: {r.get('building_name')} | Impact: {r.get('impact')} | Created At: {r.get('created_at')}")

    except Exception as e:
        print(f"Error fetching dashboard summary: {e}")

    print("\n=== VERIFYING /api/alerts Endpoint ===")
    url_alerts = "http://127.0.0.1:8000/api/alerts"
    req_alerts = urllib.request.Request(url_alerts, headers=headers)
    try:
        with urllib.request.urlopen(req_alerts) as resp:
            alerts_list = json.loads(resp.read().decode('utf-8'))
            print(f"Total active alerts returned by /api/alerts: {len(alerts_list)}")
            if alerts_list:
                print("First 3 alerts from /api/alerts:")
                for a in alerts_list[:3]:
                    print(f"  - [{a.get('alert_id')}] {a.get('building_name')} | Timestamp: {a.get('created_at')} | Source: {a.get('source')}")
    except Exception as e:
        print(f"Error fetching /api/alerts: {e}")

if __name__ == "__main__":
    main()
