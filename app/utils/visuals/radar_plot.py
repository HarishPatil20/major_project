import matplotlib.pyplot as plt
import numpy as np

def radar_chart(conf, mc_unc, tta_unc, fused_unc):
    labels = ["Confidence", "MC Unc", "TTA Unc", "Fused Unc"]
    values = [conf, mc_unc, tta_unc, fused_unc]

    # Close the chart circle
    angles = np.linspace(0, 2 * np.pi, len(values), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    # ---------------------------
    # DARK MODE FIGURE SETTINGS
    # ---------------------------
    fig = plt.figure(figsize=(4, 4), facecolor="#0e1117")   # small + dark background
    ax = fig.add_subplot(111, polar=True)
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    # Grid style
    ax.grid(color="#444", linestyle="dotted", linewidth=0.8)

    # Axis labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color="white", fontsize=10)

    ax.set_yticklabels([])
    ax.set_yticks([])

    # Line + Fill
    ax.plot(angles, values, color="#00b4d8", linewidth=2)
    ax.fill(angles, values, color="#00b4d8", alpha=0.25)

    # Outer border
    for spine in ax.spines.values():
        spine.set_color("#888")
        spine.set_linewidth(1.2)

    return fig
