#!/usr/bin/env python3
"""Rebuild public/index.html: restructured page architecture for yonedaai.com.

Reads:  public/index.html (current page: head/CSS, hero, about, methodology,
        framework, derivation, network, footer are harvested from it),
        scripts/data/catalog.json, scripts/data/repos_raw.json
Writes: public/index.html (new order: nav, hero, programs, flagship, library,
        network, repos, about, footer)
"""
import json, html, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "public", "index.html")
catalog = json.load(open(os.path.join(ROOT, "scripts", "data", "catalog.json")))
repos_raw = json.load(open(os.path.join(ROOT, "scripts", "data", "repos_raw.json")))

FIELDS = ["Physics & Quantum", "Mathematics", "AI & Computation", "Interdisciplinary"]
esc = lambda s: html.escape(s, quote=False)

# ---------------- repo curation ----------------
EXCLUDE = {"nyctax", "copied-app", "apple-test", "work_summary", "getcopied-app",
           "governance-theory", "organizational_theory", "economic_policy",
           "on_the_information_and_matter_250808", "go-test", "autopilot", "chox",
           "ansible-wordpress", "yoneda-ai-web"}
MATH_REPOS = {"unified_foundations_of_mathematics", "geometric_langlands_conjecture_expanded",
              "proof_as_code_math_physics", "proof_as_code"}
AI_REPOS = {"CatDB-Research", "time-compression-paradox", "market-theory", "typesafe-context",
            "contextfs-node", "yonedaai-industry-research", "ai_theory", "ai-preprint-forge",
            "chain-of-intent", "local_rag_pipeline", "quantum_database_theory",
            "ai-memory-merge-protocol", "preprint-forge-frontend", "database_theory", "voltforge"}
INTER_REPOS = {"yac-cannabinoid-adhd", "type-safe-biophysics"}

def repo_field(name):
    if name in MATH_REPOS: return "Mathematics"
    if name in AI_REPOS: return "AI & Computation"
    if name in INTER_REPOS: return "Interdisciplinary"
    return "Physics & Quantum"

repos = [r for r in repos_raw
         if r["visibility"] == "PUBLIC" and not r["isFork"] and r["name"] not in EXCLUDE]
repos.sort(key=lambda r: r["name"].lower())
N_REPOS = len(repos)
N_PAPERS = sum(len(c["papers"]) for c in catalog)
N_SITES = 23

src = open(INDEX, encoding="utf-8").read()

def section(sid):
    m = re.search(r'<section[^>]*id="%s"[\s\S]*?</section>' % sid, src)
    if not m:
        sys.exit(f"section {sid} not found")
    return m.group(0)

def div_block(text, marker):
    """Extract a <div ...marker...> block with balanced div nesting."""
    i = text.index(marker)
    i = text.rindex("<div", 0, i + 1)
    depth, j = 0, i
    while j < len(text):
        if text.startswith("<div", j): depth += 1; j += 4
        elif text.startswith("</div>", j):
            depth -= 1; j += 6
            if depth == 0: return text[i:j]
        else: j += 1
    sys.exit("unbalanced divs for " + marker)

# ---------------- harvested chunks ----------------
head = src[:src.index("<nav>")]
hero = section("home")
about_sec = section("about")
methodology = section("methodology")
framework = section("framework")
derivation = section("derivation")
network = section("network")
footer_on = src.index("<!-- Footer -->")
tail = src[footer_on:]

# ---------------- nav ----------------
NAV = '''<nav>
  <div class="nav-inner">
    <a href="/" class="nav-logo">Yoneda<span>AI</span></a>
    <button class="nav-hamburger" onclick="document.querySelector('.nav-links').classList.toggle('open')" aria-label="Toggle navigation">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
    </button>
    <ul class="nav-links">
      <li><a href="#programs">Programs</a></li>
      <li><a href="#flagship">Flagship</a></li>
      <li><a href="#library">Library</a></li>
      <li><a href="#network">Network</a></li>
      <li><a href="#repos">Repositories</a></li>
      <li><a href="#about">About</a></li>
      <li>
        <a href="https://github.com/MagnetonIO" class="gh-link" target="_blank" rel="noopener">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          GitHub
        </a>
      </li>
    </ul>
  </div>
</nav>
'''

