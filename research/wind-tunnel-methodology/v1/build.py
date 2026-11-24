#!/usr/bin/env python3
"""Recompute the paper's results and build its PDF, TeX and accessible HTML.

No network requests or model calls. Requires Python 3, Matplotlib, Pandoc and
XeLaTeX. Run from any directory. The benchmark is a separate, pinned release.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
BENCHMARK = ROOT.parents[1] / "wind-tunnel-us/v1/benchmark.json"
VERSION = "1.0"
STEM = "wind-tunnel-methodology-v" + VERSION
METHODS = [("previous", "2022 human survey"), ("single", "National model call"),
           ("stratified", "Census-weighted model")]


def score(rows):
    if len(rows) != 12 or len({r["id"] for r in rows}) != 12:
        raise ValueError("This publication describes exactly twelve unique items")
    items = []
    for row in rows:
        y = row["target"]["shares"]
        errors = {}
        for key, _ in METHODS:
            p = row["previous"]["shares"] if key == "previous" else row[key]
            for dist in (p, y):
                if len(dist) != 3 or any(not 0 <= x <= 1 for x in dist) or abs(sum(dist) - 1) > 1e-8:
                    raise ValueError("Invalid substantive distribution")
            errors[key] = {
                "totalVariation": sum(abs(a - b) for a, b in zip(p, y)) / 2,
                "brier": (1 + sum(a*a - 2*a*b for a, b in zip(p, y))) / 2,
            }
        items.append({"id": row["id"], "institution": row["institution"], "errors": errors})
    summary = {key: {
        "meanTotalVariation": sum(r["errors"][key]["totalVariation"] for r in items) / len(items),
        "meanBrier": sum(r["errors"][key]["brier"] for r in items) / len(items),
    } for key, _ in METHODS}
    return {"items": items, "summary": summary}


def figures(data, result):
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "windtunnel-paper-matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                         "svg.fonttype": "none", "svg.hashsalt": "wt-methodology-1.0"})
    out = ROOT / "figures"
    out.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.1, 3.5))
    ax.set(xlim=(0, 10), ylim=(0, 6.2)); ax.axis("off")

    def box(x, y, w, h, title, body, color="#eef3f1"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.09,rounding_size=0.06",
                                    facecolor=color, edgecolor="#668077", linewidth=.75))
        ax.text(x+w/2, y+h*.76, title, ha="center", va="center", fontsize=8, weight="bold", color="#1c3035")
        ax.text(x+w/2, y+h*.37, body, ha="center", va="center", fontsize=7.3, color="#344a51", linespacing=1.4)

    def arrow(a, b, dashed=False):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, lw=.9,
                                    color="#526970", linestyle="--" if dashed else "-"))

    box(.15, 4.45, 2.65, 1.2, "Demographic artifact", "ACS source release + fitted cells\nEligible universe and Nₛ")
    box(3.65, 4.45, 2.65, 1.2, "Frozen study revision", "Audience · instrument · variants\nSource hashes · execution settings")
    box(7.15, 4.45, 2.65, 1.2, "Cell generation", "Model-generated answer shares\nSchema + complete-total checks")
    box(7.15, 2.25, 2.65, 1.2, "Weighted distribution", "Σ Nₛ pₛ / Σ Nₛ\nGenerated output; 0 interviews")
    box(3.65, 2.25, 2.65, 1.2, "Separate wording review", "Authored dossiers + field probes\nDossier population weight = 0", "#f6f2eb")
    box(.15, 2.25, 2.65, 1.2, "Human evidence", "GSS item, year, weight, coding\nExternal comparison", "#edf0f6")
    box(3.65, .15, 2.65, 1.2, "Report and review record", "Measured · modeled · assumed\nVersions and limitations retained")
    arrow((2.89,5.05),(3.55,5.05)); arrow((6.4,5.05),(7.05,5.05))
    arrow((8.47,4.35),(8.47,3.55)); arrow((4.97,4.35),(4.97,3.55))
    arrow((4.97,2.15),(4.97,1.45)); arrow((8.47,2.15),(6.4,.76))
    arrow((2.89,2.2),(3.55,1.15), True)
    ax.text(1.5,1.65,"Compare; do not count as\nadditional generated cases",ha="center",va="center",fontsize=7,color="#526970")
    fig.tight_layout(pad=.1)
    for ext in ("pdf","svg"):
        fig.savefig(out / f"evidence-flow.{ext}", bbox_inches="tight", metadata={"Creator":"TACITUS"})
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.1, 4.8))
    colors = ["#47645a", "#627ea2", "#9b6541"]
    markers = ["o", "s", "D"]
    positions = range(len(result["items"]))
    labels = [r["institution"].replace("Executive branch of the federal government", "Federal executive branch")
              .replace("Banks and financial institutions","Banks / financial institutions") for r in data["rows"]]
    for mi, (key, label) in enumerate(METHODS):
        ax.scatter([r["errors"][key]["totalVariation"] * 100 for r in result["items"]],
                   [y+(mi-1)*.18 for y in positions], s=22, c=colors[mi], marker=markers[mi],label=label,zorder=3)
    ax.set_yticks(list(positions),labels);ax.invert_yaxis()
    ax.set_xlabel("Total variation from 2024 GSS (percentage points; lower is better)",labelpad=9)
    ax.set_xlim(0,21);ax.set_xticks(range(0,21,5));ax.grid(axis="x",color="#e2e7e5",linewidth=.6)
    ax.spines[["top","right","left"]].set_visible(False);ax.spines["bottom"].set_color("#b9c4c0")
    ax.tick_params(axis="y",length=0,pad=8)
    ax.legend(loc="upper center",bbox_to_anchor=(.48,-.17),ncol=3,frameon=False,fontsize=7.1,columnspacing=1.4)
    fig.tight_layout(pad=.3)
    for ext in ("pdf","svg"):
        fig.savefig(out / f"benchmark-items.{ext}", bbox_inches="tight", metadata={"Creator":"TACITUS"})
    plt.close(fig)


def main():
    os.environ.setdefault("SOURCE_DATE_EPOCH", "1795392000")
    data = json.loads(BENCHMARK.read_text())
    result = score(data["rows"])
    for key, _ in METHODS:
        for metric,value in result["summary"][key].items():
            if abs(value - data["scores"]["summary"][key][metric]) > 1e-12:
                raise ValueError("Recomputed benchmark disagrees with released scores")
    table = "| Method | Mean TV (pp) | Mean Brier |\n|:--|--:|--:|\n"
    for key,label in METHODS:
        r = result["summary"][key]
        table += f"| {label} | {100*r['meanTotalVariation']:.2f} | {r['meanBrier']:.5f} |\n"
    items = "| GSS item / institution | 2022 human | National model | Weighted model |\n|:--|--:|--:|--:|\n"
    for row in result["items"]:
        items += f"| `{row['id']}` · {row['institution']} | " + " | ".join(
            f"{100*row['errors'][key]['totalVariation']:.2f}" for key,_ in METHODS) + " |\n"
    manuscript = (ROOT / "paper.md").read_text()
    if manuscript.count("<!-- RESULTS_TABLE -->") != 1 or manuscript.count("<!-- ITEMS_TABLE -->") != 1:
        raise ValueError("Missing publication table slot")
    manuscript = manuscript.replace("<!-- RESULTS_TABLE -->",table).replace("<!-- ITEMS_TABLE -->",items)
    for heading in ("Appendix A. Item-level benchmark", "Appendix B. Reproduction record", "References"):
        manuscript = manuscript.replace("# " + heading, "# " + heading + " {.unnumbered}")
    (ROOT / "manuscript.md").write_text(manuscript)
    figures(data, result)
    common = ["pandoc", "manuscript.md", "--standalone", "--citeproc", "--bibliography=references.json",
              "--number-sections", "--metadata=link-citations:true"]
    pdf_source = manuscript.replace("Figure 1. Information flow", "Information flow").replace("Figure 2. Item-level", "Item-level")
    # Use vector PDF figures in TeX; HTML uses their equivalent SVG editions.
    with tempfile.TemporaryDirectory(prefix="wt-paper-") as tmp:
        pd = Path(tmp) / "paper.md";pd.write_text(pdf_source)
        pdfargs = common.copy();pdfargs[1] = str(pd)
        pdfargs += ["--pdf-engine=xelatex", "--include-in-header=header.tex", "--lua-filter=latex-layout.lua", "--variable=documentclass:article",
                    "--variable=fontsize:11pt", "--variable=geometry:margin=25mm", "--variable=mainfont:Latin Modern Roman",
                    "--variable=sansfont:Latin Modern Sans", "--variable=monofont:DejaVu Sans Mono",
                    "--variable=colorlinks:true", "--variable=linkcolor:teal", "--variable=urlcolor:teal"]
        subprocess.run(pdfargs + ["--to=latex", "-o", STEM + ".tex"], cwd=ROOT, check=True)
        subprocess.run(pdfargs + ["-o", STEM + ".pdf"], cwd=ROOT, check=True)
    html = manuscript.replace("figures/evidence-flow.pdf", "/research/wind-tunnel/paper/figures/evidence-flow.svg")\
                     .replace("figures/benchmark-items.pdf", "/research/wind-tunnel/paper/figures/benchmark-items.svg")
    with tempfile.TemporaryDirectory(prefix="wt-html-") as tmp:
        hp=Path(tmp)/"paper.md";hp.write_text(html)
        args=common.copy();args[1]=str(hp)
        subprocess.run(args+["--to=html5","--mathml","--toc","--toc-depth=2","--template=web-template.html","-o","index.html"],cwd=ROOT,check=True)
        subprocess.run([a for a in args if a != "--standalone"]+["--to=html5","--mathml","-o","article.html"],cwd=ROOT,check=True)
    article=(ROOT/"article.html").read_text()
    article=re.sub(r'<(/?)h([1-5])(?=[ >])',lambda m:'<'+m[1]+'h'+str(int(m[2])+1),article)
    article=re.sub(r'(<table[^>]*>)([\s\S]*?</table>)\s*<p>(Table [\s\S]*?)</p>',
                   lambda m:m[1]+'<caption>'+m[3]+'</caption>'+m[2],article)
    article=re.sub(r'\sstyle="[^"]*"','',article)
    (ROOT/"article.html").write_text(article)
    page=(ROOT/"index.html").read_text()
    page=re.sub(r'(<article class="paper-content"[^>]*>)[\s\S]*?(</article>)',lambda m:m[1]+article+m[2],page,count=1)
    (ROOT/"index.html").write_text(page)
    abstract=re.search(r'<section class="abstract"[^>]*>[\s\S]*?</h2>([\s\S]*?)</section>',page).group(1).strip()
    (ROOT/"paper.json").write_text(json.dumps({'id':'WT-2026-01','version':VERSION,'date':'2026-11-23',
        'title':'Wind Tunnel: Evidence-Separated Population Modeling and AI-Assisted Questionnaire Pretesting',
        'abstractHtml':abstract,'articleHtml':article},ensure_ascii=False,indent=2)+'\n')
    (ROOT / "citation.bib").write_text('''@techreport{tacitus2026windtunnel,
  author = {{TACITUS}},
  title = {Wind Tunnel: Evidence-Separated Population Modeling and AI-Assisted Questionnaire Pretesting},
  institution = {TACITUS},
  year = {2026},
  month = nov,
  number = {WT-2026-01},
  type = {Working paper},
  version = {1.0},
  url = {https://tacitus.me/research/wind-tunnel/paper/},
  note = {Version 1.0. Not independently peer-reviewed.}
}
''')
    (ROOT / "results.json").write_text(json.dumps(result,indent=2)+"\n")
    files=["index.html","article.html","paper.json","paper.css","citation.bib",STEM+".pdf",STEM+".tex","paper.md","manuscript.md","references.json","header.tex","latex-layout.lua","build.py","web-template.html","results.json","verify.py","README.md",
           "figures/evidence-flow.pdf","figures/evidence-flow.svg","figures/benchmark-items.pdf","figures/benchmark-items.svg"]
    manifest={"publication":"WT-2026-01","version":VERSION,"date":"2026-11-23","status":"working paper; not independently peer-reviewed",
        "benchmarkSourceCommit":"2b51dfee375b1ee0e5fd1ee7a99edd1623d8cac4","benchmarkSha256":hashlib.sha256(BENCHMARK.read_bytes()).hexdigest(),
        "files":{f:{"bytes":(ROOT/f).stat().st_size,"sha256":hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f in files}}
    (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"publication":manifest["publication"],"version":VERSION,"items":len(result["items"]),"files":len(files),"scores":result["summary"]},indent=2))


if __name__ == "__main__":
    main()
