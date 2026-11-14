# UK Cabinet / Whitehall Strategists — verified source bank (11a-uk-cabinet.md)

Deliverable: `uk-parts/11a-uk-cabinet.md` in the religion-in-service-of-empire series (13 London-level strategists c.1900–1950: Balfour, Lloyd George, Curzon, Churchill, Milner, Samuel, Amery, Ramsay MacDonald, Malcolm MacDonald, Eden, Bevin, Attlee, Sykes). All URLs below were curl-checked HTTP 200 on 2 Sep 2026 unless a code is given. Wikipedia raw texts for the 13 figures + anchor topics were saved as `pages/uk-*.wiki` (fetched via `index.php?title=X&action=raw`, `sleep 11` spacing, all healthy byte counts — no rate-limiting at 6–8 titles per batch).

## Verified archive.org items (metadata endpoint, all HTTP 200)

- **Lloyd George:** `truthaboutpeacet0001davi` + `truthaboutpeacet0002davi` (*The Truth About the Peace Treaties*, 1938, vols 1–2); `warmemoirsofdavi00lloy_0` (*War Memoirs*).
- **Churchill:** `worldcrisis0000rtho` (*The World Crisis*); `worldcrisisafter0000wins` (*The Aftermath* — used across the series); `secondworldwargr0003wins` (*The Second World War* vol. III *The Grand Alliance* — 1941 Syria/Iran chapters).
- **Curzon:** `persiapersianque0000curz` (1892, 1966 reprint; DLI scan `in.ernet.dli.2015.69515`); `britishgovernmen0000curz` (*British Government in India*, 1925); bio: `lifeoflordcurzon0002zetl` (Ronaldshay vol. 2, 1928; set also on DLI), `curzonendofepoch0000mosl` (Mosley 1961).
- **Milner:** `englandinegypt02milngoog` (*England in Egypt*, 1894); `nationempire0000lord_g0r2` (*The Nation and the Empire*, 1913); `milnerpaperssout0000ceci` + `milnerpapersvolu0000lord` (*The Milner Papers*, 1931/33 — South Africa, not the Egypt Mission); bios `milnerapostleofe0000marl` (Marlowe), `proconsulinpolit0000goll` (Gollin), `alfredlordmilner0000wren` (Wrench 1958); `toendallwarsstor0000hoch_v2l1` (Hochschild).
- **Samuel:** `groovesofchange0000unse` (*Grooves of Change*, 1946). His *Memoirs* (1945) is print-only.
- **Amery:** `mypoliticallife0001amer` / `0002` / `0003` (*My Political Life*, 1953–55, all three vols).
- **Ramsay MacDonald:** `ramsaymacdonald0000marq` (Marquand 1977 bio).
- **Malcolm MacDonald:** nothing useful on archive.org (memoirs *People and Places* 1969 in copyright) — papers portal at Durham: https://stories.durham.ac.uk/macdonald/ (200).
- **Eden:** `reckoningmemoirs0000anth` (*The Reckoning*, 1965); `facingdictatorsm00eden` (*Facing the Dictators*, 1962); `fullcirclememoir00eden` (*Full Circle*, 1960); bio `anthonyeden0000jame_r8l5` (Rhodes James 1986).
- **Bevin:** `lifetimesofernes0000bull` (Bullock vol. 1, 1960); `ernestbevinforei00bull` (Bullock vol. 3 *Foreign Secretary 1945–1951*, 1983/85 printing).
- **Attlee:** `asithappened00attl` (*As It Happened*, 1954); `twilightofempire0000fran` (Francis Williams, *Twilight of Empire: Memoirs of PM Clement Attlee*, 1961 — "A Prime Minister Remembers"); bio `attlee0000harr` (Harris 1982).
- **Balfour:** `theismandhumanis0000balf` (*Theism and Humanism*, Gifford Lectures 1915 — his religion-empire worldview); bio `dli.ministry.09872` (Dugdale 1936, DLI). Stein `balfourdeclarati0000unse` (1961), Schneer `balfourdeclarati00schn_0` (2010), Fromkin `peacetoendallpea00from` — all 200.
- **Sykes:** `caliphslastherit0000syk` (*The Caliphs' Last Heritage*, 1915 — his Ottoman religious-geography book, on archive.org!); Leslie, *Mark Sykes: His Life and Letters* (1923): `marksykeshislife00lesluoft` (Toronto scan) + `marksykeshislife0000lesl`.
- **Others:** Kedourie `englandmiddleeas0000kedo` (*England and the Middle East*); Morgan `consensusdisunit0000morg` + `davidlloydgeorge0000morg`; Gilbert official Churchill vol. IV `winstonschurchil04chur_0`; **DBFP**: 1st ser. vol. IV `doc-brit-foreign-policy-1-s-v-4`, 1st ser. vol. XIII `doc-brit-foreign-policy-1-s-v-13` (Turkey/Arabia/Persia 1920–21 — Curzon's eastern policy at its densest), 2nd ser. vol. VI `documentsonbriti0006elwo`.
- Search pattern that worked: `curl -s "https://archive.org/advancedsearch.php?q=creator%3A%28X%29+AND+title%3A%28y%29&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=creator&fl%5B%5D=date&rows=8&output=json"` — field syntax (`creator:(x) AND title:(y)`) works fine on archive.org (contrast OpenLibrary, where it fails).

## Treaty / white-paper / hansard hosts (status codes)

- Avalon: `.../20th_century/balfour.asp`, `.../sykes.asp` (Sykes–Picot), `.../brwh1939.asp` (Cmd 6019) — all 200. Wikisource `British_White_Paper_of_Palestine_1939` 200; UNISPAL `auto-insert-198767` 200.
- **BYU Sykes–Picot slug is hyphenated: `Sykes-Picot_Agreement` (200); the underscore variant 404s.** (Site also hosts Lawrence's Mesopotamia report — already in series.)
- Passfield Cmd 3692: COJS PDF `https://cojs.org/wp-content/uploads/Statement_of_Policy_1930.pdf` + JVL page — 200. MacDonald→Weizmann letter 13 Feb 1931: WJC news page 200.
- **Hansard:** modern `hansard.parliament.uk` = 403 Cloudflare-gated. **Historic Hansard API fetches cleanly:** `https://api.parliament.uk/historic-hansard/commons/1939/may/23/palestine` → 200 (22–23 May 1939 White Paper debate: Commons motion to reject WP defeated 268–179 on 22 May; Lloyd George "act of perfidy"; Churchill voted against his own party). Cite the API URL with the modern-site caveat.
- **TNA Discovery:** detail pages return 202 to bots = resolves, not dead. Verified this session: `details/c/F262414` (Milner Mission creator record) and `details/r/D7730874` (cabinet memo CAB 24/271/3 "Palestine: Policy of His Majesty's Government", cited from the McMahon–Hussein correspondence article). **The JSON search API (`API/search/records?...`) intermittently returns HTTP 500 server-error HTML — fallback: mine `/details/r/<id>` URLs from Wikipedia citation lists and verify those return 202.** `nationalarchives.gov.uk/cabinetpapers` root 404'd — don't cite the educational site.
- QDL (qdl.qa) 403 Cloudflare: Milner Mission report copy (`/en/archive/81055/vdc_100080131821.0x00002f`) and the Curzon papers finding aid (Mss Eur F111–112) are citable-with-caveat only.
- Curzon's 26 Oct 1917 cabinet memorandum "The Future of Palestine": file description page on id.m.wikipedia (Berkas:) → 200, one week before the Declaration.

## Per-figure dated anchors (fetched-wikitext verified)

- Balfour: FS to 23 Oct 1919; Declaration 2 Nov 1917; 11 Aug 1919 memo to Curzon ("700,000 Arabs" quote; reused from 09-palestine.md).
- Curzon: FS from 23 Oct 1919 (infobox); Bengal partition in force 16 Oct 1905; Sèvres 10 Aug 1920; Lausanne chief negotiator 1922–23; stayed FS under Bonar Law after Chanak.
- Milner: co-drafted Declaration text (with Amery; Stein 1961 pp. 310–11 via Milner article); Mission to Egypt Dec 1919–Mar 1920; resigned Colonial Secretary **13 Feb 1921** (infobox term_end).
- Churchill: APOC 51% purchase 1914; Cairo Conference minutes title = "Middle East Conference held in Cairo and Jerusalem, March 12 to 30, 1921"; Commons report 14 Jun 1921; Syria–Lebanon campaign 8 Jun–14 Jul 1941; Anglo-Soviet invasion of Iran 25–31 Aug 1941, Reza abdicated **16 Sep 1941**.
- Sykes: De Bunsen Committee from Mar 1915; Sykes–Picot map signed **8 May 1916**, notes exchanged 9–16 May 1916 (conventionally dated 16 May); published by Bolsheviks 23 Nov 1917; **Hogarth message to Sharif Hussein 4 Jan 1918 was written by Sykes** (McMahon–Hussein article); died 16 Feb 1919.
- Amery: wrote the final draft of the Declaration (Rubinstein 2004 p. 168 via Amery article); Colonial Sec 6 Nov 1924–4 Jun 1929; India Sec 13 May 1940–26 Jul 1945; Cripps Mission Mar 1942 with Muslim-League caveat.
- Ramsay MacDonald: Passfield Cmd 3692 20 Oct 1930; letter to Weizmann 13 Feb 1931; Communal Award 16 Aug 1932.
- Malcolm MacDonald: "oversaw and introduced" the 1939 White Paper (his article); WP drafted Mar 1939 after St James's Palace failure 17 Mar 1939.
- Eden: resigned FS 20 Feb 1938; FS again 22 Dec 1940–26 Jul 1945 (infobox); visited Palestine Feb 1940 as Dominions Sec.
- Bevin: Oct 1945 cabinet intention to refer Palestine to UN (End-of-Mandate article, citing Haron); cabinet decision to refer **14 Feb 1947**; statement "irreconcilable conflict of principles" quote in that article; abstained on UNGA 181; Creech Jones announced 15 May 1948 end on 11 Dec 1947; Portsmouth treaty 15 Jan 1948.
- Attlee: Simon Commission 1928–34; **20 Feb 1947** Commons statement (India transfer "by June 1948" + Mountbatten as Viceroy — corroborated by 4 independent study sites via search snippets); 3 June Plan; Pakistan 14 Aug / India 15 Aug 1947.

## Unverified leads carried from 11a (do NOT re-cite as fact)

- Curzon's "largely a matter of words" phrasing of the McMahon pledge — not located verbatim in any fetched text (britainpalestineproject.org 200 quotes Curzon on Palestine's inclusion; exact sentence unconfirmed).
- "Sykes coined the term Middle East" — unverified; standard accounts credit Mahan 1902, Sykes with official currency only.
- Cmd 957 (Milner Report) exact publication date 1920 vs 1921 — unconfirmed (QDL copy gated).
- DBFP 1st-series vols XVII–XVIII (Lausanne/Mosul 1922–23) — no archive.org copy checked.
- "Scuttle" accusations (Attlee/Bevin) — print-attested (Roberts) but no fetched primary.
- Sidqi–Bevin 1946 draft treaty text; Sanger 1995 and Wm. Roger Louis 1984 biographies — print-only.