# ---------------- hero tweaks ----------------
hero = re.sub(r'<div class="hero-stats">[\s\S]*?</div>\s*</div>',
  f'''<div class="hero-stats">
      <div class="hero-stat"><strong>{N_PAPERS}</strong> Papers</div>
      <div class="hero-stat"><strong>{len(catalog)}</strong> Collections</div>
      <div class="hero-stat"><strong>{N_SITES}</strong> Research Sites</div>
      <div class="hero-stat"><strong>{N_REPOS}</strong> Repositories</div>
    </div>''', hero, count=1)
hero = hero.replace('href="#library" class="btn btn-primary">Browse the Library',
                    'href="#programs" class="btn btn-primary">Explore the Research')
hero = hero.replace('<p class="subtitle">Category-theoretic foundations for open problems in quantum mechanics, gravity, and observer theory</p>',
                    '<p class="subtitle">Category-theoretic foundations for physics, mathematics, and AI &mdash; a modular body of research spanning quantum foundations, foundations of mathematics, and the mathematics of intelligence</p>')

# ---------------- programs section ----------------
def prog_card(col):
    links = [f'<a href="#lib-{col["id"]}">{len(col["papers"])} papers</a>']
    if col.get("site"):
        links.append(f'<a href="{col["site"]}" target="_blank" rel="noopener">Site ↗</a>')
    if col.get("github"):
        links.append(f'<a href="https://github.com/{col["github"]}" target="_blank" rel="noopener">GitHub ↗</a>')
    return (f'<div class="prog-card"><h4><a href="#lib-{col["id"]}">{esc(col["name"])}</a></h4>'
            f'<div class="prog-links">{" · ".join(links)}</div></div>')

bands = []
for f in FIELDS:
    cols = [c for c in catalog if c["field"] == f]
    if not cols: continue
    cards = "".join(prog_card(c) for c in cols)
    n = sum(len(c["papers"]) for c in cols)
    bands.append(f'''
    <div class="prog-band">
      <div class="prog-band-head"><h3>{esc(f)}</h3><span class="lib-col-meta">{len(cols)} collections · {n} papers</span></div>
      <div class="prog-grid">{cards}</div>
    </div>''')

PROGRAMS = f'''
<!-- Research Programs -->
<section class="programs-section" id="programs" style="background: var(--bg-alt);">
  <span id="series1"></span><span id="series2"></span>
  <div class="container">
    <div class="section-label">The Research</div>
    <h2 class="section-title">Research Programs</h2>
    <p class="section-subtitle">{len(catalog)} collections across four fields. Each program links into the full paper library below; many have dedicated sites and repositories.</p>
    {"".join(bands)}
  </div>
</section>
'''

# ---------------- flagship (framework + derivation merged) ----------------
fw_grid = div_block(framework, 'class="framework-grid"')
m = re.search(r'<p class="section-subtitle">[\s\S]*?</p>([\s\S]*)</div>\s*</section>\s*$', derivation)
deriv_content = m.group(1) if m else ""
m2 = re.search(r'<p class="section-subtitle">([\s\S]*?)</p>', derivation)
deriv_sub = m2.group(1) if m2 else ""

FLAGSHIP = f'''
<!-- Flagship: The Yoneda Constraint -->
<section id="flagship">
  <div class="container">
    <div class="section-label">Flagship Program</div>
    <h2 class="section-title">The Yoneda Constraint</h2>
    <p class="section-subtitle">Four interconnected concepts form the mathematical backbone of Quantum Perspectivism &mdash; and the derivation chain runs from the Yoneda Lemma to quantum mechanics.</p>
    {fw_grid}
    <h3 class="flagship-h3">From Yoneda to Quantum Mechanics</h3>
    <p class="section-subtitle">{deriv_sub}</p>
    {deriv_content}
  </div>
</section>
'''

