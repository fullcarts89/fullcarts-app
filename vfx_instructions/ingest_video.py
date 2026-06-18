#!/usr/bin/env python3
"""Ingest a public short-form video (Instagram / YouTube / TikTok) into the VFX
instruction schema used by effects.json — i.e. turn a video into a Claude-readable
recreation guide.

Pipeline:  yt-dlp (download)  ->  ffmpeg (frames "seeing")  ->  faster-whisper
(transcription "hearing")  ->  schema record appended to external_sources.json.

Usage:
    python ingest_video.py <url> [<url> ...]
    python ingest_video.py <url> --slug my_effect --difficulty Beginner
    python ingest_video.py <url> --no-transcribe          # frames + metadata only

Requirements: yt-dlp, ffmpeg/ffprobe on PATH, and (for transcription) faster-whisper.
Behind a TLS-intercepting proxy, set INGEST_INSECURE=1 to pass --no-check-certificates.

Re-running on a URL already present updates that record in place (dedupe by source_url).
"""
import argparse, json, os, re, subprocess, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
STORE = os.path.join(HERE, "external_sources.json")
INSECURE = ["--no-check-certificates"] if os.environ.get("INGEST_INSECURE") else []

FILLER = re.compile(r'^(welcome|hey|hi |what(?:\'s| is) up|in this (?:video|reel|lesson)|today|'
    r'so here we (?:are|go)|here we (?:are|go)|magic|boom|there (?:we|you) (?:go|have it)|'
    r'and (?:that|there)(?:\'s| is) (?:it|how)|thanks for|see you|follow for|like and|'
    r'don\'t forget|comment|save this|pretty (?:cool|simple|easy))', re.I)

def clean_steps(txt):
    if not txt: return []
    out=[]
    for x in re.split(r'(?<=[.!?])\s+', txt.strip()):
        x=re.sub(r'^(okay|ok|so|now|alright|and then|then|and|um|uh)[,\s]+','',x.strip(),flags=re.I)
        x=re.sub(r'\s+',' ',x).strip()
        if len(x)<10 or FILLER.match(x): continue
        out.append(x[0].upper()+x[1:])
    return out

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def slugify(s):
    s=re.sub(r'[^\w\s-]','',(s or 'video')).strip().lower()
    return re.sub(r'[\s_-]+','_',s)[:40] or 'video'

TAG_KW={'mask':'mask','overlay':'overlay','keyframe':'keyframes','clean plate':'clean_plate',
 'blend':'blend_mode','green screen':'green_screen','cutout':'cutout','duplicate':'duplicate',
 'remove background':'auto_bg_removal','auto removal':'auto_bg_removal','tripod':'locked_off',
 'clone':'cloning','transition':'transition','speed':'speed_ramp','split':'split_clip'}

# CapCut features mentioned (regex -> canonical name)
CAPCUT_KW={r'\boverlay\b':'Overlay',r'\bmask\b':'Mask',r'\bkeyframe':'Keyframes',
 r'remove background':'Remove Background',r'chroma key':'Chroma Key',r'\bspeed\b':'Speed',
 r'\bsplit\b':'Split',r'\bduplicate\b':'Duplicate',r'\brotate\b':'Rotate',r'\btext\b':'Text',
 r'opacity':'Opacity',r'\blayers?\b':'Layers',r'body effects':'Body Effects',
 r'video effects':'Video Effects',r'\bcrop\b':'Crop',r'aspect ratio':'Aspect Ratio',
 r'reverse':'Reverse',r'feather':'Feather'}
# AI generation tools mentioned
AI_KW={'higgsfield':'Higgsfield','openart':'OpenArt','kling':'Kling','runway':'Runway',
 'sora':'Sora','pika':'Pika','midjourney':'Midjourney','luma':'Luma','veo':'Veo'}

def transcribe(mp4):
    try:
        from faster_whisper import WhisperModel
    except Exception:
        print("  [warn] faster-whisper not installed; skipping transcription")
        return None
    model = transcribe._m if hasattr(transcribe,"_m") else None
    if model is None:
        model = WhisperModel(os.environ.get("INGEST_WHISPER_MODEL","base.en"),
                             device="cpu", compute_type="int8")
        transcribe._m = model
    segs,_ = model.transcribe(mp4, vad_filter=True)
    return " ".join(s.text.strip() for s in segs).strip()

