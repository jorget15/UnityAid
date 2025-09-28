"""Matcher agent: listens for ReportCategorized and sends ResourceMatched events to the A2A bus."""
import httpx, json, time

API='http://127.0.0.1:8000'

def choose_resource_for(report_id):
    # ask backend for resources and reports, choose nearest with capacity
    try:
        r = httpx.get(f'{API}/api/reports').json()
        rep = next((x for x in r if x['id']==report_id), None)
        res = httpx.get(f'{API}/api/resources').json()
        if not rep or not res: return None
        # naive nearest by lat/lon euclidean
        best = min((res), key=lambda x: (x['lat']-rep['lat'])**2 + (x['lon']-rep['lon'])**2)
        if best and best.get('capacity',0)>0:
            return best['id']
    except Exception as e:
        print('choose err',e)
    return None

def run():
    print('starting matcher agent')
    with httpx.stream('GET', f'{API}/a2a/subscribe', timeout=None) as resp:
        for line in resp.iter_lines():
            if not line: continue
            s = line.decode('utf-8')
            if s.startswith('data:'):
                payload = json.loads(s[len('data:'):].strip())
                if payload.get('type') == 'ReportCategorized':
                    body = payload.get('body') or {}
                    rid = body.get('report_id')
                    if rid:
                        rcid = choose_resource_for(rid)
                        if rcid:
                            msg = {'type':'ResourceMatched','body':{'report_id':rid,'resource_id':rcid}}
                            print('sending ResourceMatched', msg)
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
