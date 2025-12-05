#5
# --- Cell E — Finalized Plan Logic (with Interval Mapping + Deload + Full Tapering) ---
import pandas as pd, json, requests, re, random
from datetime import datetime, timedelta

# ---------- Helper Functions ----------
def clamp(v, lo, hi): return max(lo, min(hi, v))
def mmss(minkm):
    m=int(minkm); s=int(round((minkm-m)*60)); return f"{m}:{s:02d} min/km"
def strength_choice():
    return f"Strength: {random.choice(['Upper Body','Lower Body','Yoga'])}"

# ---------- 1) Fetch Data ----------
with open("tokens.json","r") as f: tokens = json.load(f)
all_runs, all_profiles = [], []
name_rx = re.compile(r"(morning|afternoon|evening|night)\s*run", re.IGNORECASE)

def fetch_all_pages(headers, per_page=200, max_pages=3):
    out=[]
    for page in range(1,max_pages+1):
        r=requests.get("https://www.strava.com/api/v3/athlete/activities",
                       headers=headers,params={"per_page":per_page,"page":page})
        if r.status_code!=200: break
        items=r.json()
        if not items: break
        out.extend(items)
        if len(items)<per_page: break
    return out

for athlete_id, creds in tokens.items():
    try:
        headers={"Authorization":f"Bearer {creds['access_token']}"}
        prof=requests.get("https://www.strava.com/api/v3/athlete",headers=headers)
        athlete_age=creds.get("age",None)
        if prof.status_code==200:
            p=prof.json()
            all_profiles.append({
                "athlete_id":str(athlete_id),
                "weight":p.get("weight",None),
                "age":athlete_age
            })
        acts=fetch_all_pages(headers)
        for a in acts:
            if "Run" not in a.get("type",""): continue
            nm=(a.get("name") or "").strip()
            if not name_rx.search(nm): continue
            dist=(a.get("distance",0) or 0)/1000.0
            mt=(a.get("moving_time",0) or 0)/60.0
            if dist<=0.5 or mt<=5: continue
            all_runs.append({
                "athlete_id":str(athlete_id),
                "name":nm,
                "distance_km":dist,
                "moving_time_min":mt,
                "average_heartrate":a.get("average_heartrate",None),
                "start_date_local":a.get("start_date_local","")
            })
    except Exception as e:
        print(f"❌ Error fetching {athlete_id}: {e}")

df_runs=pd.DataFrame(all_runs); df_profiles=pd.DataFrame(all_profiles)

if df_runs.empty:
    print("⚠️ No valid runs fetched. Authorize athletes first (Cells A–C).")
else:
    df_runs["start_date_local"]=pd.to_datetime(df_runs["start_date_local"],errors="coerce")
    df_runs["pace_min_per_km"]=(df_runs["moving_time_min"]/df_runs["distance_km"]).clip(2.0,15.0)
    df_runs=df_runs.sort_values("start_date_local").reset_index(drop=True)
    print(f"✅ Clean runs: {len(df_runs)}")

# ---------- 2) User Inputs ----------
target_distance=int(input("Enter target race distance (5, 10, 21, 42): "))
fitness_level=input("Enter fitness level (novice/intermediate/advanced): ").lower()
available_run_days=int(input("Enter available run days per week (3 or 4): "))
age=int(input("Enter your age: "))
weight=float(input("Enter your weight (kg): "))

option_4day=None
if available_run_days==4:
    option_4day=input("Option A (4 runs+3 ST) or B (4 runs+2 ST+1 Rest)? Enter A/B: ").upper()
    while option_4day not in ("A","B"):
        option_4day=input("Please enter A or B: ").upper()

WEEKS_BY_DISTANCE={5:8,10:12,21:16,42:20}
total_weeks=WEEKS_BY_DISTANCE[target_distance]
TAPER_WKS=2 if target_distance==5 else 3 if target_distance in (10,21) else 4
pre_taper=total_weeks-TAPER_WKS
LEVEL_RANGE={"novice":(8.0,9.5),"intermediate":(6.5,8.0),"advanced":(5.0,6.5)}

