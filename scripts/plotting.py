"""House style and plotting helpers for the B8_MolecularGas notebooks.

One place for how figures look, so every notebook on either machine draws the same way:

    from utils import plotting as pl
    pl.use_style()                                     # once, at the top of a notebook
    fig, ax = pl.figure("column")                      # journal column width
    pl.plot_families(ax, dwarfs, "M_V", "metallicity_spectroscopic",
                     err=("metallicity_spectroscopic_em", "metallicity_spectroscopic_ep"))
    fit_h = pl.plot_fit(ax, fit, (-18, 0), scatter=0.31, label="fit")   # line with its 1-sigma band
    halo_h = pl.mark_simulation(ax, -10.6, -1.49)      # the simulated galaxy, always on top
    pl.magnitude_axis(ax)                              # M_V, bright to the right
    pl.figure_legend(fig, [fit_h, (halo_h, "Halo 605")])   # legend below the axes, off the data
    pl.label_point(ax, -10.6, -1.49, "Halo 605", avoid=(dwarfs, "M_V", "metallicity_spectroscopic"))
    pl.save(fig, "feh_mv", "figures")                  # vector PDF + 300 dpi PNG (skipped if dir is None)

Design rules the helpers enforce:
  * sizes are set for print: figures are made at journal width (3.4 in column, 7.0 in page) with
    8-9 pt text, so they need no rescaling when they go into a paper;
  * data recede, relations and the simulation stand out: small translucent points, a dark fit line
    with a grey scatter band, and one bold star for the simulated galaxy drawn above everything;
  * every family has a colour AND a marker shape (Okabe & Ito colours, checked for colour-blind
    separation), so the figure survives greyscale printing;
  * upper limits are open downward triangles with an arrow, never filled points.

Works with matplotlib >= 3.8 (archlinux has 3.11, py-noether 3.8.4); needs no LaTeX installation.
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# ---------------------------------------------------------------------------------------------------
# Sizes and style
# ---------------------------------------------------------------------------------------------------
WIDTHS = {"column": 3.4, "page": 7.0}          # inches: one journal column, the full text width

FAMILY_STYLE = {                              # colour (Okabe & Ito 2008) and marker per dwarf family
    "Milky Way satellite":  dict(color="#0072B2", marker="o"),
    "M31 satellite":        dict(color="#E69F00", marker="s"),
    "Local Field":          dict(color="#009E73", marker="D"),
    "Local Field, distant": dict(color="#CC79A7", marker="^"),
}
LIMIT_COLOUR = "0.45"
FIT_COLOUR = "0.15"
BAND_COLOUR = "0.80"
SIM_STYLE = dict(marker="*", ms=15, mfc="#D55E00", mec="black", mew=0.9, ls="none", zorder=10)

STYLE = {
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 8.5, "axes.labelsize": 9, "axes.titlesize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 7.5, "legend.frameon": True, "legend.framealpha": 0.85, "legend.edgecolor": "none",
    "legend.fancybox": False, "legend.borderpad": 0.3, "legend.handletextpad": 0.3, "legend.borderaxespad": 0.4,
    "legend.labelspacing": 0.3, "legend.columnspacing": 1.0,
    "axes.linewidth": 0.7, "axes.titlepad": 4, "axes.labelpad": 3,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "xtick.major.size": 3.5, "ytick.major.size": 3.5, "xtick.minor.size": 2, "ytick.minor.size": 2,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.minor.width": 0.5, "ytick.minor.width": 0.5,
    "lines.linewidth": 1.1, "lines.markersize": 4, "errorbar.capsize": 0,
    "pdf.fonttype": 42, "ps.fonttype": 42,     # embed TrueType, so journals accept the PDF
}


def use_style():
    """Apply the house style to every figure made after this call."""
    mpl.rcParams.update(STYLE)


def figure(width="column", nrows=1, ncols=1, aspect=0.82, **kwargs):
    """A figure at journal width. aspect is the height of one panel over its width."""
    w = WIDTHS.get(width, width)
    h = w / ncols * aspect * nrows
    kwargs.setdefault("constrained_layout", True)
    return plt.subplots(nrows, ncols, figsize=(w, h), **kwargs)


def save(fig, name, directory=None, formats=("pdf", "png")):
    """Write the figure as a vector PDF and a 300 dpi PNG. Does nothing if directory is None."""
    if directory is None:
        return []
    os.makedirs(directory, exist_ok=True)
    paths = [os.path.join(directory, f"{name}.{ext}") for ext in formats]
    for p in paths:
        fig.savefig(p)
    return paths


# ---------------------------------------------------------------------------------------------------
# Axes furniture
# ---------------------------------------------------------------------------------------------------
def magnitude_axis(ax, label=r"$M_V$ (mag)", major=None):
    """x = absolute magnitude, bright to the right, with whole-magnitude ticks."""
    from matplotlib.ticker import MultipleLocator
    if not ax.xaxis_inverted():
        ax.invert_xaxis()
    lo, hi = sorted(ax.get_xlim())
    major = major or (5 if hi - lo > 12 else 2)
    ax.xaxis.set_major_locator(MultipleLocator(major))
    ax.xaxis.set_minor_locator(MultipleLocator(1 if major == 5 else 0.5))
    ax.set_xlabel(label)


def secondary_x(ax, forward, inverse, label):
    """A second x scale on the top axis (e.g. stellar mass for M_V). Top ticks of the main axis are hidden."""
    ax.tick_params(axis="x", which="both", top=False)
    top = ax.secondary_xaxis("top", functions=(forward, inverse))
    top.set_xlabel(label)
    top.tick_params(axis="x", which="both", direction="in")
    top.minorticks_on()
    return top


def panel_label(ax, text, loc="upper left"):
    """'(a)', '(b)' ... in a panel corner."""
    x, ha = (0.04, "left") if "left" in loc else (0.96, "right")
    y, va = (0.95, "top") if "upper" in loc else (0.05, "bottom")
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=9)


# ---------------------------------------------------------------------------------------------------
# Data layers
# ---------------------------------------------------------------------------------------------------
def plot_families(ax, rows, x, y, err=None, family="family", styles=FAMILY_STYLE, size=3.6, alpha=0.75,
                  hollow_unquoted=False, counts=True):
    """One layer per family: colour and marker from styles, optional asymmetric 1-sigma error bars.

    err = (lower, upper) column names. With hollow_unquoted, rows with no quoted error are drawn open.
    Returns legend handles, one per family drawn.
    """
    handles = []
    for name, st in styles.items():
        s = rows[(rows[family] == name) & rows[x].notna() & rows[y].notna()]
        if s.empty:
            continue
        quoted = s[s[err[0]].notna() & s[err[1]].notna()] if err else s
        other = s.drop(quoted.index) if err else s.iloc[0:0]
        if err and len(quoted):
            ax.errorbar(quoted[x], quoted[y], yerr=quoted[[err[0], err[1]]].to_numpy().T, fmt="none",
                        ecolor=st["color"], elinewidth=0.5, alpha=0.45 * alpha, zorder=2)
        ax.plot(quoted[x], quoted[y], ls="none", marker=st["marker"], ms=size, mfc=st["color"],
                mec="white", mew=0.25, alpha=alpha, zorder=3)
        if len(other):
            if hollow_unquoted:
                ax.plot(other[x], other[y], ls="none", marker=st["marker"], ms=size, mfc="none",
                        mec=st["color"], mew=0.7, alpha=alpha, zorder=3)
            else:
                ax.plot(other[x], other[y], ls="none", marker=st["marker"], ms=size, mfc=st["color"],
                        mec="white", mew=0.25, alpha=alpha, zorder=3)
        handles.append(Line2D([], [], ls="none", marker=st["marker"], ms=size + 0.6, mfc=st["color"],
                              mec="white", mew=0.25, label=f"{name} ({len(s)})" if counts else name))
    return handles


def plot_upper_limits(ax, x, y, length=0.4, colour=LIMIT_COLOUR, alpha=0.7, label="upper limit"):
    """The classic upper-limit symbol: a short bar at the limit with an arrow `length` (data units) down.

    Returns a legend handle.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    ax.errorbar(x, y, yerr=[np.full_like(y, length), np.zeros_like(y)], uplims=False, lolims=False,
                fmt="none", ecolor=colour, elinewidth=0.6, alpha=alpha, zorder=2)
    ax.plot(x, y, ls="none", marker="_", ms=4, mec=colour, mew=0.8, alpha=alpha, zorder=2)
    ax.plot(x, y - length, ls="none", marker="v", ms=2.6, mfc=colour, mec=colour, mew=0, alpha=alpha, zorder=2)
    return Line2D([], [], ls="none", marker=r"$\downarrow$", ms=7, mfc=colour, mec=colour, mew=0.4,
                  label=f"{label} ({len(x)})")


