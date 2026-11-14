# UK Middle East field officers — verified source bank (11d-uk-middleeast.md)

Verified 2 Sep 2026 for the deliverable `uk-parts/11d-uk-middleeast.md` (religion-in-service-of-empire series): 17 field officers/proconsuls/agents (Cox, Arnold Wilson, Bell, Haldane, Lawrence, McMahon, Clayton, Storrs, Wauchope, Glubb, Kirkbride, Cornwallis, Ryan, Percy Sykes, Ironside, Bullard, Spears). Method: `curl -s -o /dev/null -w '%{http_code}' -L -A 'Mozilla/5.0'` per URL; archive.org items confirmed via `metadata/<id>` JSON (title/creator/date); full-text availability probed via `<id>_djvu.txt`; print books via OpenLibrary `search.json` + `/works/` pages. Reuse this bank instead of re-verifying in follow-up sessions (parent cluster files 11a/11b carry their own banks; this is the 11d one).

## Canonical Wikipedia titles (resolved — plain guesses that 404)
- `Arnold Wilson` (NOT `Arnold_Wilson_(administrator)`) | `Arthur Wauchope` (NOT `Arthur_Wauchope_(British_Army_officer)`) | `Henry McMahon` (NOT `Henry_McMahon,_1st_Baronet`) | `Andrew Ryan (diplomat)` | `Edmund Ironside, 1st Baron Ironside` | `Aylmer Haldane` | all others plain (Percy_Cox, Gilbert_Clayton, Ronald_Storrs, John_Bagot_Glubb, Alec_Kirkbride, Kinahan_Cornwallis, Percy_Sykes, Reader_Bullard, Edward_Spears, Gertrude_Bell, T._E._Lawrence).
- En-dash slugs fetch fine literally with curl (`McMahon–Hussein_correspondence`, `1936–39_Arab_revolt_in_Palestine`, `1920_Nebi_Musa_riots`) — do NOT percent-encode the dash; do NOT hyphenate it. All confirmed HTTP 200.
- Event anchors confirmed 200: Treaty_of_Darin, Treaty_of_Jeddah_(1927), 1920_Iraqi_revolt, 1921_Iraqi_monarchy_referendum, 1941_Iraqi_coup_d'%C3%A9tat, Anglo-Iraqi_War, Anglo-Soviet_invasion_of_Iran, 1921_Persian_coup_d'%C3%A9tat, Peel_Commission, Cairo_Conference_(1921), Sharifian_Solution, St_John_Philby, Saudi_Aramco.

## Wikipedia extracts API caps (new pitfall, hit live this session)
- `prop=extracts` + `exchars` is capped at **1200** (larger value → whole request fails with a `warnings` block). Whole-article extracts (no `exintro`) force **`exlimit=1`** — only the first title is returned, silently. ALWAYS inspect the `warnings` key in the JSON before trusting page count.
- `exintro=1&explaintext=1&exlimit=20&redirects=1` batches many titles in ONE call (lead paragraph only) — works as a cheap identity/role/date sweep across 10–20 figures and doubles as a title resolver (redirects=1). Use it to scope before deep-fetching individuals. Successfully swept all 17 figures in one call this session.
- Whole-article plaintext (for under-known figures) is fine one title per call, 2s apart, via `prop=extracts&explaintext=1&titles=X` (no exintro, no exchars).

## Archive.org identifiers (deliverable §primary sources)
| Figure | Item | Status |
|---|---|---|
| Arnold Wilson, *Loyalties: Mesopotamia 1914–1917* (1930) | `loyaltiesmesopot0000wils` (alt `in.ernet.dli.2015.77288`) | djvu.txt HTTP 200 = full text |
| Arnold Wilson, *Mesopotamia 1917–1920: A Clash of Loyalties* (1931) | `mesopotamia1917-1920wilson` (alt `mesopotamia191710000unse`) | [META] no public djvu (404) — lending-restricted |
| Bullard, *The Camels Must Go* (1961) | `camelsmustgo0000sirr` | [META] (djvu 401) |
| Ironside, *Time Unguarded* diaries 1937–40 (1962/74) | `timeunguardediro0000iron` | [META] (djvu 403) |
| Ironside, *High Road to Command* diaries **1920–22** (1972) — the Persia-coup volume | `highroadtocomman0000iron` | [META] — cite this one for Reza Khan/Dec 1920, not Time Unguarded |
| Ryan, *The Last of the Dragomans* (1951) | `lastofdragomans0000na` | [META] (djvu 401) |
| Kirkbride, *From the Wings: Amman Memoirs 1947–51* (1976) | `fromwingsammanme0000kirk` | HTTP 200 |
| Lawrence, *Secret Despatches from Arabia* (1939, ed. A.W. Lawrence) | `in.ernet.dli.2015.279222` | HTTP 200 (contains the Twenty-seven Articles) |
| Sykes, *The Glory of the Shia World* (1910) | `gloryofshiaworld00sykeuoft` | djvu.txt HTTP 200 = full text |
| Peel Report (Cmd 5479, 1937) — Wauchope-era primary | `palestine-royal-commission-report` | HTTP 200 |

Reuse (verified in sibling country files, re-checked 200 this session): Bell *Review of the Civil Administration* `reviewofciviladm00iraqrich`; Bell *Letters* vol.1 `lettersofgertrud01lady`; Bell originals gertrudebell.ncl.ac.uk; Storrs *Orientations* `orientations0000rona` + `in.ernet.dli.2015.174934`; Haldane *Insurrection in Mesopotamia, 1920* `32882019307837-theinsurrection`; Glubb *Story of the Arab Legion* `the-story-of-the-arab-legion-john-bagot-glubb-orig` (direct PDF) + *A Soldier with the Arabs* `soldierwitharabs0000sirj`.

