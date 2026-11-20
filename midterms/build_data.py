#!/usr/bin/env python3
"""Builds midterms/data.json from the race list below.
Scheduled runs edit the `status`, `result`, `margin` fields (and `projection`, `runs`) in data.json
directly; this script only exists to regenerate the baseline."""
import json, datetime

COMP = {"Toss-up": 1.0, "Lean": 0.8, "Likely": 0.5, "Solid": 0.2}

# race, office, state, D, Dscore, Durl, R, Rscore, Rurl, wt, rating, close, note
R = [
 ("GA Gov","Gov","GA","Keisha Lance Bottoms",-2,"https://www.ajc.com/politics/2026/09/where-they-stand-jackson-bottoms-on-data-centers/","Rick Jackson",0,"https://www.ajc.com/politics/2026/09/where-they-stand-jackson-bottoms-on-data-centers/",3,"Toss-up","7:00 pm","Bottoms: statewide pause; Jackson: guardrails + local say"),
 ("SC Sen","Sen","SC","Annie Andrews",-2,"https://www.wtoc.com/2026/10/12/sc-senate-candidates-clash-over-data-center-expansion-debate/","Darline Graham (inc)",1,"https://www.wtoc.com/2026/10/12/sc-senate-candidates-clash-over-data-center-expansion-debate/",2,"Lean","7:00 pm","Andrews: 2-yr moratorium; Graham: opposes pause"),
 ("OR Gov","Gov","OR","Tina Kotek (inc)",-2,"https://www.klcc.org/politics-government/2026-09-08/gov-tina-kotek-says-she-now-supports-a-data-center-moratorium","Christine Drazan",1,"https://www.klcc.org/politics-government/2026-09-08/gov-tina-kotek-says-she-now-supports-a-data-center-moratorium",2,"Lean","11:00 pm","Kotek: statewide moratorium in place; Drazan: keep incentives"),
 ("NV Gov","Gov","NV","Aaron Ford",-1,"https://www.kolotv.com/2026/09/08/nevada-gubernatorial-candidates-weigh-data-centers/","Joe Lombardo (inc)",1,"https://www.kolotv.com/2026/09/08/nevada-gubernatorial-candidates-weigh-data-centers/",2,"Toss-up","10:00 pm","Ford: audit abatements; Lombardo: 'gold rush'"),
 ("MI Sen","Sen","MI","Abdul El-Sayed",-2,"https://katv.com/news/nation-world/senate-seeker-michan-democrat-abdul-el-sayed-digs-in-against-ai-backs-kill-switch-bill-republican-mike-rogers-2026-midterm-elections","Mike Rogers",0,"https://michiganadvance.com/?p=110527",2,"Lean","8:00 pm","El-Sayed: kill-switch bill, moratoria; Rogers: mixed"),
 ("NC Sen","Sen","NC","Roy Cooper",-1,"https://baynews9.com/fl/tampa/news/2026/08/27/data-centers-roy-cooper-whatley","Michael Whatley",1,"https://baynews9.com/fl/tampa/news/2026/08/27/data-centers-roy-cooper-whatley",2,"Lean","7:30 pm","Cooper: local final say; Whatley: opposition 'ginned up'"),
 ("OH Sen","Sen","OH","Sherrod Brown",-1,"https://newsweek.com/sherrod-browns-ai-data-center-views-as-husteds-bill-blocked-by-democrats-12514153","Jon Husted (inc)",0,"https://www.husted.senate.gov/news/in-the-news/sen-jon-husted-introduces-bill-to-stop-harmful-ai-chatbot-interactions-with-children",3,"Toss-up","7:30 pm","Brown: DC skeptic; Husted: mixed"),
 ("GA Sen","Sen","GA","Jon Ossoff (inc)",-2,"https://www.ajc.com/politics/2026/09/jon-ossoff-calls-for-inspectors-at-ai-research-labs-amid-industry-fears/","Mike Collins",0,"https://www.wtoc.com/2026/10/09/ossoff-collins-discuss-tariffs-data-centers-georgia-senate-debate/",3,"Likely","7:00 pm","Ossoff: lab inspectors, AI treaty; Collins: no record"),
 ("KS Gov","Gov","KS","Cindy Holscher",-2,"https://www.kshb.com/news/local-news/data-centers/masterson-holscher-diverge-on-data-centers-as-kansas-governors-race-heats-up","Ty Masterson",1,"https://www.kshb.com/news/local-news/data-centers/masterson-holscher-diverge-on-data-centers-as-kansas-governors-race-heats-up",1,"Toss-up","8:00 pm","Holscher: statewide moratorium; Masterson: 'win the AI race'"),
 ("PA-01","House","PA","Bob Harvie",-2,"https://whyy.org/articles/brian-fitzpatrick-bob-harvie-data-center-ad-congressional-race/","Brian Fitzpatrick (inc)",1,"https://www.inquirer.com/politics/election/bob-harvie-ai-data-centers-stance-tv-ad-20260910.html",2,"Toss-up","8:00 pm","Harvie: moratorium; Fitzpatrick: Amazon $20B backer"),
 ("MI-07","House","MI","Will Lawrence",-2,"https://www.michiganpublic.org/politics-government/2026-10-30/barrett-lawrence-target-data-centers-to-bridge-divides-in-tight-u-s-house-race","Tom Barrett (inc)",1,"https://www.newsweek.com/pro-data-center-lawmakers-risk-midterms-12506196",2,"Toss-up","8:00 pm","Lawrence: full moratorium"),
 ("TX Gov","Gov","TX","Gina Hinojosa",-2,"https://www.fox7austin.com/news/hinojosa-urges-gov-abbott-pause-new-data-centers-until-lawmakers-act","Greg Abbott (inc)",-1,"https://thehill.com/homenews/state-watch/5920754-abbott-texas-data-center-limits/amp/",3,"Lean","8:00 pm","Hinojosa: moratorium; Abbott: rural DC ban, TRAIGA"),
 ("FL Gov","Gov","FL","David Jolly",-2,"https://www.fox35orlando.com/news/florida-governor-candidates-differ-ai-data-centers-property-taxes","Byron Donalds",1,"https://nbcnews.com/politics/2026-election/super-pac-backed-ai-titans-pledges-5-million-boost-byron-donalds-run-f-rcna258612",1,"Lean","7:00/8:00 pm","Jolly: opposes DCs in FL; Donalds: Leading the Future $5M"),
 ("CO-08","House","CO","Manny Rutinel",-2,"https://www.newsweek.com/colorado-ai-primary-democratic-tech-donors-rutinel-12145533","Gabe Evans (inc)",1,"https://coloradotimesrecorder.com/2026/02/theyre-afraid-the-ai-might-misgender-someone-says-congressman-of-ai-regulations/76835/",2,"Lean","9:00 pm","Rutinel sponsored CO AI Act"),
 ("OH-09","House","OH","Marcy Kaptur (inc)",-1,"https://ohiocapitaljournal.com/2026/08/10/ohios-9th-congressional-district-race-the-candidates-records-on-data-centers/","Derek Merrin",1,"https://ohiocapitaljournal.com/2026/08/10/ohios-9th-congressional-district-race-the-candidates-records-on-data-centers/",3,"Lean","7:30 pm",""),
 ("OH-15","House","OH","Don Leonard",-1,"https://abc6onyourside.com/news/local/district-15-candidates-explain-to-abc6-why-they-should-be-voted-into-office-mike-carey-don-leonard-franklin-madison-fayette-clark-miami-shelby-congress","Mike Carey (inc)",1,"https://www.newsweek.com/where-ohio-republicans-stand-on-data-centers-amid-growing-backlash-12531253",3,"Lean","7:30 pm","New Albany / Licking Co. cluster"),
 ("VA-05","House","VA","Tom Perriello",-1,"https://newrepublic.com/post/216402/dems-might-just-shot-unlikely-district","John McGuire (inc)",1,"https://www.newsweek.com/america-data-center-capital-virginia-house-battleground-midterms-12520217",3,"Lean","7:00 pm","Perriello: anti-DC ads"),
 ("IA Sen","Sen","IA","Josh Turek",0,"https://www.wowt.com/2026/10/08/where-us-senate-candidates-agreed-disagreed-1st-debate/","Ashley Hinson",1,"https://ashleyhinson.com/op-ed-rep-ashley-hinson-congress-needs-to-ensure-that-the-ai-future-belongs-to-our-kids-not-to-beijing",2,"Toss-up","9:00 pm","Hinson: regulation 'misguided'"),
 ("AL Gov","Gov","AL","Doug Jones",-2,"https://www.lagniappemobile.com/news/data-centers-tuberville-full-speed-ahead-jones-urges-pause/article_9760db32-07ba-49cd-b731-2f45d0eed490.amp.html","Tommy Tuberville",2,"https://www.lagniappemobile.com/news/data-centers-tuberville-full-speed-ahead-jones-urges-pause/article_9760db32-07ba-49cd-b731-2f45d0eed490.amp.html",2,"Solid","8:00 pm","Jones: pause; Tuberville: 'Space Race'"),
 ("PA-10","House","PA","Janelle Stelson",-1,"https://www.cityandstatepa.com/politics/2026/10/pa-10-debate-night-scott-perry-and-janelle-stelson-spar-over-economy-iran-war-and-elections/416604/","Scott Perry (inc)",1,"https://www.newsweek.com/pro-data-center-lawmakers-risk-midterms-12506196",2,"Lean","8:00 pm",""),
 ("WI-03","House","WI","Rebecca Cooke",-2,"https://www.wispolitics.com/2026/cooke-campaign-new-rebecca-cooke-ad-calls-van-orden-out-pushes-for-data-center-moratorium-sold-us-out/","Derrick Van Orden (inc)",0,"https://urbanmilwaukee.com/?p=1001087",2,"Lean","9:00 pm","Cooke: moratorium"),
 ("VA-01","House","VA","Shannon Taylor",-1,"https://www.axios.com/local/richmond/2026/09/09/virginia-data-centers-midterm-election-2026","Rob Wittman (inc)",0,"https://www.axios.com/local/richmond/2026/09/09/virginia-data-centers-midterm-election-2026",3,"Toss-up","7:00 pm",""),
 ("VA-07","House","VA","Eugene Vindman (inc)",-1,"https://vindman.house.gov/2026/10/29/vindman-pushes-for-greater-data-center-oversight-as-virginians-face-rising-utility-bills/","Douglas Ollivant",1,"https://www.vpm.org/elections/2026-10-19/va07-district-preview-ollivant-vindman-lopez-congress-keena/",3,"Likely","7:00 pm","Vindman: Data Center Oversight Act"),
 ("AZ-01","House","AZ","Amish Shah",-1,"https://www.kjzz.org/politics/2026-10-08/arizona-1st-congressional-district-candidates-share-different-views-on-data-centers-in-debate","Jay Feely",0,"https://www.kjzz.org/politics/2026-10-08/arizona-1st-congressional-district-candidates-share-different-views-on-data-centers-in-debate",3,"Lean","9:00 pm",""),
 ("AZ-06","House","AZ","JoAnna Mendoza",-1,"https://coppercourier.com/news/elections/arizona-district-six-congress/","Juan Ciscomani (inc)",0,"https://coppercourier.com/news/elections/arizona-district-six-congress/",3,"Lean","9:00 pm",""),
 ("NM Gov","Gov","NM","Deb Haaland",-2,"https://www.abqjournal.com/news/deb-haaland-vows-to-impose-data-center-moratorium-via-executive-order-if-elected-governor/3123658","Gregg Hull",1,"https://www.abqjournal.com/news/deb-haaland-vows-to-impose-data-center-moratorium-via-executive-order-if-elected-governor/3123658",2,"Solid","9:00 pm","Haaland: day-one moratorium EO; Stargate Jupiter exposure"),
 ("LA Sen","Sen","LA","Jamie Davis",-2,"https://www.wwno.org/2026-10-19/nov-3-election-guide-meet-the-u-s-senate-candidates","Julia Letlow",1,"https://dailycaller.com/2026/09/16/leading-the-future-ai-super-pac-midterm-ads-darline-graham/",2,"Solid","9:00 pm","Meta Hyperion exposure"),
 ("ME Sen","Sen","ME","Troy Jackson",-2,"https://newsweek.com/susan-collins-vs-troy-jackson-on-ai-data-centers-amid-maine-voters-fears-12621762","Susan Collins (inc)",-1,"https://newsweek.com/susan-collins-vs-troy-jackson-on-ai-data-centers-amid-maine-voters-fears-12621762",1,"Toss-up","8:00 pm","Senate control"),
 ("KS Sen","Sen","KS","Adam Hamilton",-1,"https://www.hppr.org/2026-10-21/control-of-the-senate-goes-through-kansas-marshall-and-hamilton-clash-at-last-debate","Roger Marshall (inc)",0,"https://www.semafor.com/article/07/22/2026/republican-senator-roger-marshall-rails-against-ai-data-centers",1,"Toss-up","8:00 pm","Senate control"),
 ("NE Sen","Sen","NE","Dan Osborn (I)",-1,"https://abcnews4.com/news/nation-world/nebraska-independent-dan-osborn-embraces-safe-strategy-in-red-state-senate-race-ai-congress-midterm-elections","Pete Ricketts (inc)",0,"https://www.longtermwiki.com/races/fmor5oDhMK",2,"Likely","9:00 pm",""),
 ("TN-09","House","TN","Justin J. Pearson",-2,"https://www.wate.com/news/election-news/brent-taylor-vs-justin-pearson-meet-the-9th-congressional-district-candidates/amp/","Brent Taylor",0,"https://www.wate.com/news/election-news/brent-taylor-vs-justin-pearson-meet-the-9th-congressional-district-candidates/amp/",2,"Likely","8:00 pm","xAI Colossus exposure"),
 ("NY Gov","Gov","NY","Kathy Hochul (inc)",-2,"https://ny1.com/nyc/all-boroughs/politics/2026/07/15/hochul-blakeman-data-center-moratorium","Bruce Blakeman",2,"https://ny1.com/nyc/all-boroughs/politics/2026/07/15/hochul-blakeman-data-center-moratorium",1,"Solid","9:00 pm","RAISE Act + moratorium vs scrap it"),
 ("PA-08","House","PA","Paige Cognetti",-1,"https://www.pbs.org/newshour/politics/pennsylvania-democrat-targets-data-centers-in-drive-to-oust-republican-from-house-seat","Rob Bresnahan (inc)",0,"https://www.spotlightpa.org/news/2026/10/midterm-congress-elections-pennsylvania-data-centers-environment/",2,"Lean","8:00 pm",""),
 ("PA-07","House","PA","Bob Brooks",-1,"https://www.spotlightpa.org/news/2026/10/midterm-congress-elections-pennsylvania-data-centers-environment/","Ryan Mackenzie (inc)",0,"https://www.newsweek.com/pro-data-center-lawmakers-risk-midterms-12506196",2,"Lean","8:00 pm",""),
 ("IN-05","House","IN","J.D. Ford",-1,"https://www.larryinfishers.com/2026/09/10/ford-spartz-indiana-data-center-debate/","Victoria Spartz (inc)",0,"https://www.larryinfishers.com/2026/09/10/ford-spartz-indiana-data-center-debate/",2,"Lean","6:00/7:00 pm","LEAP district"),
 ("WI-01","House","WI","Mitchell Berman",0,"https://www.fox6now.com/news/wisconsin-election-congress-steil-berman-102626","Bryan Steil (inc)",1,"https://www.fox6now.com/news/wisconsin-election-congress-steil-berman-102626",2,"Lean","9:00 pm","Microsoft Fairwater"),
 ("NY-17","House","NY","Cait Conley",-1,"https://insideclimatenews.org/?p=115399","Mike Lawler (inc)",0,"https://insideclimatenews.org/?p=115399",1,"Toss-up","9:00 pm",""),
 ("PA Gov","Gov","PA","Josh Shapiro (inc)",-1,"https://www.spotlightpa.org/news/2026/07/garrity-shapiro-data-center-governor-race-2026-pennsylvania-elections/","Stacy Garrity",0,"https://www.spotlightpa.org/news/2026/07/garrity-shapiro-data-center-governor-race-2026-pennsylvania-elections/",2,"Solid","8:00 pm","GRID executive order"),
 ("IL Gov","Gov","IL","JB Pritzker (inc)",-1,"https://capitolnewsillinois.com/news/data-centers-emerging-as-key-issue-in-illinois-governors-race/","Darren Bailey",0,"https://capitolnewsillinois.com/news/data-centers-emerging-as-key-issue-in-illinois-governors-race/",2,"Solid","8:00 pm",""),
 ("TN Gov","Gov","TN","Jerri Green",-1,"https://www.wsmv.com/2026/10/26/tn-candidates-governor-explain-how-theyd-handle-data-centers-if-elected/","Marsha Blackburn",0,"https://www.axios.com/2026/03/18/blackburn-updated-ai-plan-trump",2,"Solid","8:00 pm",""),
 ("KY Sen","Sen","KY","Charles Booker",0,"https://www.ballotpedia.org/United_States_Congress_elections,_2026","Andy Barr",1,"https://www.newsweek.com/ai-politics/how-ai-upended-politics-and-left-lawmakers-scrambling-to-pick-a-side-12501075",2,"Solid","6:00/7:00 pm",""),
 ("MS Sen","Sen","MS","Scott Colom",0,"https://www.ballotpedia.org/United_States_Congress_elections,_2026","Cindy Hyde-Smith (inc)",1,"https://dailycaller.com/2026/09/16/leading-the-future-ai-super-pac-midterm-ads-darline-graham/",2,"Solid","8:00 pm",""),
 ("SC Gov","Gov","SC","Jermaine Johnson",-1,"https://www.wbtv.com/2026/10/26/south-carolina-governors-race-where-alan-wilson-jermaine-johnson-stand-key-issues/","Alan Wilson",0,"https://www.wbtv.com/2026/10/26/south-carolina-governors-race-where-alan-wilson-jermaine-johnson-stand-key-issues/",2,"Solid","7:00 pm",""),
 ("TX Sen","Sen","TX","James Talarico",-1,"https://www.texastribune.org/2026/07/22/texas-james-talarico-data-centers-regulation-senate-2026/","Ken Paxton",-1,"https://www.texastribune.org/2026/08/24/ken-paxton-james-talarico-data-centers-senate-texas/",3,"Toss-up","8:00/9:00 pm","Both restrictive; Senate control"),
 ("OH Gov","Gov","OH","Amy Acton",-1,"https://www.wcpo.com/news/state/state-ohio/data-centers-have-become-a-political-issue-heres-where-the-gubernatorial-candidates-stand","Vivek Ramaswamy",-1,"https://signalohio.org/ramaswamy-data-center-plan-free-electricity-november-election-2026/",3,"Lean","7:30 pm","Both restrictive"),
 ("AZ Gov","Gov","AZ","Katie Hobbs (inc)",0,"https://www.abc15.com/news/state/gov-katie-hobbs-congressman-andy-biggs-find-common-ground-on-data-centers","Andy Biggs",0,"https://www.abc15.com/news/state/gov-katie-hobbs-congressman-andy-biggs-find-common-ground-on-data-centers",3,"Likely","9:00 pm","Both: repeal tax breaks, no moratorium"),
 ("WI Gov","Gov","WI","David Crowley",0,"https://wisconsinwatch.org/2026/10/wisconsin-crowley-tiffany-data-centers-support-artificial-intelligence-governor-election/","Tom Tiffany",0,"https://wisconsinwatch.org/2026/10/wisconsin-crowley-tiffany-data-centers-support-artificial-intelligence-governor-election/",2,"Lean","9:00 pm",""),
 ("MI Gov","Gov","MI","Jocelyn Benson",0,"https://bridgemi.com/michigan-government/where-michigan-gubernatorial-candidates-stand-on-data-centers/","John James",0,"https://bridgemi.com/michigan-government/where-michigan-gubernatorial-candidates-stand-on-data-centers/",2,"Lean","8:00 pm",""),
 ("IA Gov","Gov","IA","Rob Sand",-1,"https://political.org/2026/10/28/iowa-governors-race-rob-sand-and-zach-lahn-clash-on-abortion-school-choice-and-gun-checks-agree-on-data-center-tax-breaks-in-final-debate/","Zach Lahn",-1,"https://political.org/2026/10/28/iowa-governors-race-rob-sand-and-zach-lahn-clash-on-abortion-school-choice-and-gun-checks-agree-on-data-center-tax-breaks-in-final-debate/",2,"Lean","9:00 pm","Both restrictive"),
 ("NH Sen","Sen","NH","Chris Pappas",-2,"https://www.nhpr.org/politics/2026-10-30/where-do-nh-candidates-stand-on-ai-and-data-centers-election-2026-midterms","John E. Sununu",-1,"https://www.nhpr.org/politics/2026-10-30/where-do-nh-candidates-stand-on-ai-and-data-centers-election-2026-midterms",0,"Lean","8:00 pm","No data centers; Senate control"),
 ("AK Sen","Sen","AK","Mary Peltola",0,"https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265","Dan Sullivan (inc)",1,"https://www.newsweek.com/ai-data-center-war-where-democrats-republicans-in-key-senate-races-stand-12354265",0,"Toss-up","12:00 am","No data centers; Senate control"),
 ("NH Gov","Gov","NH","Cinde Warmington",-2,"https://www.nhpr.org/politics/2026-10-30/where-do-nh-candidates-stand-on-ai-and-data-centers-election-2026-midterms","Kelly Ayotte (inc)",-2,"https://www.nhpr.org/politics/2026-08-21/data-centers-ayotte-supports-moratorium-datacenters-nh",0,"Likely","8:00 pm","Both restrictive"),
 ("MN Gov","Gov","MN","Amy Klobuchar",0,"https://www.kaxe.org/elections/2026-10-20/here-are-4-takeaways-from-the-first-demuth-klobuchar-debate","Lisa Demuth",0,"https://www.kaxe.org/elections/2026-10-20/here-are-4-takeaways-from-the-first-demuth-klobuchar-debate",1,"Solid","9:00 pm",""),
]