def plot_fit(ax, fit, x_range, scatter=None, log=False, ls="-", colour=FIT_COLOUR, label=None, band=True):
    """A linregress-style fit (intercept, slope) over x_range, with a +-scatter band.

    log=True when the fit was made in log10(y) but the axis shows y on a log scale.
    Returns a legend handle.
    """
    xs = np.linspace(*sorted(x_range), 100)
    ys = fit.intercept + fit.slope * xs
    tr = (lambda v: 10 ** v) if log else (lambda v: v)
    if scatter and band:
        ax.fill_between(xs, tr(ys - scatter), tr(ys + scatter), color=BAND_COLOUR, alpha=0.45, lw=0, zorder=1)
    ax.plot(xs, tr(ys), color=colour, lw=1.2, ls=ls, zorder=4)
    if scatter and band:
        return (Line2D([], [], color=colour, lw=1.2, ls=ls),
                mpl.patches.Patch(color=BAND_COLOUR, alpha=0.45, lw=0)), label
    return Line2D([], [], color=colour, lw=1.2, ls=ls, label=label), label


def mark_simulation(ax, x, y, style=None):
    """The simulated galaxy: one bold star above everything. Returns a legend handle (label it yourself)."""
    st = dict(SIM_STYLE, **(style or {}))
    ax.plot([x], [y], **st)
    return Line2D([], [], **dict({k: v for k, v in st.items() if k != "zorder"}, ms=10))


