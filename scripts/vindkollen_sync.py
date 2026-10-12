#!/usr/bin/env python3
"""Idempotent sync: vindkollen_leads (sajtens Postgres) -> core.leads (source_site=vindkollen).
Synkar rader med wants_legal_help=true ELLER source ersattning_for_vindkraft_kvalificering.
Loggar bara antal/län — aldrig namn eller e-post. Kör: vindkollen_sync.py [--apply]"""
import os, sys, json, collections, urllib.request
import psycopg2, psycopg2.extras
APPLY = "--apply" in sys.argv
P="40a696b3-a4fa-40ee-aaa9-0cf2c1d22f60"; E="7105e5b6-80a8-4645-9e64-54b988d27434"; PG="3663a85a"
def gql(query, v):
    r=urllib.request.Request("https://backboard.railway.com/graphql/v2",json.dumps({"query":query,"variables":v}).encode(),
        {"Authorization":"Bearer "+os.environ["RAILWAY_TOKEN"],"Content-Type":"application/json","User-Agent":"curl/8"})
    return json.load(urllib.request.urlopen(r))
sid=[e["node"]["id"] for e in gql('query($p:String!){project(id:$p){services{edges{node{id name}}}}}',{"p":P})["data"]["project"]["services"]["edges"] if e["node"]["name"]=="Postgres"][0]
src_url=gql('query($p:String!,$e:String!,$s:String!){variables(projectId:$p,environmentId:$e,serviceId:$s)}',{"p":P,"e":E,"s":sid})["data"]["variables"]["DATABASE_PUBLIC_URL"]
src=psycopg2.connect(src_url); sc=src.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
sc.execute("""select id,created_at,name,email,source,segment,county,municipality,land_hectares,project_stage,wants_legal_help,wants_projector_contact,lead_score,lead_tier
 from vindkollen_leads where wants_legal_help is true or source='ersattning_for_vindkraft_kvalificering' order by id""")
rows=sc.fetchall()
sc.execute("select count(*) n from vindkollen_leads"); total=sc.fetchone()["n"]
dst=psycopg2.connect(os.environ[os.environ.get("SYNC_DB_ENV","AGENT_DB_URL_TECH")]); dst.autocommit=False; dc=dst.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
new=0; have=0; bycounty=collections.Counter(); legal=0; tests=0
for r in rows:
    email=(r["email"] or "").strip().lower()
    if not email: continue
    test=email.endswith(("@example.com","@adviseo.se"))
    if test: tests+=1; continue
    if r["wants_legal_help"] and not test: legal+=1; bycounty[r["county"] or "okänt"]+=1
    dc.execute("select id from core.companies where lower(domain)=%s",(email,)); c=dc.fetchone()
    if c: cid=c["id"]
    else:
        if not APPLY: new+=1; continue
        dc.execute("insert into core.companies (name,domain,source,created_by,meta) values (%s,%s,%s,'tech','{}'::jsonb) returning id",(r["name"] or email,email,r["source"] or "silo_form")); cid=dc.fetchone()["id"]
    dc.execute("select id from core.leads where company_id=%s and source_site='vindkollen'",(cid,))
    if dc.fetchone(): have+=1; continue
    new+=1
    if not APPLY: continue
    why=f"score={r['lead_score']} tier={r['lead_tier']} segment={r['segment']} län={r['county']} juridik={bool(r['wants_legal_help'])} ha={r['land_hectares']} fas={r['project_stage']} src_id={r['id']}"
    dc.execute("insert into core.leads (company_id,source,source_site,owner_agent,score,created_by,meta) values (%s,%s,'vindkollen','tech',%s,'tech',%s::jsonb)",
      (cid,r["source"] or "silo_form",r["lead_score"] or 0,json.dumps({"why":why,"email":email,"synced_from":"vindkollen_leads","created_at":str(r["created_at"])})))
    dc.execute("insert into core.contacts (company_id,name,email,role,created_by) values (%s,%s,%s,'markägare','tech')",(cid,r["name"] or email,email))
if APPLY: dst.commit()
print(json.dumps({"apply":APPLY,"site_total":total,"qualifying_rows":len(rows),"legal_help_real":legal,"test_rows":tests,"legal_by_county":dict(bycounty),"newly_synced" if APPLY else "would_sync":new,"already_in_core":have},ensure_ascii=False))