OFFICE_MULT = {"Sen": 1.0, "Gov": 1.0, "House": 0.5}
races = []
for (race, office, state, d, ds, du, r, rs, ru, wt, rating, close, note) in R:
    gap = abs(ds - rs)
    comp = COMP[rating]
    rel = round(gap * wt * OFFICE_MULT[office] * comp, 1)
    if gap == 0:
        ifd = "neutral"
    else:
        ifd = "headwind" if ds < rs else "tailwind"
    races.append({
        "race": race, "office": office, "state": state,
        "d": d, "dScore": ds, "dUrl": du,
        "r": r, "rScore": rs, "rUrl": ru,
        "gap": gap, "wt": wt, "rating": rating, "comp": comp,
        "relevance": rel, "ifD": ifd,
        "status": "Not called", "winner": "", "caller": "", "margin": "",
        "close": close, "note": note,
    })
races.sort(key=lambda x: -x["relevance"])

data = {
    "title": "Midterms 2026 — AI Stance × Data Centers × Equities",
    "updated": "2026-11-03T12:00:00-05:00",
    "doc": "https://claude.ai/artifact/RpLp8eXk8xffU9Ggyszesm",
    "projection": {
        "label": "Modest headwind, largely priced",
        "lead": "Pre-results baseline. Democratic control of the House and probably the Senate raises the odds of binding federal AI legislation and tighter data-center cost-allocation rules, but federal preemption of state AI laws was already dead after the 99-1 Senate vote, and the data-center backlash now runs through both parties, so the party-control signal is weaker than a pure D/R map implies.",
        "bullets": [
            "Market-moving outcomes tonight are the surprises, not the base case.",
            "Most negative for AI equities: Bottoms wins GA Gov (8.5 GW under construction) and signals a real pause; moratorium candidates win PA-01, MI-07, CO-08 or SC Sen; Democrats reach 51+ with El-Sayed, Brown and Jackson in the caucus.",
            "Most positive: Drazan reverses Oregon's moratorium; Lombardo holds Nevada; Republicans hold the Senate; Fitzpatrick and Barrett survive moratorium challengers.",
            "Capped either way: Ratepayer Protection Act passed the House 417-3, and the largest capex commitments sit in states where tonight's winner cannot or has not pledged to stop them."
        ],
        "chambers": {"senate": "Not called (53 R – 47 D going in; D needs net +4)", "house": "Not called (219 R-aligned – 214 D going in)"}
    },
    "runs": [
        {"time": "2026-11-03 12:00 ET", "called": "— (baseline)", "change": "Set: modest headwind, largely priced", "note": "53 races scored; 30-state data-center map; Cook/Sabato final ratings."}
    ],
    "races": races,
}
with open("/home/claude/fedspeak/midterms/data.json", "w") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
print(len(races), "races written")
