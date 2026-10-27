"""Copy exactly eleven frozen archives to the same author's private candidate.

Transient source URLs are read only from the private dispatch event. They are
never printed, written to a receipt, or supplied to gh as credentials.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, subprocess, sys, urllib.parse, urllib.request

REPO='Lshiqi67/proper-hat-guessing-c5-reproducibility'
SOURCE='Lshiqi67/proper-hat-guessing-number-of-c5'
TAG='c5-arxiv-v1-evidence-20261027'
ALLOWED_HOSTS={'release-assets.githubusercontent.com','objects.githubusercontent.com'}

class ValidationError(Exception): pass

def require(ok,message):
    if not ok: raise ValidationError(message)

def api(method,path,*extra):
    r=subprocess.run(['gh','api','--method',method,path,*extra],capture_output=True)
    require(r.returncode==0,'GitHub API request failed (raw details suppressed)')
    return json.loads(r.stdout) if r.stdout else None

def matches(asset,row):
    return (asset.get('state')=='uploaded' and asset.get('name')==row['name'] and
            asset.get('size')==row['bytes'] and asset.get('digest')=='sha256:'+row['sha256'])

def check_destination(payload):
    require(api('GET','repos/'+REPO)['private'] is True,'Destination must remain private')
    require(api('GET','repos/'+REPO+'/commits/main')['sha']==payload['expected_commit'],'Main changed')
    require(api('GET','repos/'+REPO+'/commits/'+TAG)['sha']==payload['expected_commit'],'Tag changed')
    release=api('GET','repos/'+REPO+'/releases/'+str(payload['target_release_id']))
    require(release['id']==payload['target_release_id'] and release['tag_name']==TAG,'Wrong release')
    require(release['draft'] is True,'Transfer requires the prepared draft release')
    return release

def check_url(raw):
    u=urllib.parse.urlparse(raw)
    require(u.scheme=='https' and u.hostname in ALLOWED_HOSTS,'Unapproved source URL host')
    require(u.username is None and u.password is None and u.port in (None,443),'Unapproved URL authority')
    require(bool(u.query) and len(raw)<12000,'Expected bounded signed asset URL')

class RestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        check_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def main():
    require(os.environ.get('GITHUB_REPOSITORY')==REPO,'Wrong running repository')
    require(os.environ.get('GITHUB_REF')=='refs/heads/main','Wrong running ref')
    require(os.environ.get('GITHUB_EVENT_NAME')=='workflow_dispatch','Manual dispatch only')
    here=Path(__file__).resolve().parent
    identities=json.loads((here/'asset-identities.json').read_text())
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    payload=json.loads(event['inputs']['transfer_payload'])
    require(payload['schema_version']==1 and payload['target_tag']==TAG,'Wrong payload schema/tag')
    require(re.fullmatch('[0-9a-f]{40}',payload['expected_commit']) is not None,'Invalid commit')
    require(payload['expected_commit']==os.environ.get('GITHUB_SHA'),'Dispatched commit differs')
    require(type(payload['target_release_id']) is int and payload['target_release_id']>0,'Invalid release id')
    pre=payload['source_preflight']
    require(pre['repository']==SOURCE and pre['private'] is True and pre['release_id']==425024563
            and pre['tag_name']=='c5-reviewed-2026-10-27','Invalid source preflight')
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(pre['checked_at'])).total_seconds()
    require(-60<=age<=1800,'Source preflight is stale')
    expected={r['name']:r for r in identities['assets']}
    rows=payload['assets']
    require(len(expected)==11 and len(rows)==11,'Expected eleven frozen archives')
    require(len({r['name'] for r in rows})==11 and {r['name'] for r in rows}==set(expected),'Asset set mismatch')
    for row in rows:
        require({k:row[k] for k in ('name','source_asset_id','bytes','sha256')}==expected[row['name']],
                'Frozen identity differs')
        require(re.fullmatch('[A-Za-z0-9_.-]+',row['name']) is not None,'Invalid archive name')
        check_url(row['signed_url'])
    work=Path('.c5-private-transfer')
    work.mkdir(exist_ok=False)
    opener=urllib.request.build_opener(RestrictedRedirect())
    verified=[]
    for row in rows:
        release=check_destination(payload)
        same=[a for a in release['assets'] if a['name']==row['name']]
        require(len(same)<=1,'Duplicate destination asset')
        if same:
            require(matches(same[0],row),'Existing asset mismatch; no overwrite permitted')
            asset=same[0]
        else:
            target=work/row['name']
            digest=hashlib.sha256(); size=0
            req=urllib.request.Request(row['signed_url'],headers={'User-Agent':'c5-private-transport/1'})
            with opener.open(req,timeout=240) as response, target.open('xb') as out:
                check_url(response.geturl())
                while block:=response.read(1024*1024):
                    size+=len(block)
                    require(size<=row['bytes'],'Downloaded archive exceeds frozen size')
                    digest.update(block);out.write(block)
            require(size==row['bytes'] and digest.hexdigest()==row['sha256'],'Downloaded frozen archive differs')
            with target.open('rb') as inp:
                require(hashlib.file_digest(inp,'sha256').hexdigest()==row['sha256'],'Readback differs')
            check_destination(payload)
            endpoint=('https://uploads.github.com/repos/'+REPO+'/releases/'+str(payload['target_release_id'])+
                      '/assets?name='+urllib.parse.quote(row['name']))
            asset=api('POST',endpoint,'-H','Content-Type: application/zip','--input',str(target))
            require(matches(asset,row),'Server digest mismatch')
        verified.append({'name':row['name'],'bytes':row['bytes'],'sha256':row['sha256'],
                         'asset_id':asset['id'],'server_digest':asset['digest']})
        print('VERIFIED '+row['name'],flush=True)
    check_destination(payload)
    result={'status':'ALL_11_FROZEN_ARCHIVES_COPIED_AND_SERVER_VERIFIED','repository':REPO,
            'release_id':payload['target_release_id'],'tag':TAG,'commit':payload['expected_commit'],
            'bytes':sum(r['bytes'] for r in verified),'assets':verified,
            'scope':'Transport only; no recompression, SAT search or certificate replay.'}
    print(json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__':
    try:main()
    except Exception as error:
        # Network exceptions can contain signed URLs. Never print exception text
        # except the fixed, bounded messages raised by this file.
        print('TRANSFER_FAILED '+type(error).__name__+
              (': '+str(error) if isinstance(error,ValidationError) else ': details suppressed'),file=sys.stderr)
        sys.exit(1)
