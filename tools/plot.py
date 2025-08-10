from __future__ import annotations

import io, base64
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt


def scatter_with_regression_base64(x, y, xlabel="x", ylabel="y", max_bytes: int | None = None):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    fig = plt.figure(figsize=(4, 3), dpi=120)
    ax = fig.add_subplot(111)
    ax.scatter(x, y)
    if len(x) >= 2:
        a, b = np.polyfit(x, y, 1)
        xr = np.array([x.min(), x.max()])
        yr = a * xr + b
        ax.plot(xr, yr, linestyle=":", linewidth=2)  # dotted regression line
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    fig.tight_layout()

    for dpi in (120, 100, 90, 80, 72):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi)
        data = buf.getvalue()
        if max_bytes is None or len(data) < max_bytes:
            uri = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
            plt.close(fig)
            return uri
    plt.close(fig)
    return ""