## Non-archive primary texts (all HTTP 200)
- Lawrence, *Seven Pillars*: gutenberg.net.au/ebooks01/0100111h.html (full text).
- Lawrence, **'Twenty-seven Articles', Arab Bulletin, 20 Aug 1917**: https://www.bu.edu/mzank/Jerusalem/tx/lawrence.htm (Boston University host — header states source; the best live full-text copy found; no Wikisource copy).
- McMahon–Hussein correspondence: en.wikisource.org/wiki/McMahon–Hussein_Correspondence; official Cmd 5957 (1939) PDF: upload.wikimedia.org/wikipedia/commons/7/75/Correspondence_between_Sir_Henry_McMahon_and_the_Sherif_Hussein_of_Mecca_Cmd_5957.pdf.
- Treaty of Jeddah 1927 (British Treaty Series): treaties.fcdo.gov.uk/data/Library2/pdf/1927-TS0025.pdf.

## OpenLibrary /works/ keys (print secondaries — HTTP 200)
Townsend, *Proconsul to the Middle East: Sir Percy Cox* (2010) OL14990888W | Howell, *Daughter of the Desert* (2006) OL2016936W | Jeremy Wilson, *Lawrence of Arabia* (1989) OL722628W | Barr, *A Line in the Sand* (2011) OL16345802W | Spears, *Fulfilment of a Mission* (1977) OL6234896W — **not on archive.org at all**; OL works page is the verifiable record | Clayton, *An Arabian Diary* (1969) OL7209634W | Bullard, *Letters from Tehran* (1991) OL3643723W | Kirkbride, *From the Wings* (1976) OL6950210W. Kirkbride *A Crackle of Thorns* (1956) also: Google Books about-page `books.google.com/books/about/...?id=5bkLAAAAIAAJ` returns 200 (print-only).

## Status-code quirks (re-confirmed this session)
- TNA Discovery deep links → 202 (resolves; not dead). Iranica `coup-detat-of-1299-1921` → 403 (bot-block; cite with caveat).
- archive.org metadata API and details pages respond to `-A 'Mozilla/5.0'`; djvu probe codes: 200 = public full text; 401/403 = lending/restricted; 404 = no text derivative (item still citable as [META] via details page).

## Per-figure date anchors re-established this session (for reuse)
- Cox: Treaty of Darin 26 Dec 1915 (Darin, Tarut Island); Faisal proclaimed King of Iraq 23 Aug 1921 (referendum 16 Jul–11 Aug 1921, announced 96%); Uqair conference 1922; Anglo-Persian Agreement 9 Aug 1919 (negotiated/signed in Tehran by Cox with PM Vossug ed Dowleh).
- Clayton: signed Treaty of Jeddah 20 May 1927; Civil Secretary Palestine 1922–25; d. in post as HC-designate Iraq, 11 Sep 1929.
- Storrs: created the office of Grand Mufti of Jerusalem 1918 (first holder Kamil al-Husayni); Nebi Musa riots Apr 1920 under his governorship; *Orientations* 1937.
- Wauchope: HC Palestine & Trans-Jordan Oct 1931–1938; Jaffa Old City demolition Jun 1936; Jewish population 174,606→329,358 across his term (Hyamson, *Palestine: A Policy*, 1941, "heyday of Zionist history").
- Cornwallis: Arab Bureau director 1916–20 (ed. *Arab Bulletin*); Faisal's adviser 1921–35; Ambassador from 2 Apr 1941 (Rashid Ali coup 1 Apr 1941); 230 civilians evacuated Baghdad→Habbaniya.
- Ironside: Norperforce GOC from 26 Sep 1920; appointed Reza Khan to Cossack command Dec 1920; War Office report 8 Dec 1920 ("depart in peace and honour"); coup 21 Feb 1921. Book-anchored (Ghani 2001, Ullman 1972, Camb. Hist. Iran vol. 7 — no URLs; 07-iran.md).
- Bullard: consul Jeddah 1923–25, minister 1936–39; Tehran 1939–46 (1941 invasion; Reza abdication 16 Sep 1941; Zahedi removal ca. 1943 with Gen. Baillon — Wikipedia/Maclean).
- Sykes: SPR commander 1916–18 (raised ~7,000 men, Isfahan/Fars); *Glory of the Shia World* 1910; JRCAS Assyrians paper 21:2 (1934), 255–268, DOI 10.1080/03068373408725306.
- Glubb: joined Legion 1930; Desert Patrol 1931 (all-Bedouin); command 1939; West Bank/1948; dismissed 1 Mar 1956.
- Spears: flew de Gaulle out 17 Jun 1940; Mers el-Kébir ultimatum conveyed 3 Jul 1940; head of British Mission to Free French in Levant 1941–44.

## Honesty flags carried into the deliverable's Unverified Leads
- Wauchope: NO monograph exists in the sources searched (OL/archive searches empty) — genuinely under-studied; anchor to Peel Report + Wikipedia's Hyamson-sourced claims.
- Arnold Wilson resignation month (1920) not pinned in fetched sources; Cornwallis: Wavell's 1942 London Gazette "Despatch on Operations in Iraq, East Syria and Iran" PDF URL not re-verified (commonly ibiblio hyperwar); Clayton has no dedicated monograph; Cox/Wilson/Sykes paper shelfmarks (BL IOR; St Antony's MEC; Churchill SPRS for Spears) are standard-literature locations, not item-verified; Ryan "money for nothing" (1933) is reported speech via Philby/Saudi Aramco Wikipedia articles, underlying FO 371 telegram not located; Bradshaw, *The Glubb Reports* (Springer 2016) cited from Wikipedia reference list, no URL.