# ---------- 3) Map Baseline Athlete ----------
def experience_window_filter(runs, level):
    if runs.empty: return runs
    runs=runs.sort_values("start_date_local")
    first,now=runs["start_date_local"].min(),runs["start_date_local"].max()
    two_y=first+timedelta(days=730)
    if level=="novice": return runs[runs["start_date_local"]<=two_y]
    elif level=="intermediate": return runs[runs["start_date_local"]>two_y]
    else: return runs[runs["start_date_local"]>=(now-timedelta(days=730))]

def map_baseline(df_runs,df_profiles,u_age,u_w,target_km,level):
    if df_runs.empty:
        return {"athlete_id":None,"baseline_pace":7.0,"baseline_hr":150,
                "athlete_age":u_age,"athlete_weight":u_w}
    prof=df_profiles.copy()
    prof["age_f"]=prof["age"].fillna(u_age)
    prof["weight_f"]=prof["weight"].fillna(u_w)
    rows=[]
    for aid in df_runs["athlete_id"].unique():
        r=df_runs[df_runs["athlete_id"]==aid]
        r=experience_window_filter(r,level)
        near=r[(r["distance_km"]>=target_km-1)&(r["distance_km"]<=target_km+1)]
        use=near if not near.empty else r
        med_p=use["pace_min_per_km"].median()
        med_hr=use["average_heartrate"].median()
        p=prof[prof["athlete_id"]==aid]
        a_f=int(p["age_f"].iloc[0]) if not p.empty else u_age
        w_f=float(p["weight_f"].iloc[0]) if not p.empty else u_w
        rows.append({"athlete_id":aid,"median_pace":med_p,"median_hr":med_hr,
                     "athlete_age":a_f,"athlete_weight":w_f})
    dfm=pd.DataFrame(rows)
    dfm["score"]=(dfm["athlete_weight"]-u_w).abs()+0.5*(dfm["athlete_age"]-u_age).abs()
    ch=dfm.sort_values("score").iloc[0]
    return {"athlete_id":ch["athlete_id"],"baseline_pace":float(ch["median_pace"]),
            "baseline_hr":float(ch["median_hr"]) if pd.notna(ch["median_hr"]) else 150,
            "athlete_age":int(ch["athlete_age"]),"athlete_weight":float(ch["athlete_weight"])}

base=map_baseline(df_runs,df_profiles,age,weight,target_distance,fitness_level)
age_gap=age-base["athlete_age"]; weight_gap=weight-base["athlete_weight"]
x_pace=base["baseline_pace"]*(1+0.005*age_gap)*(1+0.003*weight_gap)
x_pace=clamp(x_pace,*LEVEL_RANGE[fitness_level]); x_hr=base["baseline_hr"]

print(f"📌 Baseline athlete {base['athlete_id']} | {base['athlete_age']}y | {base['athlete_weight']:.1f}kg")
print(f"   Dist-specific pace={base['baseline_pace']:.2f} → adjusted x={x_pace:.2f} | HR≈{int(x_hr)}")

# ---------- 4) Build Blocks ----------
# Tempo caps & taper caps (distance fractions of target)
# 5/10K: 40–60% in build/peak; taper cap reduced
# 21/42K: 25–40% in build/peak; taper cap reduced
TEMPO_CAP_BUILD = {5:(0.40,0.60), 10:(0.40,0.60), 21:(0.25,0.40), 42:(0.25,0.40)}
TEMPO_CAP_TAPER = {5:(0.30,0.45), 10:(0.30,0.45), 21:(0.20,0.35), 42:(0.20,0.35)}

# Time-based runs: build window vs taper window
TIME_RUN = {5:(20,40), 10:(30,75), 21:(30,120), 42:(30,210)}
TAPER_TIME = {5:(15,20), 10:(30,45), 21:(45,60), 42:(45,60)}

# --- Long run ---
def long_run_km(w):
    if w<pre_taper:
        prog=(w+1)/pre_taper
        return round(0.25*target_distance+(0.80*target_distance-0.25*target_distance)*prog,1)
    t=w-pre_taper
    seq={5:[0.5,0.0],10:[0.5,0.25,0.0],21:[0.5,0.25,0.0],42:[0.6,0.5,0.25,0.0]}[target_distance]
    return round(seq[min(t,len(seq)-1)]*target_distance,1)