def label_point(ax, x, y, text, avoid=None, bold=True, radii=(26, 40, 56)):
    """Name one point, placed clear of the data in avoid = (rows, xcol, ycol), other labels and the legend.

    Call it after the legend is drawn, so the legend is avoided too.
    """
    offset = _place_label(ax, (x, y), avoid, radii=radii)
    ax.annotate(text, (x, y), xytext=offset, textcoords="offset points", fontsize=8,
                fontweight="bold" if bold else "normal", ha="center", va="center", zorder=11,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                arrowprops=dict(arrowstyle="-", color="black", lw=0.6, shrinkA=0, shrinkB=7))


def open_marker_handle(label="open: no 1$\\sigma$ quoted"):
    """Legend entry for rows drawn open by plot_families(hollow_unquoted=True)."""
    return Line2D([], [], ls="none", marker="o", ms=4.2, mfc="none", mec="0.35", mew=0.7, label=label)


_PLACED = {}            # axes -> label centres already used (pixels), shared by all labelling helpers


def _place_label(ax, xy, avoid, radii=(22, 36, 52, 72), min_gap=(62, 16), pad_px=24):
    """Offset (points) for a label near data point xy: inside the axes, clear of other labels and of
    the points in `avoid`, preferring short leaders."""
    ax.figure.canvas.draw()
    placed = _PLACED.setdefault(ax, [])
    pixels = np.empty((0, 2))
    if avoid is not None:
        rows, xc, yc = avoid
        pts = rows[[xc, yc]].to_numpy(float)
        pixels = ax.transData.transform(pts[np.isfinite(pts).all(axis=1)])
    # legends are obstacles too
    boxes = [lg.get_window_extent() for lg in [ax.get_legend()] if lg is not None]
    inner = ax.bbox.padded(-pad_px)
    centre = ax.transData.transform(xy)
    best, score = None, -np.inf
    for r in radii:
        for a in np.arange(16) * np.pi / 8:
            s = r * np.array([np.cos(a), np.sin(a)])
            p = centre + s
            if not inner.contains(*p) or any(b.padded(8).contains(*p) for b in boxes):
                continue
            if any(abs(p[0] - q[0]) < min_gap[0] and abs(p[1] - q[1]) < min_gap[1] for q in placed):
                continue
            d = (np.hypot(*(pixels - p).T).min() if len(pixels) else 1e3) - 0.05 * r
            if d > score:
                best, score = s, d
    if best is None:
        best = np.array([radii[0], 0.0])
    placed.append(centre + best)
    return tuple(best * 72 / ax.figure.dpi)


def label_objects(ax, rows, x, y, names, key="key"):
    """Ring and name selected objects (names = {key: label}), each label placed where it is least crowded."""
    for k, name in names.items():
        hit = rows[rows[key] == k]
        if hit.empty or not np.isfinite(hit[[x, y]].to_numpy(float)).all():
            continue
        px, py = hit[x].iloc[0], hit[y].iloc[0]
        offset = _place_label(ax, (px, py), (rows, x, y))
        ax.plot([px], [py], ls="none", marker="o", ms=7.5, mfc="none", mec="black", mew=0.7, zorder=6)
        ax.annotate(name, (px, py), xytext=offset, textcoords="offset points", fontsize=7.5, ha="center",
                    va="center", zorder=7, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8),
                    arrowprops=dict(arrowstyle="-", color="0.3", lw=0.5, shrinkA=0, shrinkB=3.5))


def legend(ax, entries, **kwargs):
    """Legend from a list of artists (labelled) or (artist, label) pairs; tuples of artists overlay."""
    from matplotlib.legend_handler import HandlerTuple
    handles, labels = [], []
    for e in entries:
        if e is None:
            continue
        h, l = e if isinstance(e, tuple) and len(e) == 2 and isinstance(e[1], str) else (e, e.get_label())
        handles.append(h)
        labels.append(l)
    kwargs.setdefault("handler_map", {tuple: HandlerTuple(ndivide=None, pad=0)})
    return ax.legend(handles, labels, **kwargs)


def figure_legend(fig, entries, loc="outside lower center", ncol=2, **kwargs):
    """Legend outside the axes (below by default), so it never covers data. Same entries as legend()."""
    from matplotlib.legend_handler import HandlerTuple
    handles, labels = [], []
    for e in entries:
        if e is None:
            continue
        h, l = e if isinstance(e, tuple) and len(e) == 2 and isinstance(e[1], str) else (e, e.get_label())
        handles.append(h)
        labels.append(l)
    kwargs.setdefault("handler_map", {tuple: HandlerTuple(ndivide=None, pad=0)})
    return fig.legend(handles, labels, loc=loc, ncol=ncol, **kwargs)