# ---------------- library (regenerated with anchors + read-online links) ----------------
PDF_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'

blocks = []
for col in catalog:
    links = []
    if col.get("site"):
        links.append(f'<a href="{col["site"]}" target="_blank" rel="noopener">Website ↗</a>')
    if col.get("github"):
        links.append(f'<a href="https://github.com/{col["github"]}" target="_blank" rel="noopener">GitHub ↗</a>')
    link_html = f'<span class="lib-col-links">{"".join(links)}</span>' if links else ""
    items = []
    for p in col["papers"]:
        key = esc((p["title"] + " " + col["name"]).lower())
        base = os.path.splitext(os.path.basename(p["pdf"]))[0]
        page = f"/papers/{base}.html"
        read = (f'<a class="lib-read" href="{page}">Read online</a>'
                if os.path.exists(os.path.join(ROOT, "public", "papers", base + ".html")) else "")
        items.append(
            f'<li class="lib-paper" data-search="{key}">'
            f'<a href="{p["pdf"]}" target="_blank" rel="noopener">{PDF_ICON}<span>{esc(p["title"])}</span></a>{read}</li>')
    blocks.append(f'''
      <div class="lib-collection" id="lib-{col["id"]}" data-field="{esc(col["field"])}">
        <div class="lib-col-head">
          <h3>{esc(col["name"])}</h3>
          <span class="lib-col-meta">{len(col["papers"])} paper{"s" if len(col["papers"]) != 1 else ""} · {esc(col["field"])}</span>
          {link_html}
        </div>
        <ul class="lib-papers">{"".join(items)}
        </ul>
      </div>''')

chips = ['<button class="lib-chip active" data-field="all" type="button">All</button>'] + [
    f'<button class="lib-chip" data-field="{esc(f)}" type="button">{esc(f)}</button>' for f in FIELDS]

LIBRARY = f'''
<!-- Paper Library -->
<section class="library-section" id="library">
  <div class="container">
    <div class="section-label">Complete Catalog</div>
    <h2 class="section-title">Paper Library</h2>
    <p class="section-subtitle">{N_PAPERS} papers across {len(catalog)} collections &mdash; quantum foundations, category theory, quantum error correction, foundations of mathematics, and the mathematics of AI. Every paper is available as a PDF.</p>
    <div class="lib-controls">
      <input type="search" id="libSearch" class="lib-search" placeholder="Search {N_PAPERS} papers…" aria-label="Search papers">
      <div class="lib-chips" role="group" aria-label="Filter by field">{"".join(chips)}</div>
    </div>
    <div id="libList">{"".join(blocks)}
    </div>
    <p class="lib-empty" id="libEmpty" hidden>No papers match your search.</p>
  </div>
</section>
'''

# ---------------- repos section ----------------
def repo_card(r):
    lang = (r.get("primaryLanguage") or {}).get("name", "")
    lang_chip = f'<span class="repo-lang">{esc(lang)}</span>' if lang else ""
    desc = esc((r.get("description") or "").strip())
    if len(desc) > 140: desc = desc[:137] + "…"
    return (f'<a class="repo-card" href="https://github.com/MagnetonIO/{r["name"]}" target="_blank" rel="noopener">'
            f'<div class="repo-card-head"><h4>{esc(r["name"])}</h4>{lang_chip}</div>'
            f'<p>{desc}</p></a>')

repo_bands = []
for f in FIELDS:
    group = [r for r in repos if repo_field(r["name"]) == f]
    if not group: continue
    repo_bands.append(f'''
    <div class="prog-band">
      <div class="prog-band-head"><h3>{esc(f)}</h3><span class="lib-col-meta">{len(group)} repositories</span></div>
      <div class="repo-grid">{"".join(repo_card(r) for r in group)}</div>
    </div>''')