def long_run_pace(w):
    if w<pre_taper:
        frac=w/max(1,pre_taper-1)
        return x_pace+(0.40-0.25*frac)
    return x_pace+0.15

# --- Tempo distance progression with caps + taper ---
def tempo_km(week_idx, in_taper):
    if in_taper:
        lo, hi = TEMPO_CAP_TAPER[target_distance]
        # During taper: progress *downward* from hi to lo across taper weeks
        taper_pos = (week_idx - pre_taper + 1) / max(1, TAPER_WKS)  # 0→1 over taper
        frac = hi - (hi - lo) * taper_pos
    else:
        lo, hi = TEMPO_CAP_BUILD[target_distance]
        # Build/peak: progress upward from lo to hi across pre-taper weeks
        frac = lo + (hi - lo) * ((week_idx + 1) / max(1, pre_taper))
    return round(max(lo, min(hi, frac)) * target_distance, 1)

# --- Time-based progression with taper durations ---
def time_minutes(week_idx, in_taper):
    if in_taper:
        mn, mx = TAPER_TIME[target_distance]
        # In taper: drift toward the *lower* end of taper band
        taper_pos = (week_idx - pre_taper + 1) / max(1, TAPER_WKS)  # 0→1
        mins = mx - (mx - mn) * taper_pos
    else:
        mn, mx = TIME_RUN[target_distance]
        # Build/peak: ramp from mn to mx across pre-taper weeks
        mins = mn + (mx - mn) * ((week_idx + 1) / max(1, pre_taper))
    return int(round(mins))

# --- Interval Rest Mapping ---
def interval_rest(total_m, level):
    rules={
        "novice":[(1600,3200,150),(3200,4800,120),(4800,6400,120)],
        "intermediate":[(1600,3700,75),(3700,5800,90),(5800,7900,120),(7900,10000,150)],
        "advanced":[(2400,4300,60),(4300,6200,90),(6200,8100,120),(8100,10000,150)]
    }
    for lo,hi,rest in rules[level]:
        if lo<=total_m<=hi: return rest
    return 120

# --- Interval selection (no intervals in taper) ---
def interval_for_week(level, wk, in_taper):
    if in_taper: return None
    rules={
        5:{"novice":[(400,4),(600,4)],
           "intermediate":[(400,4),(600,4),(600,6)],
           "advanced":[(600,4),(800,4)]},
        10:{"novice":[(400,4),(600,4),(800,4)],
            "intermediate":[(400,4),(600,6),(800,6)],
            "advanced":[(600,4),(800,6),(1000,6)]},
        21:{"novice":[(400,4),(600,4),(800,6)],
            "intermediate":[(400,4),(600,6),(800,8),(1000,6)],
            "advanced":[(400,4),(600,6),(800,8),(1000,10)]},
        42:{"novice":[(400,4),(600,6),(800,8),(1000,8)],
            "intermediate":[(400,4),(600,6),(800,8),(1000,10)],
            "advanced":[(400,4),(600,6),(800,8),(1000,10)]}
    }
    seq=rules[target_distance][level]
    idx=min(wk,len(seq)-1)
    d,r=seq[idx]
    total=d*r; rest=interval_rest(total,level)
    wu_cd=round(1.0+(max(0,r-4)/6.0)*1.5,1)
    return {"dist_m":d,"reps":r,"rest":rest,"wu_cd_km":wu_cd}

# ---------- 5) Patterns ----------
pattern3=["ST","Run","ST","Run","ST","Rest","Long"]
pattern4A=["Run","ST","Run","ST","Run","ST","Long"]
pattern4B=["Run","ST","Run","ST","Run","Rest","Long"]

