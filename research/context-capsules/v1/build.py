#!/usr/bin/env python3
"""Build the proposal and replay its context. No network or model calls."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import subprocess
import tempfile

from replay import replay, main as replay_outputs

ROOT = Path(__file__).resolve().parent
STEM = 'tacitus-context-capsules-v1.0'
TITLE = 'TACITUS: Context Capsules, Artefacts, and Small Knowledge Graphs for AI Generation'
URL = 'https://tacitus.me/research/context-capsules/paper/'
FIXED_DATE = datetime.datetime(2026,11,23,tzinfo=datetime.timezone.utc)


def figures():
    os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'tacitus-context-paper-matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,
                         'svg.fonttype':'none','svg.hashsalt':'tac-context-v1.0'})
    out=ROOT/'figures';out.mkdir(exist_ok=True)

    def box(ax,x,y,w,h,title,body,color='#edf3f0',dashed=False):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.07,rounding_size=0.04',
            facecolor=color,edgecolor='#647c75',lw=.8,linestyle='--' if dashed else '-'))
        ax.text(x+w/2,y+h*.73,title,ha='center',va='center',weight='bold',fontsize=8,color='#173b3d')
        ax.text(x+w/2,y+h*.32,body,ha='center',va='center',fontsize=7.1,color='#334b52',linespacing=1.45)

    def arrow(ax,a,b,label=None,dashed=False,rad=0):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,lw=.85,color='#547477',
            linestyle='--' if dashed else '-',connectionstyle=f'arc3,rad={rad}'))
        if label:
            ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.1,label,ha='center',va='bottom',fontsize=6.7,
                    color='#4d6265',bbox={'facecolor':'white','edgecolor':'none','pad':1.6})

    def save(fig,name):
        fig.savefig(out/(name+'.pdf'),bbox_inches='tight',metadata={'Creator':'TACITUS','CreationDate':FIXED_DATE,'ModDate':FIXED_DATE})
        fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Creator':'TACITUS','Date':'2026-11-23'})
        plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.1,4.1));ax.set(xlim=(0,10),ylim=(0,6));ax.axis('off')
    box(ax,.15,4.55,2.55,1.05,'Exact sources','Edition · quote · scope\nSource lineage')
    box(ax,3.7,4.55,2.55,1.05,'Small case graph','Claims · conditions · objections\nTyped, attributed relationships')
    box(ax,7.2,4.55,2.55,1.05,'Human review','Accept or reject a version\nRecord scope and rationale',color='#f5f0e7')
    box(ax,.15,2.45,2.55,1.05,'Team context','Discussion · wording decisions\nCapsule + example artefacts',color='#f5f0e7')
    box(ax,3.7,2.45,2.55,1.05,'Context compiler','Selected whole evidence\nDependencies · omissions · hash')
    box(ax,7.2,2.45,2.55,1.05,'Bounded generation','Selected model + allowed tools\nRequested output + usage receipt',color='#edf0f6',dashed=True)
    box(ax,3.7,.3,2.55,1.05,'Proposed artefact','Sources + context receipt\nExplicit edits and versions')
    box(ax,7.2,.3,2.55,1.05,'Handover and evaluation','Another person or agent\nMeasure quality, effort and cost',color='#edf0f6',dashed=True)
    arrow(ax,(2.8,5.08),(3.6,5.08));arrow(ax,(6.35,5.08),(7.1,5.08))
    arrow(ax,(8.48,4.45),(6.4,3.35));arrow(ax,(4.98,4.45),(4.98,3.6))
    arrow(ax,(2.8,2.98),(3.6,2.98));arrow(ax,(6.35,2.98),(7.1,2.98))
    arrow(ax,(8.48,2.35),(6.4,.85));arrow(ax,(6.35,.83),(7.1,.83))
    ax.text(1.43,.85,'Evidence and instructions\nretain different authority',ha='center',va='center',fontsize=7.4,color='#586966')
    fig.tight_layout(pad=.15);save(fig,'context-flow')

    fig,ax=plt.subplots(figsize=(7.1,4.3));ax.set(xlim=(0,10),ylim=(0,6.4));ax.axis('off')
    box(ax,.15,4.7,2.6,1.1,'Source e1','Conditional permission\nRenewal for six months')
    box(ax,3.7,4.7,2.6,1.1,'Interpretation','Permission ≠ final approval\nProposed and inspectable')
    box(ax,7.25,4.7,2.6,1.1,'Required condition','Independent reviewer\naccepts the risk note',color='#f5f0e7')
    box(ax,.15,2.45,2.6,1.1,'Source e2','Objection: incomplete note\nNo final approval recorded')
    box(ax,3.7,2.45,2.6,1.1,'Decision note','Status · conditions · objections\nMissing evidence · next check',color='#edf0f6')
    box(ax,7.25,2.45,2.6,1.1,'Team wording decision','Keep the condition and objection\nwhen reusing the analysis',color='#f5f0e7')
    arrow(ax,(2.85,5.25),(3.6,5.25), 'supports')
    arrow(ax,(6.4,5.25),(7.15,5.25), 'requires')
    arrow(ax,(5,4.6),(5,3.65),'informs')
    arrow(ax,(2.85,3),(3.6,3),'qualifies')
    arrow(ax,(7.15,3),(6.4,3),'guides',True)
    ax.text(5,1.55,'The graph preserves a distinction the final sentence must retain.',ha='center',fontsize=8.1,weight='bold',color='#23434a')
    ax.text(5,.9,'Synthetic illustration. Edges organize authored readings; they are not additional evidence.\nThe executable reference uses exact spans and reified statement records.',ha='center',fontsize=7.3,color='#586966',linespacing=1.5)
    fig.tight_layout(pad=.15);save(fig,'qualified-context')


def main():
    os.environ.setdefault('SOURCE_DATE_EPOCH',str(int(FIXED_DATE.timestamp())))
    replay_outputs()
    bundle, observations=replay()
    figures()
    manuscript=(ROOT/'paper.md').read_text()
    (ROOT/'manuscript.md').write_text(manuscript)
    common=['pandoc','manuscript.md','--standalone','--citeproc','--bibliography=references.json',
            '--number-sections','--metadata=link-citations:true']
    pdf=manuscript.replace('Figure 1. Proposed information flow.','Proposed information flow.')\
                  .replace('Figure 2. A conceptual small graph','A conceptual small graph')
    pdf=re.sub(r'(?m)^: Table [1-4]\.\s*', ': ', pdf)
    with tempfile.TemporaryDirectory(prefix='tac-context-pdf-') as temp:
        path=Path(temp)/'paper.md';path.write_text(pdf)
        args=common.copy();args[1]=str(path)
        args+=['--pdf-engine=xelatex','--include-in-header=header.tex','--lua-filter=latex-layout.lua',
               '--variable=documentclass:article','--variable=fontsize:11pt','--variable=geometry:margin=25mm',
               '--variable=mainfont:Latin Modern Roman','--variable=sansfont:Latin Modern Sans',
               '--variable=monofont:DejaVu Sans Mono','--variable=colorlinks:true',
               '--variable=linkcolor:teal','--variable=urlcolor:teal']
        subprocess.run(args+['--to=latex','-o',STEM+'.tex'],cwd=ROOT,check=True)
        subprocess.run(args+['-o',STEM+'.pdf'],cwd=ROOT,check=True)
    html=manuscript.replace('figures/context-flow.pdf','/research/context-capsules/paper/figures/context-flow.svg')\
                   .replace('figures/qualified-context.pdf','/research/context-capsules/paper/figures/qualified-context.svg')
    with tempfile.TemporaryDirectory(prefix='tac-context-html-') as temp:
        path=Path(temp)/'paper.md';path.write_text(html)
        args=common.copy();args[1]=str(path)
        subprocess.run(args+['--to=html5','--mathml','--toc','--toc-depth=2','--template=web-template.html','-o','index.html'],cwd=ROOT,check=True)
        subprocess.run([a for a in args if a!='--standalone']+['--to=html5','--mathml','-o','article.html'],cwd=ROOT,check=True)
    article=(ROOT/'article.html').read_text()
    article=re.sub(r'<(/?)h([1-5])(?=[ >])',lambda m:'<'+m[1]+'h'+str(int(m[2])+1),article)
    article=re.sub(r'(<table[^>]*>)([\s\S]*?</table>)\s*<p>(Table [\s\S]*?)</p>',
                   lambda m:m[1]+'<caption>'+m[3]+'</caption>'+m[2],article)
    article=re.sub(r'\sstyle="[^"]*"','',article)
    article=re.sub(r'<p>(<math display="block"[\s\S]*?</math>)</p>',
                   lambda m:'<div class="paper-equation" tabindex="0" role="group" aria-label="Equation">'+m[1]+'</div>',article)
    (ROOT/'article.html').write_text(article)
    page=(ROOT/'index.html').read_text()
    page=re.sub(r'(<article class="paper-content"[^>]*>)[\s\S]*?(</article>)',lambda m:m[1]+article+m[2],page,count=1)
    (ROOT/'index.html').write_text(page)
    abstract=re.search(r'<section class="abstract"[^>]*>[\s\S]*?</h2>([\s\S]*?)</section>',page).group(1).strip()
    (ROOT/'paper.json').write_text(json.dumps({'id':'TAC-2026-01','version':'1.0','date':'2026-11-23',
        'title':TITLE,'status':'Research proposal; not independently peer-reviewed; efficacy experiments not run',
        'abstractHtml':abstract,'articleHtml':article},ensure_ascii=False,indent=2)+'\n')
    (ROOT/'citation.bib').write_text('''@techreport{tacitus2026contextcapsules,
  author = {{TACITUS}},
  title = {TACITUS: Context Capsules, Artefacts, and Small Knowledge Graphs for AI Generation},
  institution = {TACITUS},
  year = {2026},
  month = nov,
  number = {TAC-2026-01},
  type = {Research proposal},
  version = {1.0},
  url = {https://tacitus.me/research/context-capsules/paper/},
  note = {Version 1.0. Not independently peer-reviewed. Confirmatory experiments not run.}
}
''')
    files=sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
                 and p.name not in {'manifest.json','.gitignore'} and '__pycache__' not in p.parts)
    reference_root=ROOT.parents[2]/'reference-pipeline'
    inputs=['src/tacitus_pipeline/core.py','src/tacitus_pipeline/interchange.py','ontology/team-knowledge.json',
            'evaluations/2026-11-23-provider-probe/manifest.json']
    manifest={'publication':'TAC-2026-01','version':'1.0','date':'2026-11-23',
        'status':'research proposal; not independently peer-reviewed; confirmatory experiments not run',
        'referenceSourceCommit':'4ea0d2725de97cedca1de391a7f0b495259288de',
        'privateAppSourceReviewCommit':'2f11863ed506502a2bc508840a8e4d30ff69f15f',
        'newInferenceCalls':0,'referenceInputs':{n:hashlib.sha256((reference_root/n).read_bytes()).hexdigest() for n in inputs},
        'files':{f:{'bytes':(ROOT/f).stat().st_size,'sha256':hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f in files}}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'publication':'TAC-2026-01','references':18,'files':len(files),
                      'demoNodes':len(bundle['graph.json']['nodes']),'demoEdges':len(bundle['graph.json']['edges']),
                      'newInferenceCalls':0},indent=2))


if __name__=='__main__':
    main()
