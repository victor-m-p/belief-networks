## prototypes.py

import matplotlib.pyplot as plt


QUESTIONS_SC =[
    "concerned about climate", 
    "equal adoption rights for gay couples", 
    "migration enriches culture",
    "state should act to reduce income differences"]
questiontext = [
        'I am very concerned about climate change.', 
        'Gay and lesbian couples should have the same rights to adopt children as couples consisting of a man and a woman.', 
        'It is enriching for cultural life in Germany when migrants come here.', 
        'The state should take measures to reduce income differences more than before.']

vals_arr = {
    "P1": [0,0, 0,-1],  # LIB
    "P2": [0, -1, 0, -1], # climate-hoax RIGHT 
    "P3": [1, 1, 1, 1], # LEFT
    "P4": [0,  0, -1, 0], # RIGHT
}


for p, vals in vals_arr.items():

    fig, ax = plt.subplots(1,1,figsize=(16/2.54, 12/2.54))
    y = [3, 2,1,0]
    bar_heights = [v + (0. if abs(v)>0 else 0.05)  for v in vals ]
    ax.barh(y, bar_heights, color=["green", "purple", "blue", "red"], height=0.5)
    ax.set_yticks([])
    ax.set_xticks([-1,0,1])
    #ax.set_xticklabels(["strongly\ndisagree", "neutral", "strongly\nagree"])
    for n, qsc in enumerate(QUESTIONS_SC):
        ax.text(-0.,y[n]+0.43, qsc, rotation=0, va="center", ha="center", bbox={"pad":4, "facecolor":"gainsboro", "edgecolor":"gainsboro", "alpha":0.7})
        ax.text(-1.05, y[n], "Strongly\ndisagree", va="center", ha="right")
        ax.text(1.05, y[n], "Strongly\nagree", va="center", ha="left")
    ax.spines['bottom'].set_visible(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.hlines(y, -1, [min(v, 0) for v in vals], linestyles="--", lw=0.5, colors="grey")
    ax.hlines(y, 1, [max(v, 0) for v in vals],  linestyles="--", lw=0.5, colors="grey")
    ax.set_xlim(-1,1)
    ax.vlines(0,-0.5,3.5, colors="grey")
    ax.text(0.8, 3.5, f"{p}", ha="center", va="bottom", fontsize=20)
    ax.set_ylim(-0.5, 3.5)
    fig.tight_layout()
    print(f"{p}.png")
    plt.savefig(f"{p}_op.png", dpi=600)

