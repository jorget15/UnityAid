"""Simple categorizer agent: listens for ReportCreated A2A messages and replies with ReportCategorized."""
import httpx, json, time

API='http://127.0.0.1:8000'

def run():
    print('starting categorizer agent')
    # lightweight polling of the A2A subscribe stream using httpx streaming
    with httpx.stream('GET', f'{API}/a2a/subscribe', timeout=None) as resp:
        for line in resp.iter_lines():
            if not line: continue
            s = line.decode('utf-8')
            if s.startswith('data:'):
                payload = json.loads(s[len('data:'):].strip())
                if payload.get('type') == 'ReportCreated':
                    report = payload.get('report')
                    if report:
                        desc = report.get('description','')
                        # naive categorize
                        cat = 'other'
                        text=desc.lower()
                        if any(w in text for w in ['insulin','medicine','clinic','injury']): cat='medical'
                        elif any(w in text for w in ['water','thirst']): cat='water'
                        elif any(w in text for w in ['food','hungry']): cat='food'
                        elif any(w in text for w in ['shelter','evacua','roof']): cat='shelter'
                        msg = {'type':'ReportCategorized','body':{'report_id': report['id'], 'category': cat}}
                        print('sending ReportCategorized', msg)
                        try:
                            httpx.post(f'{API}/a2a/send', json=msg, timeout=5)
                        except Exception as e:
                            print('post err',e)

if __name__ == '__main__':
    while True:
        try:
            run()
        except Exception as e:
            print('stream ended', e)
            time.sleep(1)
