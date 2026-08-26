#!/usr/bin/env python3
"""Build paper catalog for yonedaai.com: extract titles from .tex, copy PDFs, emit JSON."""
import glob, json, os, re, shutil, sys

DEV = "/Users/mlong/Documents/Development"
SITE = os.path.join(DEV, "yoneda-ai-web", "public")
LIB = os.path.join(SITE, "papers", "pdf", "library")

MATH, PHYS, AI, OTHER = "Mathematics", "Physics & Quantum", "AI & Computation", "Interdisciplinary"

def title_from_tex(tex_path):
    try:
        s = open(tex_path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return None
    m = re.search(r"\\title\s*(\[[^\]]*\])?\s*\{", s)
    if not m:
        return None
    i = m.end()
    depth, out = 1, []
    while i < len(s) and depth:
        c = s[i]
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: break
        if depth: out.append(c)
        i += 1
    t = "".join(out)
    t = re.sub(r"(?<!\\)%[^\n]*", " ", t)
    t = re.sub(r"\\texorpdfstring\s*\{([^{}]*)\}\s*\{[^{}]*\}", r"\1", t)
    t = re.sub(r"\\vspace\*?\s*\{[^}]*\}", " ", t)
    t = t.replace('\\"o', "\u00f6").replace('\\"{o}', "\u00f6").replace("\\'e", "\u00e9")
    t = t.replace("\\\\", " ").replace("~", " ")
    t = re.sub(r"\[\s*-?[\d.]+\s*(em|pt|cm|ex|in)\s*\]", " ", t)
    t = re.sub(r"(?<![\w.])-?[\d.]+(em|pt|cm|ex)(?![a-zA-Z])", " ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", " ", t)
    t = t.replace("{", "").replace("}", "").replace("$", "").replace("%", " ")
    t = re.sub(r"\s*:\s*", ": ", t)
    t = re.sub(r"\s+", " ", t).strip(" :,-")
    return t or None

def title_from_html(base):
    p = os.path.join(SITE, "papers", os.path.splitext(base)[0] + ".html")
    if not os.path.exists(p):
        return None
    s = open(p, encoding="utf-8", errors="ignore").read()
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    if not m:
        return None
    t = re.sub(r"\s+", " ", m.group(1)).strip()
    t = re.split(r"\s*[|\u2014\u2013]\s*YonedaAI.*", t)[0].strip()
    return t or None

def pretty(name):
    n = os.path.splitext(os.path.basename(name))[0]
    n = n.replace("_", " ").replace("-", " ")
    return n.title()

def find_tex(pdf_path, tex_dirs):
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    cands = [os.path.join(os.path.dirname(pdf_path), base + ".tex")]
    for d in tex_dirs:
        cands.append(os.path.join(d, base + ".tex"))
    for c in cands:
        if os.path.exists(c):
            return c
    return None

# (id, name, field, site_url, github, pdf_globs, tex_dirs, hosted)
COLLECTIONS = [
    ("quantum-perspectivism", "Quantum Perspectivism & Foundational Problems", PHYS,
     None, "MagnetonIO/yoneda-ai",
     [f"{SITE}/papers/pdf/*.pdf"],
     [f"{DEV}/yoneda-ai/papers/latex"] + glob.glob(f"{DEV}/magneton_work/*/papers"),
     True),
    ("condensed-representation", "Condensed Representation Theory of Physics", PHYS,
     "https://condensed-representation-theory-of.vercel.app", "MagnetonIO/condensed-representation-theory-of-physics",
     [f"{DEV}/condensed-representation-theory-of-physics/papers/pdf/*.pdf"],
     [f"{DEV}/condensed-representation-theory-of-physics/papers/latex"], False),
    ("math-qg-library", "Mathematical Representations of Quantum Gravity", PHYS,
     "https://math-qg-representation-library.vercel.app", "MagnetonIO/math-qg-representation-library",
     [f"{DEV}/math-qg-representation-library/papers/pdf/*.pdf"],
     [f"{DEV}/math-qg-representation-library/papers/latex"], False),
    ("mathematics-physical-representation", "Mathematics as Physical Representation", MATH,
     "https://mathematics-physical-representation.vercel.app", "MagnetonIO/mathematics-physical-representation",
     [f"{DEV}/mathematics-physical-representation/papers/pdf/*.pdf"],
     [f"{DEV}/mathematics-physical-representation/papers/latex"], False),
    ("topological-phases", "Topological Phases of Matter", PHYS,
     "https://condensed-phase-spectrum.vercel.app", "MagnetonIO/topological-phases-of-matter",
     [f"{DEV}/topological-phases-of-matter-chatgpt/papers/pdf/*.pdf"],
     [f"{DEV}/topological-phases-of-matter-chatgpt/papers/latex"], False),
    ("yoneda-constraint", "The Yoneda Constraint: Universal Formulation", PHYS,
     "https://yoneda-constraint.vercel.app", "MagnetonIO/yoneda-constraint",
     [f"{DEV}/yoneda-constraint/papers/pdf/*.pdf"],
     [f"{DEV}/yoneda-constraint/papers/latex"], False),
    ("minimal-runtime-axiom", "The Minimal Runtime Axiom", PHYS,
     "https://minimal-runtime-axiom.vercel.app", "MagnetonIO/minimal-runtime-axiom",
     [f"{DEV}/minimal-runtime-axiom/docs/minimal-runtime-axiom.pdf"],
     [f"{DEV}/minimal-runtime-axiom/papers/latex"], False),
    ("joule-standard", "The Joule Standard: Energy Economics of Intelligence", AI,
     "https://joule-standard.vercel.app", "MagnetonIO/joule-standard",
     [f"{DEV}/joule-standard/papers/pdf/*.pdf"],
     [f"{DEV}/joule-standard/papers/latex"], False),
    ("ferrous-bridge", "Ferrous Bridge: Verified C-to-Rust Migration", AI,
     "https://ferrous-bridge.vercel.app", "MagnetonIO/ferrous-bridge",
     [f"{DEV}/ferrous-bridge/papers/pdf/*.pdf"],
     [f"{DEV}/ferrous-bridge/papers/latex"], False),
    ("categorical-qec", "Topological & Categorical Quantum Error Correction", PHYS,
     None, None,
     [f"{DEV}/magneton_work/quantum-topological-qec/*.pdf"], [], False),
    ("derived-functors-qec", "Derived Functors & Teleological QEC", PHYS,
     None, None,
     [f"{DEV}/magneton_work/derived-functors-qec/*.pdf"], [], False),
    ("proof-as-code-qec", "Proof as Code: Functorial Quantum Engineering", PHYS,
     None, None,
     [f"{DEV}/magneton_work/proof_as_code_qec/*.pdf"], [], False),
    ("quantumflow", "QuantumFlow & Derived Hamiltonians", PHYS,
     None, None,
     [f"{DEV}/magneton_work/QuantumFlow/*.pdf",
      f"{DEV}/magneton_work/synthetic_data/US_Patent_Inverse_Topological_Decoding_Derived_Hamiltonians.pdf"], [], False),
    ("mathematical-physics", "Mathematical Physics: Frameworks & Duality", PHYS,
     None, None,
     [f"{DEV}/magneton_work/quantum_unification/quantum_unification.pdf",
      f"{DEV}/magneton_work/mathematical_physics/PDF/*.pdf",
      f"{DEV}/magneton_work/on_the_same_origin_of_quantum_physics_and_general_relativity_expanded_with_code/physical_duality.pdf",
      f"{DEV}/magneton_work/on_the_same_origin_of_quantum_physics_and_general_relativity_expanded_with_code/prototype-unifying-equation.pdf"],
     [f"{DEV}/magneton_work/mathematical_physics/LaTex",
      f"{DEV}/magneton_work/on_the_same_origin_of_quantum_physics_and_general_relativity_expanded_with_code"], False),
    ("foundations-mathematics", "Foundations of Mathematics", MATH,
     None, None,
     [f"{DEV}/magneton_work/unified_foundations_of_mathematics/*.pdf"], [], False),
    ("geometric-langlands", "Geometric Langlands & Universal Categories", MATH,
     None, None,
     [f"{DEV}/magneton_work/geometric_langlands_conjecture_expanded/*.pdf"], [], False),
    ("encoding-primes", "Proof as Code: Number Theory", MATH,
     None, None,
     [f"{DEV}/magneton_work/proof_as_code_math_physics/*.pdf"], [], False),
    ("functorial-fission", "Functorial Fission", PHYS,
     None, None,
     [f"{DEV}/magneton_work/functorial-fission/pdf/main.pdf"],
     [f"{DEV}/magneton_work/functorial-fission/latex"], False),
    ("type-safe-physics", "Type-Safe Physics", PHYS,
     None, None,
     [f"{DEV}/magneton_work/type-safe-physics/pdf/*.pdf"],
     [f"{DEV}/magneton_work/type-safe-physics/tex"], False),
    ("type-safe-biophysics", "Type-Safe Biophysics & Context Engineering", OTHER,
     None, None,
     [f"{DEV}/magneton_work/type-safe-biophysics/pdf/*.pdf"],
     [f"{DEV}/magneton_work/type-safe-biophysics/tex"], False),
    ("fibered-sheaf-memory", "Fibered Sheaf Memory for AI", AI,
     None, None,
     [f"{DEV}/magneton_work/ai-memory-merge-protocol/*.pdf"], [], False),
    ("homotopical-semantics", "Homotopical Semantics & AI Hallucination", AI,
     None, None,
     [f"{DEV}/magneton_work/ai-hallucination-research/sources/*.pdf"], [], False),
    ("quantum-database-theory", "Quantum Database Theory", AI,
     None, None,
     [f"{DEV}/magneton_work/quantum_database_theory/quantum_database_theory_topos_theory_entanglement_for_global_consistency.pdf",
      f"{DEV}/magneton_work/quantum_database_theory/dist_qdb_qec_framework.pdf",
      f"{DEV}/magneton_work/quantum_database_theory/quantum_databases_expanded.pdf",
      f"{DEV}/magneton_work/quantum_database_theory/quantum_db_topos_entanglement_pipeline.pdf",
      f"{DEV}/magneton_work/quantum_database_theory/augmented_science.pdf"], [], False),
    ("topos-database-theory", "Topos-Theoretic Database Theory", AI,
     None, None,
     [f"{DEV}/magneton_work/database_theory/*.pdf"], [], False),
    ("ai-code-generation", "AI Code Generation", AI,
     None, None,
     [f"{DEV}/magneton_work/industry_research/*.pdf"], [], False),
    ("time-compression", "The Time Compression Paradox", AI,
     None, None,
     [f"{DEV}/magneton_work/time_compression_paradox/sources/time-compression-paradox.pdf"], [], False),
    ("cannabinoid-adhd", "Pathway-Selective Cannabinoids for ADHD", OTHER,
     None, None,
     [f"{DEV}/magneton_work/yac-cannabinoid-adhd/paper/*.pdf"], [], False),
]

def main():
    os.makedirs(LIB, exist_ok=True)
    catalog = []
    total = 0
    for cid, name, field, site, gh, pdf_globs, tex_dirs, hosted in COLLECTIONS:
        pdfs = []
        for g in pdf_globs:
            pdfs.extend(sorted(glob.glob(g)))
        seen = set()
        papers = []
        for p in pdfs:
            base = os.path.basename(p)
            if base in seen:
                continue
            seen.add(base)
            tex = find_tex(p, tex_dirs)
            title = title_from_html(base) if hosted else None
            if not title and tex:
                title = title_from_tex(tex)
            if not title:
                title = pretty(base).replace("Us ", "US ").replace(" Qp", " QP")
            if hosted:
                url = "/papers/pdf/" + base
            else:
                dest_dir = os.path.join(LIB, cid)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(p, os.path.join(dest_dir, base))
                url = f"/papers/pdf/library/{cid}/{base}"
            papers.append({"title": title, "pdf": url})
        if not papers:
            print(f"WARN: no papers for {cid}", file=sys.stderr)
            continue
        total += len(papers)
        catalog.append({"id": cid, "name": name, "field": field,
                        "site": site, "github": gh, "papers": papers})
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog.json")
    json.dump(catalog, open(out, "w"), indent=1)
    print(f"{len(catalog)} collections, {total} papers -> {out}")

if __name__ == "__main__":
    main()