REPOS = f'''
<!-- Repositories -->
<section class="repos-section" id="repos">
  <div class="container">
    <div class="section-label">Open Source</div>
    <h2 class="section-title">Repositories</h2>
    <p class="section-subtitle">{N_REPOS} public research repositories on <a href="https://github.com/MagnetonIO" target="_blank" rel="noopener">github.com/MagnetonIO</a> &mdash; LaTeX sources, Haskell verifications, and research tooling.</p>
    {"".join(repo_bands)}
  </div>
</section>
'''

# ---------------- about (about + condensed methodology) ----------------
meth_intro = re.search(r'<p class="methodology-intro">[\s\S]*?</p>', methodology).group(0)
results = div_block(methodology, 'class="results-grid"')
results = results.replace("Modules in unified framework", "Framework modules")
about_inner = re.search(r'([\s\S]*)</div>\s*</section>\s*$', about_sec).group(1)
ABOUT = f'''{about_inner}
    <h3 class="flagship-h3">Methodology: Agent Orchestration for Frontier Science</h3>
    {meth_intro}
    {results}
  </div>
</section>
'''

# ---------------- CSS additions ----------------
CSS = """
    /* Research Programs + Repositories */
    .prog-band { margin-bottom: 34px; }
    .prog-band:last-child { margin-bottom: 0; }
    .prog-band-head { display: flex; align-items: baseline; gap: 14px; margin-bottom: 12px; }
    .prog-band-head h3 { font-size: 1.15rem; font-weight: 700; color: var(--text); }
    .prog-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; }
    .prog-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px 14px; }
    .prog-card h4 { font-size: 0.92rem; font-weight: 600; margin-bottom: 4px; }
    .prog-card h4 a { color: var(--text); text-decoration: none; }
    .prog-card h4 a:hover { color: var(--accent); }
    .prog-links { font-size: 0.78rem; color: var(--text-muted); }
    .prog-links a { color: var(--accent); text-decoration: none; font-weight: 600; }
    .prog-links a:hover { text-decoration: underline; }
    .repo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }
    .repo-card { display: block; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px 14px; text-decoration: none; transition: border-color .15s, transform .15s; }
    .repo-card:hover { border-color: var(--accent-light); transform: translateY(-2px); }
    .repo-card-head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
    .repo-card h4 { font-size: 0.88rem; font-weight: 600; color: var(--text); font-family: 'JetBrains Mono', monospace; overflow-wrap: anywhere; }
    .repo-lang { margin-left: auto; flex: none; font-size: 0.66rem; font-weight: 700; color: var(--accent); background: var(--accent-bg); border-radius: 999px; padding: 2px 8px; }
    .repo-card p { font-size: 0.8rem; line-height: 1.5; color: var(--text-secondary); }
    .flagship-h3 { font-size: 1.3rem; font-weight: 700; color: var(--text); margin: 36px 0 8px; }
    .lib-read { flex: none; font-size: 0.76rem; font-weight: 600; color: var(--accent); text-decoration: none; padding: 4px 0; }
    .lib-read:hover { text-decoration: underline; }
    .lib-paper { display: flex; align-items: center; gap: 12px; }
    .lib-paper > a:first-child { flex: 1; }
"""
i = head.rindex("</style>")
head = head[:i] + CSS + "\n  " + head[i:]

# meta description already updated in a previous pass; refresh counts
head = head.replace("A library of 122 papers across 27 research collections, plus a network of 23 companion research sites.",
                    f"A library of {N_PAPERS} papers across {len(catalog)} research collections, {N_SITES} companion research sites, and {N_REPOS} open-source repositories.")

out = (head + NAV + "\n<!-- Hero -->\n" + hero + "\n" + PROGRAMS + "\n" + FLAGSHIP + "\n"
       + LIBRARY + "\n" + network + "\n" + REPOS + "\n\n<!-- About -->\n" + ABOUT + "\n" + tail)

open(INDEX, "w", encoding="utf-8").write(out)
print(f"Rebuilt index.html: {len(out.splitlines())} lines | {N_PAPERS} papers, "
      f"{len(catalog)} collections, {N_REPOS} repos, {N_SITES} sites")
