"""Draw the report's figures from aggregate exports; needs matplotlib and numpy.

These plots contain no source text, author names, video IDs, or individual records.
Both standard and narrow-screen figures are generated, with shared definitions.
"""
from pathlib import Path
import csv
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"figures"
OUT.mkdir(exist_ok=True)
SUMMARY = json.loads((ROOT/"data/summary.json").read_text())
TOPICS = list(csv.DictReader((ROOT/"data/topic-prevalence.csv").open()))
ADVICE = list(csv.DictReader((ROOT/"data/advice-estimates.csv").open()))
INK, MUTED, PAPER, LINE, BRASS, SLATE = "#302923", "#6e6255", "#f7f2e8", "#ded4c5", "#86643b", "#526674"
LABELS = {
    "heads-up-pot": "Two-player pots", "c-bet-flop": "Betting again on flop (c-bet)",
    "three-bet-pot": "Preflop re-raise (three-bet)", "wet-connected-board": "Connected shared cards",
    "single-raised-pot": "One preflop raise", "deep-stack-spot": "Deep stacks",
    "multi-way-pot": "Multi-player pots", "check-call-down": "Check and call",
    "iso-raise": "Isolation raise", "standard-stack-spot": "Standard stacks",
    "draw-heavy-board": "Draw-heavy shared cards", "overbet-river": "Larger-than-pot river bet",
    "hero-call": "Hero call", "squeeze": "Squeeze play", "check-raise-bluff": "Check-raise bluff",
    "paired-board": "Paired shared cards", "trap-slowplay": "Disguising strength (slow-play)",
    "delayed-c-bet": "Delayed continuation bet", "monotone-board": "Single-suit shared cards"
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
    "axes.facecolor": PAPER, "figure.facecolor": PAPER, "text.color": INK,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
    "axes.edgecolor": LINE, "svg.fonttype": "path", "savefig.facecolor": PAPER,
    "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(OUT/(name+"."+ext), dpi=180, bbox_inches="tight", pad_inches=.18,
                    metadata={"Creator": "Elias Brown poker project; 2026 AI-assisted descriptive reanalysis"})
    plt.close(fig)


def base_axes(ax, xmax=100):
    ax.set_xlim(0, xmax)
    ax.xaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax.xaxis.set_major_locator(MultipleLocator(20 if xmax>65 else 10))
    ax.grid(axis="x", color=LINE, linewidth=.7)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)


def forum_topics(narrow=False):
    rows = sorted(TOPICS, key=lambda r: (-int(r["hand_records"]), r["topic"]))[:10]
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(5.0 if narrow else 9.0, 8 if narrow else 5.9))
    if narrow:
        ax.barh(y+.15, [float(r["hand_percent"]) for r in rows], color=BRASS, height=.32)
        ax.set_yticks([])
        for i,r in enumerate(rows):
            ax.text(0, i-.15, LABELS[r["topic"]], fontsize=12, va="center")
            ax.text(float(r["hand_percent"])+1, i+.15, f'{float(r["hand_percent"]):.1f}%', va="center", fontsize=11)
        ax.set_ylim(len(rows)-.5, -.55)
    else:
        ax.barh(y, [float(r["hand_percent"]) for r in rows], color=BRASS, height=.55)
        ax.set_yticks(y, [LABELS[r["topic"]] for r in rows]);ax.invert_yaxis()
        for i,r in enumerate(rows):
            ax.text(float(r["hand_percent"])+1, i, f'{int(r["hand_records"]):,}  /  {float(r["hand_percent"]):.1f}%', va="center", fontsize=11)
    base_axes(ax, 85 if not narrow else 80)
    ax.set_xlabel("Share of 1,000 labeled hand accounts", labelpad=12, fontsize=11)
    fig.tight_layout()
    save(fig, "forum-topics"+("-mobile" if narrow else ""))


def shared_topics(narrow=False):
    rows=sorted([r for r in TOPICS if int(r["videos"]) and int(r["hand_records"])],
                key=lambda r: (-int(r["videos"]), r["topic"]))
    fig,ax=plt.subplots(figsize=(4.5 if narrow else 9.2, 10.5 if narrow else 7.1))
    for i,r in enumerate(rows):
        h,v=float(r["hand_percent"]),float(r["video_percent"])
        y=i+.17 if narrow else i
        ax.plot([h,v],[y,y], color=LINE, linewidth=2, zorder=1)
        ax.scatter(h,y,s=65,color=BRASS,marker="o",label="Hand accounts" if i==0 else None,zorder=3)
        ax.scatter(v,y,s=65,color=SLATE,marker="D",label="Videos" if i==0 else None,zorder=3)
        if narrow:
            ax.text(0,i-.2,LABELS[r["topic"]],fontsize=12,va="center")
            ax.text(76,y,f'{h:.1f}% / {v:.1f}%',va="center",fontsize=11,color=MUTED)
        else:
            ax.text(76,i,f'{h:.1f}%  /  {v:.1f}%',va="center",fontsize=10,color=MUTED)
    ax.set_yticks([] if narrow else np.arange(len(rows)), [] if narrow else [LABELS[r["topic"]] for r in rows])
    ax.set_ylim(len(rows)-.4,-.6)
    base_axes(ax,100)
    ax.set_xlabel("Share with this topic in each source",labelpad=12,fontsize=11)
    ax.legend(loc="lower left",bbox_to_anchor=(-.02,1.01),frameon=False,ncol=2,fontsize=11)
    fig.tight_layout()
    save(fig,"shared-topics"+("-mobile" if narrow else ""))


def advice_density(narrow=False):
    rows=SUMMARY["advice_summary"]
    labels={"general_advice":"General advice", "hand_review":"Hand reviews", "promo":"Promotional", "storytelling":"Storytelling"}
    fig,ax=plt.subplots(figsize=(5.0 if narrow else 9.0,5.5 if narrow else 4.8))
    for i,row in enumerate(rows):
        counts={float(r["estimate_percent"]):int(r["videos"]) for r in ADVICE if r["segment_type"]==row["segment_type"]}
        for x,n in counts.items():
            offsets=(np.arange(n)-(n-1)/2)*.09
            ax.scatter([x]*n,i+offsets,color=SLATE,s=27,alpha=.8,edgecolors=PAPER,linewidth=.5,clip_on=False)
        ax.plot([row["median_estimate"]]*2,[i-.31,i+.31],color=BRASS,linewidth=2.5)
        ax.text(row["median_estimate"]+2, i-.38, f'{row["median_estimate"]:g}%', color=BRASS, fontsize=10, fontweight="bold")
    names=[f'{labels[r["segment_type"]]}\n(n = {r["videos"]})' for r in rows]
    ax.set_yticks(np.arange(4),names,fontsize=11)
    ax.set_ylim(3.6,-.7)
    base_axes(ax)
    ax.set_xlabel("Estimated share of text giving advice",labelpad=12,fontsize=11)
    fig.tight_layout()
    save(fig,"advice-density"+("-mobile" if narrow else ""))


for narrow in (False,True):
    forum_topics(narrow);shared_topics(narrow);advice_density(narrow)
print("Created three analytical figures, each with standard and mobile SVG/PNG versions.")
