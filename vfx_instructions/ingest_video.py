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
    meta = run(["yt-dlp",*INSECURE,"--no-warnings","--skip-download",
                "--print","%(uploader)s\t%(uploader_id)s\t%(title)s\t%(duration)s\t%(id)s\t%(extractor_key)s",url])
    uploader=uid=title=dur=vid=platform=""
    if meta.returncode==0 and meta.stdout.strip():
        parts=(meta.stdout.strip().split("\t")+[""]*6)[:6]
        uploader,uid,title,dur,vid,platform=parts
    slug = slug or slugify(title or vid)
    adir=os.path.join(ASSETS,slug); os.makedirs(adir,exist_ok=True)
    mp4=os.path.join(adir,"_src.mp4")
    dl=run(["yt-dlp",*INSECURE,"--no-warnings","-o",mp4,"-f","mp4/best",url])
    if not (os.path.exists(mp4) and os.path.getsize(mp4)>2000):
        print("  [error] download failed:", dl.stderr.strip()[:200]); return None
    # duration
    try: duration=float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",mp4]).stdout.strip())
    except: duration=float(dur or 0)
    # frames
    run(["ffmpeg","-y","-loglevel","error","-i",mp4,"-vf","fps=1/%d,scale=360:-1"%frame_every,
         os.path.join(adir,"frame_%02d.jpg")])
    frames=sorted("assets/%s/%s"%(slug,f) for f in os.listdir(adir) if f.startswith("frame_"))
    # transcribe
    txt=transcribe(mp4) if do_transcribe else None
    os.remove(mp4)
    # split filming vs editing at the editing-app boundary
    filming=editing=[]
    if txt:
        m=re.search(r'\b(open up |open )?(capcut|premiere|after effects|cap cut|import (both|your))', txt, re.I)
        if m:
            filming=clean_steps(txt[:m.start()]); editing=clean_steps(txt[m.start():])
        else:
            editing=clean_steps(txt)
    tags=sorted({v for k,v in TAG_KW.items() if k in (txt or '').lower()})
    rec={"effect":title or slug.replace('_',' ').title(),"slug":slug,"difficulty":difficulty,
         "source":(platform or "web").lower(),
         "source_url":url,
         "source_creator":(("%s (@%s)"%(uploader,uid)).strip() if uploader else None),
         "category_ids":[],"gear":None,
         "technique_note":"Ingested from an external %s video via yt-dlp + ffmpeg frames + Whisper transcription."%(platform or 'web'),
         "is_full_tutorial":bool(filming or editing),
         "filming_steps":filming,"editing_steps":editing,"breakdown_images":[],
         "demo_still":frames[0] if frames else None,
         "demo_frames":frames[:3],"editing_screenshots":frames[3:] if len(frames)>3 else [],
         "tags":tags,"num_lessons":1,"num_videos":1,
         "lessons":[{"post_id":(platform.lower()+"_"+vid) if vid else slug,
                     "title":title or "Tutorial","role":"tutorial","duration_sec":round(duration,1),
                     "wistia_id":None,"transcript":txt,"transcript_source":"whisper" if txt else None,
                     "source_url":url,"video_url":None}]}
    print("  ok: %s | filming:%d editing:%d frames:%d tags:%s"%(slug,len(filming),len(editing),len(frames),tags))
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

if __name__=="__main__":
    main()