def ingest(url, slug=None, difficulty="Beginner", do_transcribe=True, frame_every=3):
    print("==>", url)
    # full metadata (caption, hashtags, engagement, dimensions)
    mj = run(["yt-dlp",*INSECURE,"--no-warnings","--skip-download","--dump-single-json",url])
    j = {}
    try: j = json.loads(mj.stdout)
    except Exception: pass
    uploader=j.get("uploader") or ""; uid=j.get("uploader_id") or ""
    title=j.get("title") or ""; vid=j.get("id") or ""
    platform=(j.get("extractor_key") or "web")
    duration=float(j.get("duration") or 0)
    caption=(j.get("description") or "").strip()
    hashtags=sorted(set(re.findall(r'#(\w+)', caption)))
    slug = slug or slugify(title or vid)
    adir=os.path.join(ASSETS,slug); os.makedirs(adir,exist_ok=True)
    mp4=os.path.join(adir,"_src.mp4")
    dl=run(["yt-dlp",*INSECURE,"--no-warnings","-o",mp4,"-f","mp4/best",url])
    if not (os.path.exists(mp4) and os.path.getsize(mp4)>2000):
        print("  [error] download failed:", dl.stderr.strip()[:200]); return None
    try: duration=float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",mp4]).stdout.strip()) or duration
    except: pass
    run(["ffmpeg","-y","-loglevel","error","-i",mp4,"-vf","fps=1/%d,scale=360:-1"%frame_every,
         os.path.join(adir,"frame_%02d.jpg")])
    frames=sorted("assets/%s/%s"%(slug,f) for f in os.listdir(adir) if f.startswith("frame_"))
    txt=transcribe(mp4) if do_transcribe else None
    os.remove(mp4)
    # heuristic filming/editing split (NOTE: imperfect; review + re-author for quality)
    filming=[]; editing=[]
    if txt:
        m=re.search(r'\b(open up |open )?(capcut|premiere|after effects|cap cut|import (both|your))', txt, re.I)
        if m: filming=clean_steps(txt[:m.start()]); editing=clean_steps(txt[m.start():])
        else: editing=clean_steps(txt)
    low=(txt or '').lower()
    tags=sorted({v for k,v in TAG_KW.items() if k in low})
    capcut_features=sorted({v for k,v in CAPCUT_KW.items() if re.search(k, low)})
    ai_tools=sorted({v for k,v in AI_KW.items() if k in low})
    is_ai=bool(ai_tools)
    if is_ai: capcut_features=[]   # AI-tool tutorials aren't CapCut recipes
    rec={"effect":title or slug.replace('_',' ').title(),"slug":slug,"difficulty":difficulty,
         "source":platform.lower(),"source_url":url,
         "source_creator":(("%s (@%s)"%(uploader,uid)).strip() if uploader else None),
         "tool":("AI ("+", ".join(ai_tools)+")") if is_ai else ("CapCut" if capcut_features else None),
         "effect_category":None,
         "category_ids":[],"gear":None,
         "technique_note":"Ingested from an external %s video via yt-dlp + ffmpeg frames + Whisper transcription. Steps auto-split (review recommended)."%platform,
         "is_full_tutorial":bool(filming or editing),
         "requires_filming":bool(filming),
         "is_ai_generated":is_ai,"ai_tools":ai_tools,"prompt_needed":is_ai,
         "capcut_features":capcut_features,
         "inputs_required":[],"props":[],"needs_clean_plate":("clean plate" in low),
         "needs_tripod":("tripod" in low or "locked" in low),"output_aspect":"9:16",
         "sound_design":None,
         "filming_steps":filming,"editing_steps":editing,"breakdown_images":[],
         "demo_still":frames[0] if frames else None,
         "demo_frames":frames[:3],"editing_screenshots":frames[3:] if len(frames)>3 else [],
         "tags":tags,"num_lessons":1,"num_videos":1,
         "source_meta":{"platform":platform.lower(),"creator_name":uploader or None,
            "creator_handle":uid or None,"creator_url":j.get("uploader_url"),
            "caption":caption[:2000] or None,"hashtags":hashtags,
            "view_count":j.get("view_count"),"like_count":j.get("like_count"),
            "comment_count":j.get("comment_count"),"upload_date":j.get("upload_date"),
            "duration_sec":j.get("duration"),"thumbnail":j.get("thumbnail"),
            "width":j.get("width"),"height":j.get("height")},
         "lessons":[{"post_id":(platform.lower()+"_"+vid) if vid else slug,
                     "title":title or "Tutorial","role":"tutorial","duration_sec":round(duration,1),
                     "wistia_id":None,"transcript":txt,"transcript_source":"whisper" if txt else None,
                     "source_url":url,"video_url":None}]}
    print("  ok: %s | filming:%d editing:%d frames:%d ai:%s tags:%s"%(slug,len(filming),len(editing),len(frames),is_ai,tags))
    return rec

def save(records):
    if os.path.exists(STORE):
        doc=json.load(open(STORE))
    else:
        doc={"source":"External short-form videos ingested into the VFX schema",
             "generated":"","schema_version":1,"effect_count":0,"effects":[]}
    by={e["source_url"]:i for i,e in enumerate(doc["effects"])}
    for r in records:
        if not r: continue
        if r["source_url"] in by: doc["effects"][by[r["source_url"]]]=r
        else: doc["effects"].append(r)
    import datetime
    doc["generated"]=datetime.date.today().isoformat()
    doc["effect_count"]=len(doc["effects"])
    json.dump(doc, open(STORE,"w"), indent=1, ensure_ascii=False)
    print("saved %d records -> %s"%(len(doc["effects"]), STORE))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--difficulty", default="Beginner")
    ap.add_argument("--no-transcribe", action="store_true")
    a=ap.parse_args()
    recs=[ingest(u, slug=a.slug if len(a.urls)==1 else None,
                 difficulty=a.difficulty, do_transcribe=not a.no_transcribe) for u in a.urls]
    save(recs)
    emit_manuals(recs)

def emit_manuals(records):
    """Land every freshly-ingested video in the MANUAL_SCHEMA format too.

    Writes a draft manual per record (preserving any hand-authored manual) and
    rebuilds manuals/index.json, so future videos are saved/created in this format
    automatically — ready for the VFX tool and for human re-authoring.
    """
    try:
        import manual_builder as mb
    except Exception as e:
        print("  [warn] manual_builder unavailable, skipping manual emit:", e); return
    n=0
    for r in records:
        if not r: continue
        _,status=mb.write_draft_if_absent(r); n+=1
        print("  manual[%s]: %s"%(status, r["slug"]))
    idx=mb.rebuild_index()
    print("manuals: %d emitted, index rebuilt (%d total) -> manuals/index.json"%(n, idx["count"]))

if __name__=="__main__":
    main()