# ---------- 6) Build Weekly Plan ----------
rows=[]
for wk in range(total_weeks):
    in_taper = wk >= pre_taper
    is_final = (wk == total_weeks-1)
    use_b2b = (target_distance in (21,42)) and (wk in (pre_taper-2,pre_taper-1)) and not in_taper
    deload  = ((wk+1)%4==0)  # every 4th week deload

    if available_run_days==3:
        pattern=pattern3[:]; desired_st=3
    else:
        pattern=pattern4A[:] if option_4day=="A" else pattern4B[:]
        desired_st=3 if option_4day=="A" else 2

    days=["Rest"]*7

    # --- Final taper week: only Easy + Time; use *taper* time band
    if is_final:
        easy_km = round(target_distance*(0.45 if target_distance<=10 else 0.30),1)
        days[1]=f"Easy Run: {easy_km} km @ {mmss(x_pace+0.6)}"
        days[3]=f"Time Run: {time_minutes(wk, True)} min (Endurance Focus)"
        st=0
        for i in [0,4,5]:
            if st<desired_st and days[i]=="Rest":
                days[i]=strength_choice(); st+=1
        rows.append([wk+1]+days); continue

    # --- Long run logic (freeze distance on deload week) ---
    if deload and wk>0:
        prev_sunday = rows[-1][7]
        m = re.search(r'(\d+\.?\d*)\s*km', prev_sunday or "")
        long_km = float(m.group(1)) if m else long_run_km(wk)
    else:
        long_km = long_run_km(wk)
    long_p = long_run_pace(wk)

    # Mon–Fri run roster
    alt = "Tempo" if wk % 2 == 0 else "Intervals"
    run_order = (["Easy",alt] if available_run_days==3 else ["Easy","Time",alt])
    run_idx=0

    for i,tok in enumerate(pattern):
        if i==6: continue  # Sunday later
        if tok=="Run":
            rtype=run_order[run_idx%len(run_order)]
            if rtype=="Easy":
                dist=round(max(1.0,float(long_km)*0.6),1)
                pace=x_pace+0.6 if deload else x_pace+random.uniform(0.5,0.75)
                days[i]=f"Easy Run: {dist} km @ {mmss(pace)}"
            elif rtype=="Tempo":
                dist=tempo_km(wk, in_taper)
                pace=(x_pace if deload else x_pace - random.uniform(0.50,0.75))
                days[i]=f"Tempo Run: {dist} km @ {mmss(pace)}"
            elif rtype=="Intervals":
                iv=interval_for_week(fitness_level,wk,in_taper)
                if iv:
                    pace=x_pace-random.uniform(1.0,1.2)
                    days[i]=(f"Intervals: {iv['reps']}x{iv['dist_m']}m @ {mmss(pace)} "
                             f"(WU/CD {iv['wu_cd_km']} km, Rest {iv['rest']}s)")
                else:
                    # Taper replacement
                    dist=round(max(1.0,float(long_km)*0.6),1)
                    days[i]=f"Easy Run: {dist} km @ {mmss(x_pace+0.5)}"
            elif rtype=="Time":
                mins=time_minutes(wk, in_taper)
                days[i]=f"Time Run: {mins} min (Endurance Focus)"
            run_idx+=1
        elif tok=="ST":
            days[i]=strength_choice()

    # --- Back-to-back weekends for 21K/42K (two weeks before taper) ---
    if use_b2b:
        sat_frac,sun_frac=((0.4,0.6) if wk==pre_taper-2 else (0.25,0.75))
        days[5]=f"Long Run: {round(target_distance*sat_frac,1)} km @ {mmss(long_p)}"
        days[6]=f"Long Run: {round(target_distance*sun_frac,1)} km @ {mmss(long_p)}"
        # Protect Friday
        if "Run" in days[4] or "Intervals" in days[4]:
            days[4]="Rest" if option_4day=="B" else strength_choice()
    else:
        days[6]=f"Long Run: {long_km} km @ {mmss(long_p)}"

    # --- Ensure desired ST count ---
    st_ct=sum(1 for d in days if d.startswith("Strength"))
    i=0
    while st_ct<desired_st and i<7:
        if days[i]=="Rest":
            days[i]=strength_choice(); st_ct+=1
        i+=1

    rows.append([wk+1]+days)

plan_df=pd.DataFrame(rows,columns=["Week","Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
print(f"\n✅ Plan Ready: {target_distance}km | {fitness_level} | {total_weeks}w | {available_run_days} runs | Opt={option_4day or '-'}")
display(plan_df)
