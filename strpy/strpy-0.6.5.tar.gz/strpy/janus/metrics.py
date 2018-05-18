import os
import tempfile
import numpy as np
import math
from scipy import sparse
import strpy.bobo.util
from strpy.bobo.util import tempcsv, temppdf,  islist, tolist, Stopwatch, lower_bound, quietprint, readcsv, readcsvwithheader, writecsv, readlist, groupby, bobo_groupby
import strpy.bobo.metrics
from strpy.janus.dataset.cs2 import CS2
from itertools import product
from strpy.janus.openbr import readbee, writebee, brMaskMatrix, brSimilarityMatrix, openbr_eval, openbr_plot, importbr
import  sklearn.metrics
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from collections import OrderedDict
from strpy.bobo.geometry import BoundingBox
from strpy.bobo.image import ImageDetection
from strpy.bobo.metrics import plot_roc
from strpy.janus.bcubed import bcubed

def get_outfile(basename=None, extension='pdf', extra=None):
    if basename is None:
        if extension == 'pdf':
            name = temppdf()
        elif extension == 'csv':
            name = tempcsv()
        else:
            name = temppdf()
    else:
        dirname, filename = os.path.split(basename)
        # If there's absolutely no directory part, then we're going make it a temporary.
        if dirname == '':
            name = os.path.join(tempfile.gettempdir(), basename)
        file, ext = os.path.splitext(basename)
        if ext == '':
            name = basename + '.' + extension
    if extra is None:
        return name
    else:
        dirname, filename = os.path.split(name)
        base, ext = os.path.splitext(filename)
        base = base + '-' + extra + ext
        return os.path.join(dirname, base)

def set_fontsize(fontsize, fig=None):
    if fig is not None:
        plt.figure(fig)
        ax = plt.gca()
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(fontsize)

def decision_error_tradeoff(gtMatrix, simMatrix):
    """FNIR (eq.3) vs. FPIR (eq.1) in http://biometrics.nist.gov/cs_links/face/frvt/frvt2013/NIST_8009.pdf"""

    n_matesearch = gtMatrix.shape[0]

    # FPIR: At a given threshold t, the false alarm rate (i.e., the false positive identification rate (FPIR), or the type I error rate) measures what fraction
    # of comparisons between probe templates and non-mate gallery templates result in a match score exceeding t.
    (Yneg, Yhat) = (1.0-gtMatrix.flatten(), simMatrix.flatten())  # Yneg = non-mate gallery templates (true negatives)
    fpir = np.cumsum(Yneg[np.argsort(Yhat)]) / np.sum(Yneg.flatten());
    return fpir

    #fpir = [np.mean(np.float32(Y[k_nonmate] == np.float32(Yhat[k_nonmate] > t))) for t in T]

    # FNIR: The miss rate (i.e., the false negative identification rate (FNIR), or the type II error rate) measures what fraction of probe
    # searches will fail to match a mated gallery template above a score of t.
    (k_nonmate, Y, Yhat) = (np.argwhere(gtMatrix.flatten() == 0), gtMatrix.flatten(), simMatrix.flatten())

    T = np.sort(np.unique(Yhat.flatten()))  # ascending
    #fnir = [np.mean(np.sum(Y
    fnir = np.cumsum(Y[np.argsort(Yhat)]) / n_probe

    return (fnir, fpir)


def fnmr_at_fmr(y, yhat, at):
    """false negative match rate (FNMR) at false match rate (FMR)"""
    (fmr, fnmr) = det11(y, yhat)
    f = interp1d(fmr, fnmr)
    return f(at)

def fmr_at_fnmr(y, yhat, at):
    """false negative match rate (FNMR) at false match rate (FMR)"""
    (fmr, fnmr) = det11(y, yhat)
    f = interp1d(fnmr, fmr)
    return f(at)


def det11(y, yhat):
    """ False negative match rate (FNMR)=1-TAR, vs false match rate (FMR) """
    (far, tar, thresholds) = sklearn.metrics.roc_curve(y, yhat, pos_label=1)
    (fmr, fnmr) = (far, 1-tar)
    return (fmr, fnmr)

def tpir_at_fpir(y, yhat, at, topk=20):
    """true positive identification rate at false positive identification rate"""
    (fpir, tpir) = det1N(y, yhat, False, topk)
    f = interp1d(fpir, tpir)
    return f(at)

def fnir_at_fpir(y, yhat, at, topk=20):
    """true positive identification rate at false positive identification rate"""
    (fpir, tpir) = det1N(y, yhat, False, topk)
    f = interp1d(fpir, (1-tpir))
    return f(at)

def det1N(y, yhat, returnThresholds=False, topk=20):
    """ False negative identification rate (FNIR)=1-TPIR, vs false positive identification rate (FPIR) """
    i_nonmated = np.argwhere(np.sum(y, axis=1) == 0)  # WARNING: this assumes that the matrices use the open set gallery with non-mates
    i_mated = np.argwhere(np.logical_or(np.sum(np.nan_to_num(y), axis=1) > 0, np.isnan(np.sum(y, axis=1))))  # mate in top-k or mate in gallery but not in top-k
    y = np.nan_to_num(y)  # nan to zero

    (y_nonmated, yhat_nonmated) = (np.zeros( (len(i_nonmated), topk) ), np.zeros( (len(i_nonmated), topk) ))
    for (k,i) in enumerate(i_nonmated):
        j = np.argsort(-yhat[i,:]).flatten()  # yhat is similarity -> -yhat is distance -> sort in ascending distance order
        y_nonmated[k,:] = y[i,j[0:topk]]  # top-k only
        yhat_nonmated[k,:] = yhat[i,j[0:topk]]  # top-k only

    (y_mated, yhat_mated) = (np.zeros( (len(i_mated), topk) ), np.zeros( (len(i_mated), topk) ))
    for (k,i) in enumerate(i_mated):
        j = np.argsort(-yhat[i,:]).flatten()  # yhat is similarity -> -yhat is distance -> sort in ascending distance order
        y_mated[k,:] = y[i,j[0:topk]]  # top-k only
        yhat_mated[k,:] = yhat[i,j[0:topk]]  # top-k only

    yhatmax_nonmated = np.max(yhat_nonmated, axis=1).flatten()  # maximum nonmated similarity
    yhatmax_mated = np.zeros(y_mated.shape[0])

    for i in range(y_mated.shape[0]):
        k = np.argwhere(y_mated[i,:].flatten() > 0).flatten()
        if len(k) > 0:  # mate in top-k?
            yhatmax_mated[i] = yhat_mated[i, k]  # yes, mated similarity within top-k
        else:
            yhatmax_mated[i] = -np.inf  # no match in top-k

    thresholds = sorted(list(set(np.array(yhatmax_mated.flatten().tolist() + yhatmax_nonmated.flatten().tolist()).tolist())))  # smallest to largest similarity
    thresholds = [t for t in thresholds if np.isfinite(t)]

    tpir = np.zeros(len(thresholds))
    fpir = np.zeros(len(thresholds))
    fnir = np.zeros(len(thresholds))
    for (k,t) in enumerate(thresholds):
        #tpir[k] = np.mean(yhatmax_mated >= t) # mated similarity at or above threshold, tpir=1-fnir
        fnir[k] = np.mean(yhatmax_mated < t) # mated similarity not in top-k (-inf) or below threshold, tpir=1-fnir
        fpir[k] = np.mean(yhatmax_nonmated >= t)   # non-mated similarity at or above threshold

    #return (fpir.flatten(), tpir.flatten())
    if not returnThresholds:
        return (fpir.flatten(), (1-fnir).flatten())
    else: 
        return (fpir.flatten(), (1-fnir).flatten(), thresholds)



def plot_det1N(fpir=None, tpir=None, y=None, yhat=None, label=None, title=None, outfile=None, figure=None, hold=False, logx=True, style=None, fontsize=None, xlabel='False Match Rate (FMR)', ylabel='False Negative Match Rate (FNMR)', legendSwap=False, errorbars=None, color=None):
    return plot_det11(fnmr=(1-tpir), fmr=fpir, label=label, title=title, outfile=outfile, figure=figure, hold=hold, logx=logx, style=style, fontsize=fontsize, xlabel='False Positive Identification Rate (FPIR)', ylabel='False Negative Identification Rate (FNIR)', legendSwap=legendSwap, errorbars=errorbars, color=color)

def plot_det11(fnmr=None, fmr=None, y=None, yhat=None, label=None, title=None, outfile=None, figure=None, hold=False, logx=True, style=None, fontsize=None, xlabel='False Match Rate (FMR)', ylabel='False Negative Match Rate (FNMR)', legendSwap=False, errorbars=None, color=None):
    """ Plot DET 1:1 curves """
    if (fnmr is None) and (fmr is None):
        if y is not None and yhat is not None:
            (fmr, fnmr) = det11(y, yhat)
        else:
            raise ValueError()

    if figure is not None:
        plt.figure(figure)
        plt.hold(True)
    else:
        plt.figure()

    if hold == True:
        plt.hold(True)
    else:
        plt.clf()

    if style is None:
        # Use plot defaults to increment plot style when holding
        p = plt.plot(fmr, fnmr, label=label, color=color)
    else:
        p = plt.plot(fmr, fnmr, style, label=label, color=color)

    if errorbars is not None:
        (x,y,yerr) = zip(*errorbars)  # [(x,y,yerr), (x,y,yerr), ...]
        plt.gca().errorbar(x, y, yerr=yerr, fmt='none', ecolor=plt.getp(p[0], 'color'))  # HACK: force error bars to have same color as plot

    if logx == False:
        plt.plot([0, 1], [0, 1], 'k--', label="_nolegend_")
    if logx is True:
        plt.xscale('log')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    legendLoc = "upper right" if legendSwap else "lower left"
    if fontsize is None:
        plt.legend(loc=legendLoc)
    else:
        plt.legend(loc=legendLoc, prop={'size':fontsize})
    plt.grid(True)
    plt.gca().set_aspect('equal')
    plt.autoscale(tight=True)

    if title is not None:
        plt.title(title)

    # Font size
    ax = plt.gca()
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(fontsize)
    #plt.tight_layout()  # throws exception on macos
    plt.gcf().set_tight_layout(True)


    if outfile is not None:
        quietprint('[janus.metric.plot_det11]: saving "%s"' % outfile)
        plt.savefig(outfile)
    else:
        plt.show()


def ijba11(Y, Yh, verbose=True, prependToLegend='Split', fontsize=12, detPlotStyle=None, hold=False, detLegendSwap=False, cmcLegendSwap=True, figure=2, splitmean=False, verboseLegend=True, outfile=None):
    """IJB-A 1:1 evaluation for a list of splits containing pairwise similarity (Yh), and ground truth (Y)"""
    """ False negative match rate (FNMR) is 1-TAR, and FMR is equivalent to FAR """
    """ equations are defined in NIST report 14SEP15 """

    # Figure setup
    if hold is False:
        strpy.bobo.metrics.clearfig(figure)

    # Input normalization
    if islist(Y) == False and islist(Yh) == False:
        (Y, Yh) = ([Y], [Yh])  # Handle singleton splits

    # Evaluation over splits
    n_splits = len(Y)
    (fnmr_at_fmr_1Em3, fnmr_at_fmr_1Em2, far_at_tar_85, far_at_tar_95, fnmr_at_fmr_1Em1, fmr_fnmr) = ([], [], [], [], [], [])
    (fnmr_at_fmr_1Em6, fnmr_at_fmr_1Em5, fnmr_at_fmr_1Em4) = ([], [], [])
    for k in range(0, n_splits):
        # Verification: 1 to 1
        y = np.array(Y[k]).astype(np.float32).flatten()
        yhat = np.array(Yh[k]).astype(np.float32).flatten()
        fnmr_at_fmr_1Em6.append(fnmr_at_fmr(y, yhat, at=1E-6))
        fnmr_at_fmr_1Em5.append(fnmr_at_fmr(y, yhat, at=1E-5))
        fnmr_at_fmr_1Em4.append(fnmr_at_fmr(y, yhat, at=1E-4))
        fnmr_at_fmr_1Em3.append(fnmr_at_fmr(y, yhat, at=1E-3))
        fnmr_at_fmr_1Em2.append(fnmr_at_fmr(y, yhat, at=1E-2))
        fnmr_at_fmr_1Em1.append(fnmr_at_fmr(y, yhat, at=1E-1))
        far_at_tar_85.append(fmr_at_fnmr(y, yhat, at=(1-0.85)))
        far_at_tar_95.append(fmr_at_fnmr(y, yhat, at=(1-0.95)))
        if n_splits > 1:
            if verboseLegend:
                roc_label = '%s-%d [FNMR@FMR(1E-2)=%1.2f]' % (prependToLegend, int(k+1), fnmr_at_fmr_1Em2[k])
            else:
                roc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                roc_label = '%s [FNMR@FMR(1E-2)=%1.2f]' % (prependToLegend, fnmr_at_fmr_1Em2[k])
            else:
                roc_label = '%s' % (prependToLegend)

        # Plot each split?
        if not splitmean:
            plot_det11(y=y, yhat=yhat, figure=figure, label=roc_label, style=detPlotStyle, logx=True, fontsize=fontsize, legendSwap=detLegendSwap, hold=True)
        fmr_fnmr.append(det11(y, yhat))

    # Results summary
    results = {'FNMR@FMR(1E-6)':{'mean':np.mean(fnmr_at_fmr_1Em6), 'std':np.std(fnmr_at_fmr_1Em6)},
               'FNMR@FMR(1E-5)':{'mean':np.mean(fnmr_at_fmr_1Em5), 'std':np.std(fnmr_at_fmr_1Em5)},
               'FNMR@FMR(1E-4)':{'mean':np.mean(fnmr_at_fmr_1Em4), 'std':np.std(fnmr_at_fmr_1Em4)},
               'FNMR@FMR(1E-3)':{'mean':np.mean(fnmr_at_fmr_1Em3), 'std':np.std(fnmr_at_fmr_1Em3)},
               'FNMR@FMR(1E-2)':{'mean':np.mean(fnmr_at_fmr_1Em2), 'std':np.std(fnmr_at_fmr_1Em2)},
               'FNMR@FMR(1E-1)':{'mean':np.mean(fnmr_at_fmr_1Em1), 'std':np.std(fnmr_at_fmr_1Em1)},
               'FAR@TAR(0.85)':{'mean':np.mean(far_at_tar_85), 'std':np.std(far_at_tar_85)},
               'FAR@TAR(0.95)':{'mean':np.mean(far_at_tar_95), 'std':np.std(far_at_tar_95)},
               'Y':Y, 'Yhat':Yh, 'fmr_fnmr':fmr_fnmr} # data to reproduce

    # Plot mean over splits?
    if splitmean:
        (minfmr, maxfmr, lenfmr) = (np.min([np.min(x[0]) for x in results['fmr_fnmr']]), np.max([np.max(x[0]) for x in results['fmr_fnmr']]), np.max([len(x[0]) for x in results['fmr_fnmr']]))
        fmr = np.arange(minfmr, maxfmr, (float(maxfmr)-float(minfmr))/float(lenfmr))  # mean interpolation
        fnmr = []
        for (x,y) in results['fmr_fnmr']:
            f = interp1d(x, y)
            fnmr.append([f(at) for at in fmr])
        fnmr = np.mean(fnmr, axis=0)
        if verboseLegend:
            det_label = '%s [FNMR@FMR(1E-2)=%1.2f]' % (prependToLegend, results['FNMR@FMR(1E-2)']['mean'])
        else:
            det_label = '%s' % (prependToLegend)
        errorbars = [(1E-3, results['FNMR@FMR(1E-3)']['mean'], results['FNMR@FMR(1E-3)']['std']), (1E-2, results['FNMR@FMR(1E-2)']['mean'], results['FNMR@FMR(1E-2)']['std']), (1E-1, results['FNMR@FMR(1E-1)']['mean'], results['FNMR@FMR(1E-1)']['std'])]
        plot_det11(fmr=fmr, fnmr=fnmr, figure=figure, label=det_label, style=detPlotStyle, logx=True, fontsize=fontsize, legendSwap=detLegendSwap, hold=True, errorbars=errorbars)
        (results['meanfmr'],  results['meanfnmr'],  results['maxfnmr'])  = (fmr, fnmr, np.nanmax(fnmr))

    # Print!
    results['DET'] = strpy.bobo.metrics.savefig(get_outfile(outfile, extra='DET'), figure=figure)
    if verbose == True:
        if n_splits > 1:
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-6) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-6)']['mean'], results['FNMR@FMR(1E-6)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-5) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-5)']['mean'], results['FNMR@FMR(1E-5)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-4) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-4)']['mean'], results['FNMR@FMR(1E-4)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-3) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-3)']['mean'], results['FNMR@FMR(1E-3)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-2) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-2)']['mean'], results['FNMR@FMR(1E-2)']['std'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-1) mean=%1.6f, std=%1.6f' % (results['FNMR@FMR(1E-1)']['mean'], results['FNMR@FMR(1E-1)']['std'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.85) mean=%1.6f, std=%1.6f' % (results['FAR@TAR(0.85)']['mean'], results['FAR@TAR(0.85)']['std'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.95) mean=%1.6f, std=%1.6f' % (results['FAR@TAR(0.95)']['mean'], results['FAR@TAR(0.95)']['std'])
        else:
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-6)=%1.6f' % (results['FNMR@FMR(1E-6)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-5)=%1.6f' % (results['FNMR@FMR(1E-5)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-4)=%1.6f' % (results['FNMR@FMR(1E-4)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-3)=%1.6f' % (results['FNMR@FMR(1E-3)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-2)=%1.6f' % (results['FNMR@FMR(1E-2)']['mean'])
            print '[janus.metrics.ijba11]: FNMR@FMR(1E-1)=%1.6f' % (results['FNMR@FMR(1E-1)']['mean'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.85)=%1.6f' % (results['FAR@TAR(0.85)']['mean'])
            print '[janus.metrics.ijba11]: FAR@TAR(0.95)=%1.6f' % (results['FAR@TAR(0.95)']['mean'])

        print '[janus.metrics.ijba11]: DET curve saved to "%s"' % results['DET']

    return results



def ijba1N(Y, Yh, verbose=True, title=None, prependToLegend='Split', fontsize=12, detPlotStyle=None, hold=False, detLegendSwap=False, cmcPlotStyle=None, cmcLegendSwap=None, cmcFigure=3, detFigure=4, splitmean=False, cmcLogy=False, L=20, verboseLegend=True, verboseLegendRank=10, cmcMinY=0.0, color=None, topk=20, outfile=None):
    """IJB-A 1:N evaluation"""

    # Figure setup
    if hold is False:
        strpy.bobo.metrics.clearfig(cmcFigure)
        strpy.bobo.metrics.clearfig(detFigure)

    # Input normalization
    if islist(Y) == False and islist(Yh) == False:
        (Y, Yh) = ([Y], [Yh])  # Handle singleton splits

    # Evaluation over splits
    n_splits = len(Y)
    (tpir_at_rank_1, tpir_at_rank_10, tpir_at_rank_20, tpir_at_fpir_1Em3, tpir_at_fpir_1Em2, fnir_at_fpir_3Em2, tpir_at_fpir_1Em1, recall_at_rank_all, fnir_at_fpir_all) = ([], [], [], [], [], [], [], [], [])
    tpir_at_rank_5 = []
    tpir_at_rank_dict = {1:tpir_at_rank_1, 5:tpir_at_rank_5, 10:tpir_at_rank_10, 20:tpir_at_rank_20}
    desired_legend_rank_val = tpir_at_rank_dict[verboseLegendRank] if verboseLegendRank in tpir_at_rank_dict else tpir_at_rank_10
    desired_legend_rank = verboseLegendRank if verboseLegendRank in tpir_at_rank_dict else 10
    for k in range(0, n_splits):
        # Cumulative match characteristic
        gtMatrix = Y[k].astype(np.float32)
        simMatrix = Yh[k].astype(np.float32)
        (rank, recall) = strpy.bobo.metrics.cumulative_match_characteristic(simMatrix, gtMatrix)
        tpir_at_rank_1.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=1))
        tpir_at_rank_5.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=5))
        tpir_at_rank_10.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=10))
        tpir_at_rank_20.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=20))
        if n_splits > 1:
            if verboseLegend:
                cmc_label = '%s-%d [TPIR@Rank%s=%1.2f]' % (prependToLegend, int(k+1),desired_legend_rank, desired_legend_rank_val[k])
            else:
                cmc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                cmc_label = '%s [TPIR@Rank%s=%1.2f]' % (prependToLegend,desired_legend_rank, desired_legend_rank_val[k])
            else:
                cmc_label = '%s' % (prependToLegend)
        if not splitmean:
            strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=cmcFigure, style=cmcPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=True, logy=cmcLogy, miny=cmcMinY, color=color)

        # DET 1:N curve (top-L)
        (yh, y) = ([], [])
        for i in range(0, Yh[k].shape[0]):
            j = np.argsort(-Yh[k][i,:])  # yhat is similarity -> -yhat is distance -> sort in ascending distance order
            yh.append( [Yh[k][i,jj] for jj in j[0:L]] )
            y.append( [Y[k][i,jj] for jj in j[0:L]] )
        (fpir, tpir) = det1N(np.array(y), np.array(yh), returnThresholds=False, topk=topk)
#        (fpir, tpir) = det1N(Y[k], Yh[k])  # WARNING: this was used to generate results for 18DEC15 datacall, makes no difference

        fnir = 1-tpir

        tpir_at_fpir_1Em1.append(tpir_at_fpir(Y[k], Yh[k], at=1E-1, topk=topk))
        tpir_at_fpir_1Em2.append(tpir_at_fpir(Y[k], Yh[k], at=1E-2, topk=topk))
        tpir_at_fpir_1Em3.append(tpir_at_fpir(Y[k], Yh[k], at=1E-3, topk=topk))
        fnir_at_fpir_3Em2.append(fnir_at_fpir(Y[k], Yh[k], at=3E-2, topk=topk))

        if n_splits > 1:
            if verboseLegend:
                det_label = '%s-%d [FNIR@FPIR(1E-2)=%1.2f]' % (prependToLegend, int(k+1), 1-tpir_at_fpir_1Em2[k])
            else:
                det_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                det_label = '%s [FNIR@FPIR(1E-2)=%1.2f]' % (prependToLegend, 1-tpir_at_fpir_1Em2[k])
            else:
                det_label = '%s' % (prependToLegend)

        if not splitmean:
            plot_det1N(fpir=fpir, tpir=tpir, title=title, label=det_label, style=detPlotStyle, fontsize=fontsize, legendSwap=detLegendSwap, hold=True, figure=detFigure, color=color)
        recall_at_rank_all.append( (rank, recall) )
        fnir_at_fpir_all.append( (fpir, fnir) )

    # Results summary
    results = {'TPIR@Rank1':{'mean':np.mean(tpir_at_rank_1), 'std':np.std(tpir_at_rank_1)},
               'TPIR@Rank5':{'mean':np.mean(tpir_at_rank_5), 'std':np.std(tpir_at_rank_5)},
               'TPIR@Rank10':{'mean':np.mean(tpir_at_rank_10), 'std':np.std(tpir_at_rank_10)},
               'TPIR@Rank20':{'mean':np.mean(tpir_at_rank_20), 'std':np.std(tpir_at_rank_20)},
               'FNIR@FPIR(3E-2)':{'mean':np.mean(fnir_at_fpir_3Em2), 'std':np.std(fnir_at_fpir_3Em2)},
               'TPIR@FPIR(1E-3)':{'mean':np.mean(tpir_at_fpir_1Em3), 'std':np.std(tpir_at_fpir_1Em3)},
               'TPIR@FPIR(1E-2)':{'mean':np.mean(tpir_at_fpir_1Em2), 'std':np.std(tpir_at_fpir_1Em2)},
               'TPIR@FPIR(1E-1)':{'mean':np.mean(tpir_at_fpir_1Em1), 'std':np.std(tpir_at_fpir_1Em1)},
               'recall_at_rank':recall_at_rank_all, 'fnir_at_fpir':fnir_at_fpir_all}

    # Interpolated mean curves?
    if splitmean:
        # Mean CMC curve interpolated over splits
        (minrank, maxrank, lenrank) = (np.min([np.min(x[0]) for x in results['recall_at_rank']]), np.min([np.max(x[0]) for x in results['recall_at_rank']]), np.max([len(x[0]) for x in results['recall_at_rank']]))
        rank = np.arange(minrank, maxrank, (float(maxrank)-float(minrank))/(float(lenrank)))  # mean interpolation
        recall = []

        for (x,y) in results['recall_at_rank']:
            f = interp1d(x, y)
            recall.append([f(at) for at in rank])
        recall = np.mean(recall, axis=0)
        (results['meanrank'],  results['meanrecall'])  = (rank, recall)
        if verboseLegend:
            cmc_label = '%s [TPIR@Rank%s=%1.2f]' % (prependToLegend, desired_legend_rank, results['TPIR@Rank%s' % desired_legend_rank]['mean'])
        else:
            cmc_label = '%s' % (prependToLegend)
        errorbars = [(1, results['TPIR@Rank1']['mean'], results['TPIR@Rank1']['std']),
                     (5, results['TPIR@Rank5']['mean'], results['TPIR@Rank5']['std']),
                     (10, results['TPIR@Rank10']['mean'], results['TPIR@Rank10']['std'])]
        strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=cmcFigure, style=cmcPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=True, errorbars=errorbars, logy=cmcLogy, miny=cmcMinY, color=color)

        # Mean DET curve interpolated over splits
        # changing plot limits such that interpolation doesn't fall outside the range for some splits; One caveat will be that some splits will get clipped
        (minfpir, maxfpir, lenfpir) = (np.max([np.min(x[0]) for x in results['fnir_at_fpir']]), np.min([np.max(x[0]) for x in results['fnir_at_fpir']]), np.max([len(x[0]) for x in results['fnir_at_fpir']]))
        fpir = np.arange(minfpir, maxfpir, (float(maxfpir)-float(minfpir))/(float(lenfpir)))  # mean interpolation
        fnir = []
        for (x,y) in results['fnir_at_fpir']:
            f = interp1d(x, y)
            fnir.append([f(at) for at in fpir])
        fnir_mean = np.mean(fnir, axis=0)
        fnir_std = np.std(fnir, axis=0)
        f = interp1d(fpir, fnir_mean)
        g = interp1d(fpir, fnir_std)
        (results['meanfpir'],  results['meanfnir'])  = (fpir, fnir_mean)
        if verboseLegend:
            det_label = '%s [FNIR@FPIR(1E-2)=%1.2f]' % (prependToLegend, f(1E-2))
        else:
            det_label = '%s' % (prependToLegend)
        errorbars = [((1E-3), f(1E-3), g(1E-3)), ((1E-2), f(1E-2), g(1e-2)), (1E-1, f(1E-1), g(1E-1))]
        plot_det1N(fpir=fpir, tpir=(1.0-fnir_mean), label=det_label, style=detPlotStyle, fontsize=fontsize, legendSwap=detLegendSwap, hold=True, figure=detFigure, errorbars=errorbars, color=color)


    # Print!
    results['CMC'] = strpy.bobo.metrics.savefig(get_outfile(outfile, extra='CMC'), figure=cmcFigure)
    results['DET'] = strpy.bobo.metrics.savefig(get_outfile(outfile, extra='DET'), figure=detFigure)

    if verbose == True:
        print '[janus.metrics.ijba1N]: TPIR@Rank1 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank1']['mean'], results['TPIR@Rank1']['std'])
        print '[janus.metrics.ijba1N]: TPIR@Rank5 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank5']['mean'], results['TPIR@Rank5']['std'])
        print '[janus.metrics.ijba1N]: TPIR@Rank10 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank10']['mean'], results['TPIR@Rank10']['std'])
        print '[janus.metrics.ijba1N]: TPIR@Rank20 mean=%1.3f, std=%1.3f' % (results['TPIR@Rank20']['mean'], results['TPIR@Rank20']['std'])
        print '[janus.metrics.ijba1N]: TPIR@FPIR(1E-1) mean=%1.3f, std=%1.3f' % (results['TPIR@FPIR(1E-1)']['mean'], results['TPIR@FPIR(1E-1)']['std'])
        print '[janus.metrics.ijba1N]: FNIR@FPIR(3E-2) mean=%1.3f, std=%1.3f' % (results['FNIR@FPIR(3E-2)']['mean'], results['FNIR@FPIR(3E-2)']['std'])
        print '[janus.metrics.ijba1N]: TPIR@FPIR(1E-2) mean=%1.3f, std=%1.3f' % (results['TPIR@FPIR(1E-2)']['mean'], results['TPIR@FPIR(1E-2)']['std'])
        print '[janus.metrics.ijba1N]: CMC curve saved to "%s"' % results['CMC']
        print '[janus.metrics.ijba1N]: DET curve saved to "%s"' % results['DET']

    return results


def ijba(Y11, Yh11, Y1N, Yh1N, verbose=True, prependToLegend='Split', fontsize=12, rocPlotStyle=None, cmcPlotStyle=None, hold=False, rocLegendSwap=False, cmcLegendSwap=False, outfile=None):
    """Y/YHat is list of numpy arrays over splits of size NumProbe x NumGallery, or a vector which can be reshaped using N_gallery"""

    # Cleanup
    if hold is False:
        strpy.bobo.metrics.clearfig(1)
        strpy.bobo.metrics.clearfig(2)

    # Input normalization
    if islist(Y11) == False and islist(Yh11) == False:
        (Y11, Yh11, Y1N, Yh1N) = ([Y11], [Yh11], [Y1N], [Yh1N])  # Handle singleton splits

    # Evaluation over splits
    n_splits = len(Y11)
    (tar_at_far1Em3, tar_at_far1Em2, tar_at_far1Em1, tdr_at_rank1, tdr_at_rank5, tdr_at_rank10) = ([], [], [], [], [], [])
    for k in range(0, n_splits):
        # Verification: 1 to 1
        y = np.array(Y11[k]).astype(np.float32).flatten()
        yhat = np.array(Yh11[k]).astype(np.float32).flatten()
        tar_at_far1Em3.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-3))
        tar_at_far1Em2.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-2))
        tar_at_far1Em1.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-1))
        if n_splits > 1:
            roc_label = '%s-%d [TAR@FAR(1E-3)=%1.2f]' % (prependToLegend, int(k+1), tar_at_far1Em3[k])
        else:
            roc_label = '%s [TAR@FAR(1E-3)=%1.2f]' % (prependToLegend, tar_at_far1Em3[k])
        strpy.bobo.metrics.plot_roc(y, yhat, figure=2, label=roc_label, style=cmcPlotStyle, logx=True, fontsize=fontsize, legendSwap=rocLegendSwap, hold=True)

        # Identification
        gtMatrix = Y1N[k].astype(np.float32)
        simMatrix = Yh1N[k].astype(np.float32)
        (rank, recall) = strpy.bobo.metrics.cumulative_match_characteristic(simMatrix, gtMatrix)
        tdr_at_rank1.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=1))
        tdr_at_rank5.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=5))
        tdr_at_rank10.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=10))
        if n_splits > 1:
            cmc_label = '%s-%d [Recall@Rank5=%1.2f]' % (prependToLegend, int(k+1), tdr_at_rank5[k])
        else:
            cmc_label = '%s [Recall@Rank5=%1.2f]' % (prependToLegend, tdr_at_rank5[k])
        strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=1, style=rocPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=True)

        # DET


    # Results summary
    results = {'TAR@FAR(1E-3)':{'mean':np.mean(tar_at_far1Em3), 'std':np.std(tar_at_far1Em3)},
               'TAR@FAR(1E-2)':{'mean':np.mean(tar_at_far1Em2), 'std':np.std(tar_at_far1Em2)},
               'TAR@FAR(1E-1)':{'mean':np.mean(tar_at_far1Em1), 'std':np.std(tar_at_far1Em1)},
               'Recall@Rank1':{'mean':np.mean(tdr_at_rank1), 'std':np.std(tdr_at_rank1)},
               'Recall@Rank5':{'mean':np.mean(tdr_at_rank5), 'std':np.std(tdr_at_rank5)},
               'Recall@Rank10':{'mean':np.mean(tdr_at_rank10), 'std':np.std(tdr_at_rank10)},
               'ROC':strpy.bobo.metrics.savefig(get_outfile(outfile, extra='ROC'), figure=2),
               'CMC':strpy.bobo.metrics.savefig(get_outfile(outfile, extra='CMC'), figure=1)}

    # Print!
    if verbose == True:
        print '[janus.metrics.ijba]: TAR@FAR(1E-3) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-3)']['mean'], results['TAR@FAR(1E-3)']['std'])
        print '[janus.metrics.ijba]: TAR@FAR(1E-2) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-2)']['mean'], results['TAR@FAR(1E-2)']['std'])
        print '[janus.metrics.ijba]: TAR@FAR(1E-1) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-1)']['mean'], results['TAR@FAR(1E-1)']['std'])
        print '[janus.metrics.ijba]: Recall@Rank(1) mean=%1.3f, std=%1.3f' % (results['Recall@Rank1']['mean'], results['Recall@Rank1']['std'])
        print '[janus.metrics.ijba]: Recall@Rank(5) mean=%1.3f, std=%1.3f' % (results['Recall@Rank5']['mean'], results['Recall@Rank5']['std'])
        print '[janus.metrics.ijba]: Recall@Rank(10) mean=%1.3f, std=%1.3f' % (results['Recall@Rank10']['mean'], results['Recall@Rank10']['std'])
        print '[janus.metrics.ijba]: ROC curve saved to "%s"' % results['ROC']
        print '[janus.metrics.ijba]: CMC curve saved to "%s"' % results['CMC']

    # Done!
    return results





def report(Y, Yhat, N_gallery=None, verbose=True, prependToLegend='Split', atrank=[1,5,10], fontsize=12, rocPlotStyle=None, cmcPlotStyle=None, hold=False, rocLegendSwap=False, cmcLegendSwap=False, cmcLogy=False, verboseLegend=True, cmcMinY=0.0, display=True, outfile=None):
    """Y/YHat is list of numpy arrays over splits of size NumProbe x NumGallery, or a vector which can be reshaped using N_gallery"""

    # Cleanup
    if hold is False and display is True:
        strpy.bobo.metrics.clearfig(1)
        strpy.bobo.metrics.clearfig(2)

    # Input normalization
    if islist(Y) == False and islist(Yhat) == False:
        (Y, Yhat) = ([Y], [Yhat])  # Handle singleton splits for Y and Yhat

    # Evaluation over splits
    n_splits = len(Y)
    eer = []; fpr_at_tpr85 = []; fpr_at_tpr75 = []; tdr_at_rank1=[];  tdr_at_rank5=[]; tdr_at_rank10=[]; fpr_at_tpr75 = [];
    (tar_at_far1Em3, tar_at_far1Em2, tar_at_far1Em1) = ([], [], [])
    for k in range(0, n_splits):
        y = np.array(Y[k]).astype(np.float32).flatten()
        yhat = np.array(Yhat[k]).astype(np.float32).flatten()
        n_gallery = N_gallery[k] if N_gallery is not None else Y[k].shape[1]

        # Verification
        eer.append(np.floor(100*strpy.bobo.metrics.roc_eer(y, yhat)) / (100.0))
        fpr_at_tpr75.append(strpy.bobo.metrics.fpr_at_tpr(y, yhat, at=0.75))
        fpr_at_tpr85.append(strpy.bobo.metrics.fpr_at_tpr(y, yhat, at=0.85))
        tar_at_far1Em3.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-3))
        tar_at_far1Em2.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-2))
        tar_at_far1Em1.append(strpy.bobo.metrics.tpr_at_fpr(y, yhat, at=1E-1))

        # Identification
        gtMatrix = y.reshape( (len(y)/n_gallery, n_gallery) )
        simMatrix = yhat.reshape( (len(yhat)/n_gallery, n_gallery) )
        (rank, recall) = strpy.bobo.metrics.cumulative_match_characteristic(simMatrix, gtMatrix)
        tdr_at_rank1.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=atrank[0]))
        tdr_at_rank5.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=atrank[1]))
        tdr_at_rank10.append(strpy.bobo.metrics.tdr_at_rank(rank, recall, at=atrank[2]))

        # Plots
        if n_splits > 1:
            if verboseLegend:
                cmc_label = '%s-%d [TDR@Rank%d=%1.3f]' % (prependToLegend, int(k+1), atrank[2], tdr_at_rank10[k])
            else:
                cmc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                cmc_label = '%s [TDR@Rank%d=%1.3f]' % (prependToLegend, atrank[2], tdr_at_rank10[k])
            else:
                cmc_label = '%s' % (prependToLegend)
        if display:
            strpy.bobo.metrics.plot_cmc(rank, recall, label=cmc_label, figure=1, style=rocPlotStyle, fontsize=fontsize, legendSwap=cmcLegendSwap, hold=hold, logy=cmcLogy, miny=cmcMinY)

        # ROC plots
        if n_splits > 1:
            if verboseLegend:
                roc_label = '%s-%d [FPR@TDR(0.85)=%1.3f]' % (prependToLegend, int(k+1), fpr_at_tpr85[k])
            else:
                roc_label = '%s-%d' % (prependToLegend, int(k+1))
        else:
            if verboseLegend:
                roc_label = '%s [FPR@TDR(0.85)=%1.3f]' % (prependToLegend, fpr_at_tpr85[k])
            else:
                roc_label = '%s' % (prependToLegend)
        if display:
            strpy.bobo.metrics.plot_roc(y, yhat, figure=2, label=roc_label, style=cmcPlotStyle, logx=True, fontsize=fontsize, legendSwap=rocLegendSwap, hold=hold)

    # Results summary
    results = {'EER':{'mean':np.mean(eer), 'std':np.std(eer)},
               'FPR@TDR=0.75':{'mean':np.mean(fpr_at_tpr75), 'std':np.std(fpr_at_tpr75)},
               'FPR@TDR=0.85':{'mean':np.mean(fpr_at_tpr85), 'std':np.std(fpr_at_tpr85)},
               'TAR@FAR(1E-3)':{'mean':np.mean(tar_at_far1Em3), 'std':np.std(tar_at_far1Em3)},
               'TAR@FAR(1E-2)':{'mean':np.mean(tar_at_far1Em2), 'std':np.std(tar_at_far1Em2)},
               'TAR@FAR(1E-1)':{'mean':np.mean(tar_at_far1Em1), 'std':np.std(tar_at_far1Em1)},
               'ROC':strpy.bobo.metrics.savefig(get_outfile(outfile, extra='ROC'), figure=2) if display else None,
               'CMC':strpy.bobo.metrics.savefig(get_outfile(outfile, extra='CMC'), figure=1) if display else None,
               'TDR@Rank=%d' % atrank[0]:{'mean':np.mean(tdr_at_rank1), 'std':np.std(tdr_at_rank1)},
               'TDR@Rank=%d' % atrank[1]:{'mean':np.mean(tdr_at_rank5), 'std':np.std(tdr_at_rank5)},
               'TDR@Rank=%d' % atrank[2]:{'mean':np.mean(tdr_at_rank10), 'std':np.std(tdr_at_rank10)},
               'pickled':strpy.bobo.util.save( (Y,Yhat,N_gallery) )}

    # Print!
    if verbose == True:
        print '[janus.metrics.report]: EER mean=%1.3f, std=%1.3f' % (results['EER']['mean'], results['EER']['std'])
        print '[janus.metrics.report]: FPR@TDR=0.75 mean=%1.5f, std=%1.5f' % (results['FPR@TDR=0.75']['mean'], results['FPR@TDR=0.75']['std'])
        print '[janus.metrics.report]: FPR@TDR=0.85 mean=%1.5f, std=%1.5f' % (results['FPR@TDR=0.85']['mean'], results['FPR@TDR=0.85']['std'])
        print '[janus.metrics.report]: TAR@FAR(1E-3) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-3)']['mean'], results['TAR@FAR(1E-3)']['std'])
        print '[janus.metrics.report]: TAR@FAR(1E-2) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-2)']['mean'], results['TAR@FAR(1E-2)']['std'])
        print '[janus.metrics.report]: TAR@FAR(1E-1) mean=%1.3f, std=%1.3f' % (results['TAR@FAR(1E-1)']['mean'], results['TAR@FAR(1E-1)']['std'])
        print '[janus.metrics.report]: TDR@Rank%d mean=%1.3f, std=%1.3f' % (atrank[0], results['TDR@Rank=%d' % atrank[0]]['mean'], results['TDR@Rank=%d' % atrank[0]]['std'])
        print '[janus.metrics.report]: TDR@Rank%d mean=%1.3f, std=%1.3f' % (atrank[1], results['TDR@Rank=%d' % atrank[1]]['mean'], results['TDR@Rank=%d' % atrank[1]]['std'])
        print '[janus.metrics.report]: TDR@Rank%d mean=%1.3f, std=%1.3f' % (atrank[2], results['TDR@Rank=%d' % atrank[2]]['mean'], results['TDR@Rank=%d' % atrank[2]]['std'])
        print '[janus.metrics.report]: ROC curve saved to "%s"' % results['ROC']
        print '[janus.metrics.report]: CMC curve saved to "%s"' % results['CMC']
        print '[janus.metrics.report]: data to reproduce saved to "%s"' % results['pickled']

    # Done!
    return results

def asgallery(y, n_gallery):
    """Convert nx1 vector y to (n/m)xm Gallery Matrix, assume that y is stored row major"""
    ya = np.array(y);
    return ya.reshape( (ya.size/n_gallery, n_gallery) )



def detection_from_imscene(imscenedet, imscenetruth, min_overlap=0.2):
    """Return assigned detections"""

    y = []; yhat = [];
    for (j, (imdet, imtruth)) in enumerate(zip(imscenedet, imscenetruth)):
        print '[janus.metrics.detection][%d/%d]: detector evaluation' % (j+1, len(imscenedet))

        # Detector for current scene
        det = [{'bbox':im.boundingbox(), 'label':im.category(), 'probability':im.probability()} for im in imdet.objects()]
        truth = [{'bbox':im.boundingbox(), 'label':im.category(), 'probability':im.probability()} for im in imtruth.objects()]
        det = sorted(det, key=lambda x: x['probability'], reverse=True)  # sort inplace, descending by score

        # Assign detections
        is_assigned = [False]*len(truth)
        for d in det:
            overlap = [d['bbox'].overlap(t['bbox']) for t in truth]  # overlap of current detection with truth bounding boxes
            is_overlapped_label = [(x >= min_overlap) and (d['label'] == t['label']) for (x,t) in zip(overlap, truth)]  # minimum overlap and same label?
            if any(is_overlapped_label):  # any assignments with minimum overlap and same label?
                max_overlap = [k for (k,v) in enumerate(overlap) if (np.abs(v - max(overlap)) < 1E-6 and is_overlapped_label[k])]  # truth bounding box with maximum overlap
                if len(max_overlap) > 0 and is_assigned[max_overlap[0]] == False:  # truth already assigned?
                    # True detection!
                    y.append(1.0)
                    yhat.append(d['probability']) # true detection probability
                    is_assigned[max_overlap[0]] = True
                else:
                    #y.append( (0.0, -np.inf) )  # non-maximum suppression
                    pass  # ignore multiple detections for same truth
            else:
                # False alarm
                y.append(0.0)
                yhat.append(d['probability'])

        # Missed detections
        for t in is_assigned:
            if t == False:
                y.append(1.0)
                yhat.append(0.0)

    # Return ground truth label and detection score
    return (y, yhat)

def detection_from_csvfile(detcsvfile, truthcsvfile, min_overlap=0.2, ignore=False, skipheader=True, errorFile=None, imageIndex=False, isVideo=False):
    return greedy_bounding_box_assignment(detcsvfile, truthcsvfile, min_overlap, ignore, skipheader, errorFile, imageIndex=imageIndex, isVideo=isVideo)

def get_index(name, index_list):
    try:
        return index_list[name]
    except KeyError:
        return -1

def greedy_bounding_box_assignment(detcsvfile, truthcsvfile, min_overlap=0.2, ignore=False, skipheader=True, errorFile=None, minscore=-1E6, downsample=1, threshold=0.0, imageIndex=False, isVideo=False):
    """Return {0,1} ground truth (Y) and similarity scores (Yh) for assigned detection suitable for computing ROC curve, using csv file inputs
       truth CSV files of the form (imagefile, xmin, ymin, width, height, ignore... )
       detector CSV files of the form (imagefile, xmin, ymin, width, height, confidence ... )
       This function performs greedy assignment of each detection to best ground truth with overlap greater than min_overlap.
       if returnAssignments=True, then return the row index of the ground truth assignment
    """

    match_frame_num = False
    # Unique image filenames
    TRUTH_FILENAME = 0
    TRUTH_FACE_X = 1
    TRUTH_FACE_Y = 2
    TRUTH_FACE_WIDTH = 3
    TRUTH_FACE_HEIGHT = 4
    TRUTH_IGNORE = 5
    TRUTH_FRAME_NUM = -1
    DET_FILENAME = 0
    DET_FACE_X = 1
    DET_FACE_Y = 2
    DET_FACE_WIDTH = 3
    DET_FACE_HEIGHT = 4
    DET_CONFIDENCE = 5
    DET_FRAME_NUM = -1
    if skipheader:
        # If the file has a header, get field offsets from that, rather than hard-coding them. get_index
        # just looks up the value in the map returned by readcsvwithheader, and returns -1 if it's not found.
        dets,det_header = readcsvwithheader(detcsvfile)
        truths,truth_header = readcsvwithheader(truthcsvfile)
        TRUTH_FILENAME = get_index('FILENAME', truth_header)
        TRUTH_FACE_X = get_index('FACE_X', truth_header)
        TRUTH_FACE_Y = get_index('FACE_Y', truth_header)
        TRUTH_FACE_WIDTH = get_index('FACE_WIDTH', truth_header)
        TRUTH_FACE_HEIGHT = get_index('FACE_HEIGHT', truth_header)
        TRUTH_IGNORE = get_index('IGNORE_FLAG', truth_header)
        TRUTH_FRAME_NUM = get_index('FRAME_NUM', truth_header)
        DET_FILENAME = get_index('FILENAME', det_header)
        DET_FACE_X = get_index('FACE_X', det_header)
        DET_FACE_Y = get_index('FACE_Y', det_header)
        DET_FACE_WIDTH = get_index('FACE_WIDTH', det_header)
        DET_FACE_HEIGHT = get_index('FACE_HEIGHT', det_header)
        DET_CONFIDENCE = get_index('CONFIDENCE', det_header)
        DET_FRAME_NUM = get_index('FRAME_NUM', det_header)
        print 'Truth FILENAME={}; det FILENAME={}; TRUTH_IGNORE={}'.format(TRUTH_FILENAME, DET_FILENAME, TRUTH_IGNORE)

        # If we don't have frame numbers both in the metadata and in the detections, don't use them at all.
        if TRUTH_FRAME_NUM < 0 or DET_FRAME_NUM < 0:
            imfile_set = set([x[DET_FILENAME] for x in dets[1:]])
            imfiles = list(imfile_set)
            truthfiles = set([x[TRUTH_FILENAME] for x in truths[1:]])
            missing_imfiles = []
            if len(imfiles) != len(truthfiles):
                print 'Truth data has {} files; detections {}'.format(len(truthfiles), len(imfile_set))
                if len(imfiles) < len(truthfiles):
                    for truthfile in truthfiles:
                        if truthfile not in imfile_set:
                            print 'No detection line for {}'.format(truthfile)
                            missing_imfiles.append(truthfile)
                            # print missing_imfiles
                    # print 'missing_imfiles: {}'.format(missing_imfiles)
                # assert len(imfiles) == len(set([x[0] for x in readcsv(truthcsvfile)[1:]]))
            # group csv rows by filename into dictionary keyed by filename        
            d_detcsv = {key:list(group) for (key, group) in bobo_groupby(dets[1:], lambda x: x[DET_FILENAME])}
            for imfile in missing_imfiles:
                d_detcsv[imfile] = []
            d_truthcsv = {key:list(group) for (key, group) in bobo_groupby(truths[1:], lambda x: x[TRUTH_FILENAME])}
        else:
            # We have frame numbers here. The "filename" is the actual file concatenated with the frame number.
            # We have to be a little more forgiving about missing files in this case--it's entirely likely that
            # a single frame will not have any detections, and the test harness wonn't write out a blank entry
            # in that case.
            imfile_set = set([x[DET_FILENAME] + '-' + x[DET_FRAME_NUM] for x in dets[1:]])
            imfiles = list(imfile_set)
            d_detcsv = {key:list(group) for (key, group) in bobo_groupby(dets[1:], lambda x: x[DET_FILENAME] + '-' + x[DET_FRAME_NUM])}
            # Handle downsampling on the truth data.
            truthfiles = set([x[TRUTH_FILENAME] + '-' + x[TRUTH_FRAME_NUM] for x in truths[1:] if downsample <= 1 or (int(x[TRUTH_FRAME_NUM] - 1) % downsample) == 0])
            d_truthcsv = {key:list(group) for (key, group) in bobo_groupby(truths[1:], lambda x: x[TRUTH_FILENAME] + '-' + x[TRUTH_FRAME_NUM])}
            print 'Truth entries={}/{}; det entries={}/{}'.format(len(d_truthcsv), len(truths) - 1, len(d_detcsv), len(dets) - 1)
    else:
        imfiles = list(set([x[0] for x in readcsv(detcsvfile)]))
        assert len(imfiles) == len(set([x[0] for x in readcsv(truthcsvfile)]))
        # group csv rows by filename into dictionary keyed by filename        
        d_detcsv = {key:list(group) for (key, group) in bobo_groupby(readcsv(detcsvfile), lambda x: x[DET_FILENAME])}  
        d_truthcsv = {key:list(group) for (key, group) in bobo_groupby(readcsv(truthcsvfile), lambda x: x[TRUTH_FILENAME])}  

    errorOut = None
    if not errorFile is None:
        errorOut = open(errorFile, 'w')
        # TYPE of 1 means it was a missed detection; 0 means false alarm
        errorOut.write('TYPE (0 is FA),FILENAME,FACE_X,FACE_Y,FACE_WIDTH,FACE_HEIGHT,CONFIDENCE\n')


    # Greedy assignment
    y = []; yhat = [];  imgindex=[]
    # If we have frame numbers they're handled in the keys here.
    for (j, f) in enumerate(imfiles):
        # All detections in current image
        try:
            truth_dets = d_truthcsv[f]
        except KeyError as ex:
            # Don't throw an exception in this case--not every frame will be mentioned either in the truth
            # or in the detections.
            if not isVideo:
                raise ex
            truth_dets = []

        if TRUTH_IGNORE >= 0:
            for x in truth_dets:
                try:
                    a = x[TRUTH_IGNORE]
                except:
                    print 'Bad truth line at {}: {}; len {}'.format(j, f, len(x))
        det = [{'filename':f,
                'bbox':BoundingBox(xmin=float(x[DET_FACE_X]), ymin=float(x[DET_FACE_Y]),
                                   width=float(x[DET_FACE_WIDTH]), height=float(x[DET_FACE_HEIGHT])),
                                  'label':'object', 'probability':float(x[DET_CONFIDENCE])} for x in d_detcsv[f] if len(x[DET_FACE_X])>0 and float(x[DET_CONFIDENCE]) > threshold]
        truth = [{'filename':f,
                  'bbox':BoundingBox(xmin=float(x[TRUTH_FACE_X]), ymin=float(x[TRUTH_FACE_Y]), width=float(x[TRUTH_FACE_WIDTH]), height=float(x[TRUTH_FACE_HEIGHT])),
                  'label':'object', 'probability':1.0,
                  'ignore':0.0 if TRUTH_IGNORE < 0 or len(x) <= TRUTH_IGNORE else float(x[TRUTH_IGNORE])} for x in truth_dets if len(x[TRUTH_FACE_WIDTH])>0]
        det = sorted(det, key=lambda x: x['probability'], reverse=True)  # sort detections inplace, descending by score

        # Greedy assignment of detections
        is_assigned = [False]*len(truth)
        for d in det:
            overlap = 0.0
            is_overlapped_label = False
            try:
                overlap = [d['bbox'].overlap(t['bbox']) for t in truth]  # overlap of current detection with all ground truth bounding boxes
                is_overlapped_label = [(x >= min_overlap) and (d['label'] == t['label']) for (x,t) in zip(overlap, truth)]  # minimum overlap and same label?
                #print '{}: overlap {}'.format(d, any(is_overlapped_label))
                #for (x,t) in zip(overlap,truth):
                #    print '    ', t, x
            except ZeroDivisionError as e:
                print 'Divide by zero in detection @{}, {} ({} x {}) in {}'.format(d['bbox'].xmin, d['bbox'].ymin, d['bbox'].width(), d['bbox'].height(), f)
                overlap = 0.0
                is_overlapped_label = []
            if any(is_overlapped_label):  # any assignments with minimum overlap and same label?
                max_overlap = [k for (k,v) in enumerate(overlap) if (np.abs(v - max(overlap)) < 1E-6 and is_overlapped_label[k])]  # truth bounding box with maximum overlap
                if len(max_overlap) > 0 and is_assigned[max_overlap[0]] == False:  # truth not already assigned?
                    # True detection!
                    y.append(1.0)
                    imgindex.append(d['filename'])
                    yhat.append(d['probability']) # true detection probability
                    is_assigned[max_overlap[0]] = True  # mark this ground truth assigned
                else:
                    # False alarm - No unassigned ground truth (Non-maximum suppression error)
                    y.append(0.0)
                    imgindex.append(d['filename'])
                    yhat.append(d['probability'])
            else:
                # False alarm - No overlapping ground truth
                y.append(0.0)
                imgindex.append(d['filename'])
                yhat.append(d['probability'])
                if not errorOut is None:
                    bbox = d['bbox']
                    errorOut.write('0,{},{},{},{},{},{}\n'.format(f, bbox.xmin, bbox.ymin, bbox.width(), bbox.height(), d['probability']))

        # Missed detections
        for i, truthItem in enumerate(truth):
            if is_assigned[i] == False:
                y.append(1.0)
                imgindex.append(d['filename'])
                yhat.append(minscore)
                if not errorOut is None:
                    bbox = truthItem['bbox']
                    errorOut.write('1,{},{},{},{},{},1.0\n'.format(f, bbox.xmin, bbox.ymin, bbox.width(), bbox.height()))

        if j % 1000 == 0:
            print '[janus.metrics.greedy_bounding_box_assignment][%d/%d]: file=%s, %d detections' % (j+1, len(imfiles), f, len(det))

    if not errorOut is None:
        errorOut.close()

    # Return ground truth label and detection score
    return (y, yhat) if imageIndex is False else (y, yhat, imgindex)


#FIXME: Generalize to different datasets
def order_cs2_results(split, y, yhat, probe_ids, gallery_ids):
    ''' Returns ground truth, scores, probe and gallery template ids ordered according to the CS2 protocol csv files'''

    protocoldir = CS2().protocoldir

    num_y = len(y)
    num_yhat = len(yhat)
    assert num_y==num_yhat, 'num_y [%d] != num_yhat [%d]'%(num_y, num_yhat)
    num_id_pairs = len(probe_ids)
    assert num_y==num_id_pairs, 'num_y [%d] != num_id_pairs [%d]'%(num_y, num_id_pairs)

    probecsv  = os.path.join(protocoldir, 'split%d'%split, 'probe_%d.csv'%split)
    gallerycsv = os.path.join(protocoldir, 'split%d'%split, 'gallery_%d.csv'%split)
    print '\n'.join([probecsv, gallerycsv])

    ordered_probe_ids = []
    ordered_gallery_ids = []

    def getIdList(csvfile):
        ids = []
        with open(csvfile, 'r') as f:
            next(f) # skip header
            for l in f:
                tid = l.encode('utf-8').split(',')[0]
                if not any(ids) or tid != ids[-1]:
                    ids.append(tid)
        return ids

    ordered_probe_ids = getIdList(probecsv)
    ordered_gallery_ids = getIdList(gallerycsv)

    real_id_pairs = [[int(x[0]),int(x[1])] for x in product(ordered_probe_ids, ordered_gallery_ids)]
    test_id_pairs = zip(probe_ids, gallery_ids)

    sfy = []
    sfyhat = []
    sfpid = []
    sfgid = []

    quietprint('[janus.metrics.order_cs2_results]: Starting search...', 2)
    with Stopwatch() as sw:
        stuff = zip(y, yhat, test_id_pairs)
        stuff.sort(key=lambda p: p[2])
        for ids in real_id_pairs:
            ids = tuple(ids) # convert from list
            lb = lower_bound(stuff, ids, key=lambda x: x[2])
            assert lb >= 0, 'Key not found: [%d,%d]: \n%r\n%r'%(ids[0],ids[1], ids, stuff)
            assert ids[0]==stuff[lb][2][0], 'pid mismatch: %d, %d'%(ids[0],stuff[lb][2][0])
            assert ids[1]==stuff[lb][2][1], 'gid mismatch: %d, %d'%(ids[1],stuff[lb][2][1])
            sfy.append(stuff[lb][0])
            sfyhat.append(stuff[lb][1])
            sfpid.append(ids[0])
            sfgid.append(ids[1])
        assert len(sfy)==len(y), 'Failed to find all test pairs! len(y)==%d, len(sfy)==%d'%(len(y),len(sfy))
    quietprint('[janus.metrics.order_cs2_results]: Complete in %.1fs' % sw.elapsed, 2)
    return sfy, sfyhat, sfpid, sfgid


class CS3(object):
    def __init__(self, protocoldir, resultsdir=None):
        self.protocoldir = protocoldir
        self.resultsdir = resultsdir
        if not os.path.isdir(protocoldir):
            'Protocol directory {} does not exist'.format(protocoldir)
            raise ValueError('Protocol directory {} does not exist'.format(protocoldir))

    def __repr__(self):
        return str('<janus.metrics.cs3: protocoldir=%s>' % self.protocoldir)

    def _11_cov(self, verifycsv, refcsv, probecsv):

        h = readcsv(verifycsv, ' ')[0] # header only
        vcsv = readcsv(verifycsv, ' ')[1:] # header
        rcsv = readcsv(refcsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        rid_sid = { r[0]: r[1] for r in rcsv }  # reference template id to subject id
        pid_sid = { r[0]: r[1] for r in pcsv }  # probe template ud to subject id

        Y = [float(pid_sid[r[0]]==rid_sid[r[1]]) for r in vcsv]

        Y = np.array(Y, dtype=np.float32)
        k = h.index('SIMILARITY_SCORE')  # different
        Yhat = [float(r[k]) for r in vcsv]
        Yhat = np.array(Yhat, dtype=np.float32)

        return (Y, Yhat)


    def _11(self, verifycsv, probecsv, gals1csv, gals2csv, separator=' '):

        h = readcsv(verifycsv, separator)[0] # header only
        if len(h) == 1:
            h = readcsv(verifycsv, separator)[0] # header only
            vcsv = readcsv(verifycsv, separator)[1:] # header
        else:
            h = readcsv(verifycsv, separator)[0] # header only
            vcsv = readcsv(verifycsv, separator)[1:] # header

        pcsv = readcsv(probecsv, ',')[1:] # header
        s1csv = readcsv(gals1csv, ',')[1:] # header
        s2csv = readcsv(gals2csv, ',')[1:] # header

        gcsv = s1csv + s2csv  # merge s1 and s2

        gid_sid = { r[0]: r[1] for r in gcsv }  # gallery template id to subject id
        pid_sid = { r[0]: r[1] for r in pcsv }  # probe template ud to subject id

        Y = []
        for r in vcsv:
            try:
                Y.append(pid_sid[r[1]]==gid_sid[r[0]])
            except IndexError as e:
                print 'r: {}; pid_sid length: {}; gid_sid length: {}'.format(r, len(pid_sid), len(gid_sid))
                try:
                    print 'pid_sid {}'.format(pid_sid[r[1]])
                except:
                    print 'Failed accessing pid_sid with {}'.format(r[1])
                try:
                    print 'gid_sid {}'.format(gid_sid[r[0]])
                except:
                    print 'Failed accessing gid_sid with {}'.format(r[0])
                raise e

        # Y = [float(pid_sid[r[1]]==gid_sid[r[0]]) for r in vcsv]   # r[0] is gallery (reference), r[1] is probe (verify)

        Y = np.array(Y, dtype=np.float32)
        try:
            k = h.index('SIMILARITY_SCORE')  # older
        except:
            k = h.index('SCORE')  # newer

        Yhat = [float(r[k]) for r in vcsv]
        Yhat = np.array(Yhat, dtype=np.float32)

        return (Y, Yhat)


    def _1N(self, searchcsv, gallerycsv, probecsv):
        h = readcsv(searchcsv, ' ')[0] # header
        if len(h) == 1:
            h = readcsv(searchcsv, ',')[0] # header                    
            scsv = readcsv(searchcsv, ',')[1:] # header
        else:
            scsv = readcsv(searchcsv, ' ')[1:] # header
        gcsv = readcsv(gallerycsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        gid_to_subject = { r[0]: r[1] for r in gcsv }
        pid_to_subject = { r[0]: r[1] for r in pcsv }

        pid = list(OrderedDict.fromkeys([x[0] for x in pcsv]))  # unique template ids, order preserving
        # print 'pid ({})={}'.format(probecsv, pid)
        gid = list(OrderedDict.fromkeys([x[0] for x in gcsv]))  # unique template ids, order preserving
        # print 'gid ({})={}'.format(gallerycsv, gid)

        pid_to_index = { p : k for (k,p) in enumerate(pid) }
        gid_to_index = { g : k for (k,g) in enumerate(gid) }

        Y = [float(pid_to_subject[p] == gid_to_subject[g]) for (p,g) in product(pid, gid)]
        
        Y = np.array(Y, dtype=np.float32)
        Y.resize([len(pid), len(gid)])

        Yhat = -1E3*np.ones_like(Y)
        try:
            k_score = h.index('SIMILARITY_SCORE')  # OLDER
        except:
            k_score = h.index('SCORE')  # NEWER

        try:
            k_gid = h.index('GALLERY_TEMPLATE_ID')  # NEWER
        except:
            k_gid = 2  # OLDER

        try:
            search_time = h.index('SEARCH_TIME')
        except:
            search_time = -1

        total_search_time = 0.0
        total_search_count = 0
        for r in scsv:
            if search_time > 0:
                total_search_time = total_search_time + float(r[search_time])
                total_search_count = total_search_count + 1
            try:
                i = pid_to_index[r[0]]
            except Exception as e:
                print 'pid_to_index missing match for {}'.format(r)
                raise e
            try:
                j = gid_to_index[r[k_gid]]
            except Exception as e:
                print 'gid_to_index missing match for {} (k_gid={})'.format(r, k_gid)
                raise e
            Yhat[i,j] = float(r[k_score])

        if total_search_count > 0:
            print '[janus.metrics._1N]: Searches: count={}; mean={}'.format(total_search_count, total_search_time / total_search_count)
            
        #n = len(set([int(r[1]) for r in scsv]))  # ranks

        #Y = [float(pid_sid[r[0]]==gid_sid[r[2]]) for r in scsv] # r[0] is probe, r[2] is gallery
        #Y = np.array(Y, dtype=np.float32)
        #Y.resize([len(Y)/n, n])

        #Yhat = [float(r[-1]) for r in scsv]
        #Yhat = np.array(Yhat, dtype=np.float32)
        #Yhat.resize([len(Yhat)/n, n])

        return (Y, Yhat)



    def cs3_1N_img_S1(self, searchcsv=None, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_img.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def cs3_1N_img_S2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_img.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def cs3_1N_mixed_S1(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_1N_mixed_S2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_1N_video_S1(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_video.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_1N_video_S2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs3_1N_gallery_S2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_video.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def cs3_11_mixed(self, verifycsv, detFigure=2, prependToLegend='D3.0', hold=False):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs3_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'cs3_1N_gallery_S1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs3_1N_gallery_S2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs3_11_cov(self, verifycsv, detFigure=2, prependToLegend='D3.0', hold=False):
        """input csv is verify.scores output"""

        probecsv = os.path.join(self.protocoldir, 'cs3_11_covariate_probe_metadata.csv')
        refcsv = os.path.join(self.protocoldir, 'cs3_11_covariate_reference_metadata.csv')
        (Y, Yhat) = self._11_cov(verifycsv, refcsv, probecsv)
        ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)


    def detection(self):
        detcsv = os.path.join(self.protocoldir, 'cs3_face_detection.csv')
        return readcsv(detcsv)


class CS4(CS3):

    def _11_cov(self, verifycsv, probecsv, separator=' '):

        csv = readcsv(verifycsv, separator)
        if len(csv[0]) == 1:
            # HACK: If there was only one field found, try again with the other separator
            if separator == ' ':
                separator = ','
            else:
                separator = ' '
            csv = readcsv(verifycsv, separator)
        h = csv[0] # header only
        vcsv = csv[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        pid_sid = { r[0]: r[1] for r in pcsv }  # probe template id to subject id

        Y = [float(pid_sid[r[0]]==pid_sid[r[1]]) for r in vcsv]

        Y = np.array(Y, dtype=np.float32)

        k = h.index('SIMILARITY_SCORE')  if 'SIMILARITY_SCORE' in h else h.index('SCORE') # different
        Yhat = [float(r[k]) for r in vcsv]
        Yhat = np.array(Yhat, dtype=np.float32)

        return (Y, Yhat)

    def _cs4_11_mixed(self, verifycsv):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        return (Y,Yhat)

    def cs4_11_mixed(self, verifycsv, detFigure=2, prependToLegend='D4.0', hold=False):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs4_1N_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        return ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def cs4_11_cov(self, verifycsv, detFigure=2, prependToLegend='D4.0', hold=False, separator=','):
        """input csv is verify.scores output"""

        probecsv = os.path.join(self.protocoldir, 'cs4_11_covariate_probe_reference.csv')
        (Y, Yhat) = self._11_cov(verifycsv, probecsv, separator=separator)
        return ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def _cs4_1N_mixed_G1(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)
        
    def cs4_1N_mixed_G1(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)

    def _cs4_1N_mixed_G2(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)

    def cs4_1N_mixed_G2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)


    def cs4_1N_mixed_distractors(self, searchcsv, minDistractorId=1000000, split='G1', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        probecsv = os.path.join(self.protocoldir, 'cs4_1N_probe_mixed.csv')
        if split == 'G1':
            gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G1.csv')
        else:
            gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G2.csv')

        with open(searchcsv, 'r') as f:
            list_of_rows_header = [x.strip() for x in f.readline().split(' ')]  # header
            list_of_rows = [[x.strip() for x in r.split(' ')] for r in f.readlines() if int(r.split(' ')[1]) < 50]  # only valid retrievals
        h = list_of_rows_header
        scsv = list_of_rows
        gcsv = readcsv(gallerycsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        gid_to_subject = { r[0]: r[1] for r in gcsv }
        pid_to_subject = { r[0]: r[1] for r in pcsv }

        pid = list(OrderedDict.fromkeys([x[0] for x in pcsv]))  # unique template ids, order preserving
        gid = list(OrderedDict.fromkeys([x[0] for x in gcsv]))  # unique template ids, order preserving
        did = list(set([r[2] for r in scsv if int(r[2]) >= minDistractorId]))  # unique distractor IDs for augmented gallery
        #gid = gid + did;  # append discractors to gallery

        pid_to_index = { p : k for (k,p) in enumerate(pid) }
        gid_to_index = { g : k for (k,g) in enumerate(gid) }
        z = gid_to_subject.copy();  z.update( {x:x for x in did} ); gid_to_subject = z.copy();  # distractor subject ID is template ID


        Y = [float(pid_to_subject[p] == gid_to_subject[g]) for (p,g) in product(pid, gid)]
        Y = np.array(Y, dtype=np.float32)
        Y.resize([len(pid), len(gid)])
        Y = np.hstack( (Y, np.zeros( (len(pid), 50) )) )

        Yhat = -1E3*np.ones_like(Y)
        k = h.index('SIMILARITY_SCORE')
        for r in scsv:
            if int(r[1]) < 50:
                if (int(r[2]) < minDistractorId):
                    (i,j) = (pid_to_index[r[0]], gid_to_index[r[2]])
                else:
                    (i,j) = (pid_to_index[r[0]], len(gid) + int(r[1]))
                Yhat[i,j] = float(r[k])

        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)
                    

    def cs4_detection(self, detectioncsv, min_overlap=0.2, figure=1, prependToLegend='D4.0', logx=True, hold=False, outfile=None):
        """detectioncsv is face_detection.list"""
        (Y,Yh) = greedy_bounding_box_assignment(detectioncsv, os.path.join(self.protocoldir, 'cs4_face_detection.csv'), skipheader=True, min_overlap=min_overlap)
        plot_roc(Y, Yh, label=prependToLegend, figure=figure, logx=logx, hold=hold)
        return strpy.bobo.metrics.savefig(get_outfile(outfile), figure=figure)
        
    def _detection_to_probe(self, detectioncsv, min_overlap=0.5, outfile=None):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [FILENAME,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probecsv file for use in 1:N search, analogous to protocols/cs4_1N_probe_mixed.csv, images with no detections are rejected"""
        # We assume that we have a header here
        detections = readcsv(detectioncsv)
        header = detections[0]
        det_filename = header.index('FILENAME')
        det_face_x = header.index('FACE_X')
        det_face_y = header.index('FACE_Y')
        det_face_width=header.index('FACE_WIDTH')
        det_face_height=header.index('FACE_HEIGHT')

        truth = readcsv(os.path.join(self.protocoldir, 'cs4_metadata.csv'), separator=',')
        header = truth[0]
        truth_filename = header.index('FILENAME')
        truth_category = header.index('SUBJECT_ID')
        truth_face_x = header.index('FACE_X')
        truth_face_y = header.index('FACE_Y')
        truth_face_width=header.index('FACE_WIDTH')
        truth_face_height=header.index('FACE_HEIGHT')
        
        probeset = [ImageDetection(filename=x[det_filename]).boundingbox(xmin=x[det_face_x],ymin=x[det_face_y],width=x[det_face_width],height=x[det_face_height]) if len(x[det_face_x])>0 else ImageDetection(filename=x[det_filename]) for x in detections[1:]]
        truthset = [ImageDetection(filename=x[truth_filename], category=x[truth_category]).boundingbox(xmin=x[truth_face_x],ymin=x[truth_face_y],width=x[truth_face_width],height=x[truth_face_height]) for x in truth[1:]]
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}  
        for imp in probeset:
            truthgroup = d_filename_to_truthset[imp.filename()]
            iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
            if np.max(iou) > min_overlap:
                imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
            else: 
                imp = imp.category('-1')  # set unassigned category
            
        for (k,im) in enumerate(probeset):
            # print 'Probe {}: {}'.format(k, im.filename())
            if not im.bbox.isvalid() and not math.isnan(im.bbox.xmin):
                print ('{}: invalid bounding box @({}, {}) {} x {}'.format(im.filename(), im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()))
        # Template ID is row index (including header) in detectioncsv, subject ID from maximum overlap from ground truth, invalid boxes are discarded
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(k+1, im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(probeset) if im.bbox.isvalid()], get_outfile(outfile, extension='csv'))        

    def _detection_v2_to_probe(self, detectioncsv, min_overlap=0.5, outfile=None, replace_underscore=True):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [TEMPLATE_ID,FILENAME,SUBJECT_ID,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probecsv file for use in 1:N search, analogous to protocols/cs4_1N_probe_mixed.csv, images with no detections are rejected"""
        if replace_underscore:
            probeset = [ImageDetection(filename=x[1].replace('_','/'), attributes={'TEMPLATE_ID':x[0]}).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) if len(x[3])>0 else ImageDetection(filename=x[1].replace('_','/'), attributes={'TEMPLATE_ID':x[0]}) for x in readcsv(detectioncsv)[1:]]
        else:
            probeset = [ImageDetection(filename=x[1], attributes={'TEMPLATE_ID':x[0]}).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) if len(x[3])>0 else ImageDetection(filename=x[1], attributes={'TEMPLATE_ID':x[0]}) for x in readcsv(detectioncsv)[1:]]
        truthset = [ImageDetection(filename=x[1], category=x[0]).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) for x in readcsv(os.path.join(self.protocoldir, 'cs4_metadata.csv'), separator=',')[1:]]
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}  
        for imp in probeset:
            truthgroup = d_filename_to_truthset[imp.filename()]
            iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
            if np.max(iou) > min_overlap:
                imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
            else: 
                imp = imp.category('-1')  # set unassigned category

        # subject ID from maximum overlap from ground truth, invalid boxes are discarded
        for (k,im) in enumerate(probeset):
            # print 'Probe {}: {}'.format(k, im.filename())
            if not im.bbox.isvalid() and not math.isnan(im.bbox.xmin):
                print ('{}: invalid bounding box @({}, {}) {} x {}'.format(im.filename(), im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()))
        # Template ID is row index (including header) in detectioncsv, subject ID from maximum overlap from ground truth, invalid boxes are discarded
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(im.attributes['TEMPLATE_ID'], im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(probeset) if im.bbox.isvalid()], get_outfile(outfile, extension='csv'))        

    def cs4_1N_wild_still_G1(self, searchcsv, detectioncsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, outfile=None):
        """searchcsv is s.candidate_lists output, detectioncsv is detection output, probe template IDs correspond to rows in detectioncsv"""        
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G1.csv')            
        probecsv = self._detection_to_probe(detectioncsv, outfile=outfile) if readcsv(detectioncsv)[0][0] == 'FILENAME' else self._detection_v2_to_probe(detectioncsv, outfile=outfile)   # YUCK
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50, outfile=outfile)

    def cs4_1N_wild_still_G2(self, searchcsv, detectioncsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, outfile=None):
        """searchcsv is s.candidate_lists output, detectioncsv is detection output, probe template IDs correspond to rows in detectioncsv"""        
        gallerycsv = os.path.join(self.protocoldir,'cs4_1N_gallery_G2.csv')            
        probecsv = self._detection_to_probe(detectioncsv, outfile=outfile) if readcsv(detectioncsv)[0][0] == 'FILENAME' else self._detection_v2_to_probe(detectioncsv, outfile=outfile)   # YUCK
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50, outfile=outfile)

    def cs4_clustering_32(self, clustercsv):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (cs4_clustering_32_hint_100.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=True)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_32_hint_100.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}

    def cs4_clustering_1024(self, clustercsv):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (cs4_clustering_1024_hint_10000.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=True)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_1024_hint_10000.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}
        
    def cs4_clustering_1845(self, clustercsv):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (cs4_clustering_1845_hint_10000.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=True)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_1845_hint_10000.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}

    def cs4_clustering_3548(self, clustercsv):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (cs4_clustering_3548_hint_10000.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=True)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'cs4_clustering_2548_hint_10000.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}

class IJBC(CS3):

    def _11_cov(self, verifycsv, probecsv, separator=' '):
        csv = readcsv(verifycsv, ' ')
        if len(csv[0]) == 1:
            csv = readcsv(verifycsv, ',')  # HACK
        h = csv[0] # header only
        vcsv = csv[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        pid_sid = { r[0]: r[1] for r in pcsv }  # probe template id to subject id

        Y = [float(pid_sid[r[0]]==pid_sid[r[1]]) for r in vcsv]

        Y = np.array(Y, dtype=np.float32)
        k = h.index('SIMILARITY_SCORE')  if 'SIMILARITY_SCORE' in h else h.index('SCORE') # different
        Yhat = [float(r[k]) for r in vcsv]
        Yhat = np.array(Yhat, dtype=np.float32)

        return (Y, Yhat)

    def _ijbc_11_mixed(self, verifycsv):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'ijbc_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'ijbc_1N_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'ijbc_1N_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        return (Y,Yhat)

    def ijbc_11_mixed(self, verifycsv, detFigure=2, prependToLegend='D4.0', hold=False, separator=',', detLegendSwap=True, outfile=None):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'ijbc_1N_probe_mixed.csv')
        s1csv = os.path.join(self.protocoldir, 'ijbc_1N_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'ijbc_1N_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv, separator=separator)
        return ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=detLegendSwap, hold=hold, outfile=outfile)

    def ijbc_11_cov(self, verifycsv, detFigure=2, prependToLegend='D4.1', hold=False, separator=','):
        """input csv is verify.scores output"""

        probecsv = os.path.join(self.protocoldir, 'ijbc_11_covariate_probe_reference.csv')
        (Y, Yhat) = self._11_cov(verifycsv, probecsv, separator=separator)
        return ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold)

    def _ijbc_1N_mixed_G1(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'ijbc_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)
        
    def ijbc_1N_mixed_G1(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'ijbc_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)

    def _ijbc_1N_mixed_G2(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'ijbc_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)

    def ijbc_1N_mixed_G2(self, searchcsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'ijbc_1N_probe_mixed.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)

    def ijbc_1N_mixed_distractors(self, searchcsv, minDistractorId=1000000, split='G1', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        probecsv = os.path.join(self.protocoldir, 'ijbc_1N_probe_mixed.csv')
        if split == 'G1':
            gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G1.csv')
        else:
            gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G2.csv')

        with open(searchcsv, 'r') as f:
            list_of_rows_header = [x.strip() for x in f.readline().split(' ')]  # header
            list_of_rows = [[x.strip() for x in r.split(' ')] for r in f.readlines() if int(r.split(' ')[1]) < 50]  # only valid retrievals
        h = list_of_rows_header
        scsv = list_of_rows
        gcsv = readcsv(gallerycsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        gid_to_subject = { r[0]: r[1] for r in gcsv }
        pid_to_subject = { r[0]: r[1] for r in pcsv }

        pid = list(OrderedDict.fromkeys([x[0] for x in pcsv]))  # unique template ids, order preserving
        gid = list(OrderedDict.fromkeys([x[0] for x in gcsv]))  # unique template ids, order preserving
        did = list(set([r[2] for r in scsv if int(r[2]) >= minDistractorId]))  # unique distractor IDs for augmented gallery
        #gid = gid + did;  # append discractors to gallery

        pid_to_index = { p : k for (k,p) in enumerate(pid) }
        gid_to_index = { g : k for (k,g) in enumerate(gid) }
        z = gid_to_subject.copy();  z.update( {x:x for x in did} ); gid_to_subject = z.copy();  # distractor subject ID is template ID


        Y = [float(pid_to_subject[p] == gid_to_subject[g]) for (p,g) in product(pid, gid)]
        Y = np.array(Y, dtype=np.float32)
        Y.resize([len(pid), len(gid)])
        Y = np.hstack( (Y, np.zeros( (len(pid), 50) )) )

        Yhat = -1E3*np.ones_like(Y)
        k = h.index('SIMILARITY_SCORE')
        for r in scsv:
            if int(r[1]) < 50:
                if (int(r[2]) < minDistractorId):
                    (i,j) = (pid_to_index[r[0]], gid_to_index[r[2]])
                else:
                    (i,j) = (pid_to_index[r[0]], len(gid) + int(r[1]))
                Yhat[i,j] = float(r[k])

        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)
                    

    def ijbc_detection(self, detectioncsv, min_overlap=0.2, figure=1, prependToLegend='D4.1', logx=True, hold=False, transform=None, outfile=None, threshold=0.0):
        """detectioncsv is face_detection.list"""
        truthPath = 'ijbc_face_detection_ground_truth.csv'
        if transform != None:
            transformTruthPath = 'ijbc_face_detection_{}.csv'.format(transform)
            if os.path.isfile(os.path.join(self.protocoldir, transformTruthPath)):
                truthPath = transformTruthPath
        elif not os.path.isfile(os.path.join(self.protocoldir, truthPath)):
            truthPath = 'ijbc_face_detection.csv'
        truthFileName = os.path.join(self.protocoldir, truthPath)
        print 'Using ground truth from {}'.format(truthFileName)
        (Y,Yh) = greedy_bounding_box_assignment(detectioncsv, truthFileName, skipheader=True, min_overlap=min_overlap, threshold=threshold)
        plot_roc(Y, Yh, label=prependToLegend, figure=figure, logx=logx, hold=hold)
        return strpy.bobo.metrics.savefig(get_outfile(outfile), figure=figure)

    def _detection_to_probe(self, detectioncsv, min_overlap=0.5, outfile=None):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [FILENAME,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probecsv file for use in 1:N search, analogous to protocols/ijbc_1N_probe_mixed.csv, images with no detections are rejected"""
        proberows, probedict = readcsvwithheader(detectioncsv)
        probeset = [ImageDetection(filename=x[probedict['FILENAME']]).boundingbox(xmin=x[probedict['FACE_X']],ymin=x[probedict['FACE_Y']],width=x[probedict['FACE_WIDTH']],height=x[probedict['FACE_HEIGHT']]) if len(x[1])>0 else ImageDetection(filename=x[0]) for x in proberows]
        # probeset = [ImageDetection(filename=x[0]).boundingbox(xmin=x[1],ymin=x[2],width=x[3],height=x[4]) if len(x[1])>0 else ImageDetection(filename=x[0]) for x in readcsv(detectioncsv)[1:]]
        print 'Truth from {}'.format(os.path.join(self.protocoldir, 'ijbc_metadata.csv'))
        # This generates a set for everything in the metadata (more than we need, perhaps), keyed by subject ID
        truthset = [ImageDetection(filename=x[1], category=x[0]).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) for x in readcsv(os.path.join(self.protocoldir, 'ijbc_metadata.csv'), separator=',')[1:]]
        # and a mapping to let us get from a filename to the ground truth in that file
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}  
        for imp in probeset:
            # Get ground truth
            truthgroup = d_filename_to_truthset[imp.filename()]
            iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
            if np.max(iou) > min_overlap:
                # Sets the subject ID whose ground truth in this frame has the largest overlap
                imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
            else: 
                imp = imp.category('-1')  # set unassigned category
            
        for (k,im) in enumerate(probeset):
            # print 'Probe {}: {}: @({}, {}) {} x {}'.format(k, im.filename(), im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height())
            if not im.bbox.isvalid() and not math.isnan(im.bbox.xmin):
                print ('{}: invalid bounding box @({}, {}) {} x {}'.format(im.filename(), im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()))
        # Template ID is row index (including header) in detectioncsv, subject ID from maximum overlap from ground truth, invalid boxes are discarded
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(k+1, im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(probeset) if im.bbox.isvalid()], get_outfile(outfile, 'csv'))

    def _detection_v2_to_probe(self, detectioncsv, probecsv, min_overlap=0.5, outfile=None):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [TEMPLATE_ID,FILENAME,SUBJECT_ID,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probecsv file for use in 1:N search, analogous to protocols/cs4_1N_probe_mixed.csv, images with no detections are rejected"""
        detected_probeset = [ImageDetection(filename=x[1].replace('_','/'), attributes={'TEMPLATE_ID':x[0]}).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) if len(x[3])>0 else ImageDetection(filename=x[1].replace('_','/'), attributes={'TEMPLATE_ID':x[0]}) for x in readcsv(detectioncsv)[1:]]
        filenames_probeset =  set([x[0] for x in readcsv(probecsv)[1:]])
        missing_probeset = filenames_probeset.difference(set([p.filename() for p in detected_probeset]))  # probe files not found in detectioncsv
        probeset = detected_probeset + [ImageDetection(x, attributes={'TEMPLATE_ID':1000000+int(k)}) for (k,x) in enumerate(missing_probeset)]  # append missing probes with invalid bboxes
        truthset = [ImageDetection(filename=x[1], category=x[0]).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) for x in readcsv(os.path.join(self.protocoldir, 'ijbc_metadata.csv'), separator=',')[1:]]
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}  
        for imp in probeset:
            truthgroup = d_filename_to_truthset[imp.filename()]
            iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
            if imp.bbox.isvalid() and (np.max(iou) > min_overlap):
                imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
            elif imp.bbox.isvalid(): 
                imp = imp.category('-1')  # set unassigned category for valid unassigned box
            else:
                imp = imp.category(d_filename_to_truthset[imp.filename()][0].category())  # set true category for filtered boxes
                imp = imp.boundingbox(xmin=0, ymin=0, width=1, height=1)  # set valid box to pass filter below

        for (k,im) in enumerate(probeset):
            # print 'Probe {}: {}'.format(k, im.filename())
            # taa: Depending on the detector, we may get entries with empty coordinates. Don't print those.
            if not im.bbox.isvalid() and not math.isnan(im.bbox.xmin):
                print ('{}: invalid bounding box @({}, {}) {} x {}'.format(im.filename(), im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()))
        # subject ID from maximum overlap from ground truth, invalid boxes are discarded        
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(im.attributes['TEMPLATE_ID'], im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(probeset) if im.bbox.isvalid()], get_outfile(outfile, extension='csv'))        

    def ijbc_1N_wild_still_G1(self, searchcsv, detectioncsv, cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, detLegendSwap=True, outfile=None, title=None):
        """searchcsv is s.candidate_lists output, detectioncsv is detection output, probe template IDs correspond to rows in detectioncsv"""        
        gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G1.csv')            
        probecsv = self._detection_to_probe(detectioncsv) if readcsv(detectioncsv)[0][0] == 'FILENAME' else self._detection_v2_to_probe(detectioncsv, os.path.join(self.protocoldir, 'ijbc_wild_test9.csv'), outfile=outfile)   # YUCK
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        if title is None:
            title = 'IJBC 1:N G1'
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, title=title, prependToLegend=prependToLegend, detLegendSwap=detLegendSwap, hold=hold, topk=50, L=50)

    def ijbc_1N_wild_still_G2(self, searchcsv, detectioncsv, cmcFigure=3, detFigure=4, title=None, prependToLegend='D4.0', hold=False, detLegendSwap=True, outfile=None):
        """searchcsv is s.candidate_lists output, detectioncsv is detection output, probe template IDs correspond to rows in detectioncsv"""        
        gallerycsv = os.path.join(self.protocoldir,'ijbc_1N_gallery_G2.csv')            
        probecsv = self._detection_to_probe(detectioncsv) if readcsv(detectioncsv)[0][0] == 'FILENAME' else self._detection_v2_to_probe(detectioncsv, os.path.join(self.protocoldir, 'ijbc_wild_test9.csv'), outfile=outfile)   # YUCK
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        if title is None:
            title = 'IJBC 1:N G2'
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, title=title, prependToLegend=prependToLegend, detLegendSwap=detLegendSwap, hold=hold, topk=50, L=50)

    def ijbc_clustering_32(self, clustercsv, ignoreheader=False):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (ijbc_clustering_32_hint_100.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=ignoreheader)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_32_hint_100.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}

    def ijbc_clustering_1021(self, clustercsv, ignoreheader=False):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (ijbc_clustering_1021_hint_10000.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=ignoreheader)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_1021_hint_10000.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}
        
    def ijbc_clustering_1839(self, clustercsv, ignoreheader=False):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (ijbc_clustering_1845_hint_10000.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=ignoreheader)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_1839_hint_10000.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}

    def ijbc_clustering_3531(self, clustercsv, ignoreheader=False):
        """clustertxt is a csvfile of the form (TEMPLATE_ID,FILENAME,CLUSTER_INDEX) where TEMPLATE_ID is assumed to be in the order as the protocol file (ijbc_clustering_3531_hint_10000.csv)"""
        """Returns the precision, recall and f-measure statistics"""
        d_template_id_to_true_cluster_id = {int(x[0]):int(x[1]) for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_ground_truth.csv'), ignoreheader=True)}  # dictionary from templateid to cluster id (== subject IDs)
        est_cluster_id = [int(x[2]) for x in readcsv(clustercsv, ignoreheader=ignoreheader)]  # estimated cluster IDs 
        true_cluster_id = [d_template_id_to_true_cluster_id[int(x[0])] for x in readcsv(os.path.join(self.protocoldir, 'clustering', 'ijbc_clustering_3531_hint_10000.csv'), ignoreheader=True)] 
        prf = bcubed(true_cluster_id, est_cluster_id)
        return {'precision':prf[0], 'recall':prf[1], 'F-score':prf[2]}


class CS5(CS4):

    def _1N(self, searchcsv, gallerycsv, probecsv):
        print '_1N: searchcsv={}; gallery={}; probe={}'.format(searchcsv, gallerycsv, probecsv)
        # If we can, find names in the headers and use those for things that matter.
        scsv, search_header = readcsvwithheader(searchcsv, ' ') # header
        if len(search_header) == 1:
            scsv, search_header = readcsvwithheader(searchcsv)
            if len(scsv[0]) == 1:
                scsv = readcsv(searchcsv, ' ')[1:]  # space separated (HACK, sometimes the header is comma-separated and body is space-separated)
        
        gcsv, gallery_header = readcsvwithheader(gallerycsv, ',')
        pcsv, probe_header = readcsvwithheader(probecsv, ',') # header


        try:
            TEMPLATE_ID = gallery_header['TEMPLATE_ID']
            SUBJECT_ID = gallery_header['SUBJECT_ID']
            gid_to_subject = { r[TEMPLATE_ID]: r[SUBJECT_ID] for r in gcsv }
        except IndexError as ex:
            for i in range(len(gcsv)):
                r = gcsv[i]
                if len(r) < 2:
                    print 'Bad record {} in gcsv'.format(i)
                    break
            raise ex
        try:
            TEMPLATE_ID = probe_header['TEMPLATE_ID']
            SUBJECT_ID = probe_header['SUBJECT_ID']
            pid_to_subject = { r[TEMPLATE_ID]: r[SUBJECT_ID] for r in pcsv }
        except IndexError as ex:
            for i in range(len(pcsv)):
                r = pcsv[i]
                if len(r) < 2:
                    print 'Bad record {} in pcsv'.format(i)
                    break
            raise ex

        pid = list(OrderedDict.fromkeys([x[0] for x in pcsv]))  # unique template ids, order preserving
        gid = list(OrderedDict.fromkeys([x[0] for x in gcsv]))  # unique template ids, order preserving

        pid_to_index = { p : k for (k,p) in enumerate(pid) }
        gid_to_index = { g : k for (k,g) in enumerate(gid) }

        try:
            SCORE = search_header['SIMILARITY_SCORE']  # OLDER
        except:
            SCORE = search_header['SCORE']  # NEWER

        try:
            GALLERY_TEMPLATE_ID = search_header['GALLERY_TEMPLATE_ID']  # NEWER
        except:
            GALLERY_TEMPLATE_ID = 2  # OLDER

        try:
            SEARCH_TIME = search_header['SEARCH_TIME']
        except:
            SEARCH_TIME = -1


        RANK = search_header['RANK']
        try:
            SEARCH_TEMPLATE_ID = search_header['SEARCH_TEMPLATE_ID']
        except KeyError:
            SEARCH_TEMPLATE_ID = search_header['TEMPLATE_ID']
        maxrank = len(set([r[RANK] for r in scsv]))
        Yhat = 1E-3*np.ones( (len(pid), maxrank) ).astype(np.float32)
        Y = np.zeros ( (len(pid), maxrank) ).astype(np.float32)
        Y_ingallery = np.zeros ( (len(pid), 1) ).astype(np.float32)
        G = set(gid_to_subject.values())

        total_search_time = 0.0
        total_search_count = 0

        for r in scsv:
            try:
                i = pid_to_index[r[SEARCH_TEMPLATE_ID]]
            except Exception as e:
                print 'pid_to_index missing match for {}'.format(r)
                raise e
            j = int(r[1])  # rank
            Yhat[i,j] = float(r[SCORE])
            Y[i,j] = float(pid_to_subject[r[SEARCH_TEMPLATE_ID]] == gid_to_subject[r[GALLERY_TEMPLATE_ID]]) 
            Y_ingallery[i] = pid_to_subject[r[0]] in G
            if SEARCH_TIME >= 0 and j == 0:
                total_search_count = total_search_count + 1
                total_search_time = total_search_time + float(r[SEARCH_TIME])

        if total_search_count > 0:
            print '[janus.metrics._1N]: Searches: count={}; mean={}'.format(total_search_count, total_search_time / total_search_count)
            
        for (i,(y,g)) in enumerate(zip(Y,Y_ingallery)):
            if g and np.sum(y) == 0:
                Y[i,:] = np.float32(np.nan)  # subject in gallery but not in top-k, set to nan and handle in metrics code
        return (Y, Yhat)


    def _cs5_11_mixed(self, verifycsv):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs5_1N_still.csv')
        s1csv = os.path.join(self.protocoldir, 'cs5_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs5_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv)
        return (Y,Yhat)

    def cs5_11_mixed(self, verifycsv, detFigure=2, prependToLegend='D4.0', hold=False, separator=',', outfile=None):
        """input csv is verify.scores output"""
        probecsv = os.path.join(self.protocoldir, 'cs5_1N_still.csv')
        s1csv = os.path.join(self.protocoldir, 'cs5_gallery_G1.csv')
        s2csv = os.path.join(self.protocoldir, 'cs5_gallery_G2.csv')
        (Y, Yhat) = self._11(verifycsv, probecsv, s1csv, s2csv, separator=separator)
        return ijba11([Y], Yh=[Yhat], figure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, outfile=outfile)

    def _cs5_1N_mixed_G1(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs5_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs5_1N_still.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)
        
    def cs5_1N_mixed_G1(self, searchcsv, cmcFigure=3, detFigure=4, title='CS5 1:N G1', prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs5_gallery_G1.csv')
        probecsv = os.path.join(self.protocoldir, 'cs5_1N_still.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, title=title, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)

    def _cs5_1N_mixed_G2(self, searchcsv):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs5_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs5_1N_still.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return (Y, Yhat)

    def cs5_1N_mixed_G2(self, searchcsv, cmcFigure=3, detFigure=4, title='CS5 1:N G2', prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        gallerycsv = os.path.join(self.protocoldir,'cs5_gallery_G2.csv')
        probecsv = os.path.join(self.protocoldir, 'cs5_1N_still.csv')
        (Y, Yhat) = self._1N(searchcsv, gallerycsv, probecsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, title=title, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)

    def cs5_1N_mixed_distractors(self, searchcsv, minDistractorId=1000000, split='G1', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False):
        """input csv is s.candidate_lists output"""
        probecsv = os.path.join(self.protocoldir, 'cs5_1N_still.csv')
        if split == 'G1':
            gallerycsv = os.path.join(self.protocoldir,'cs5_gallery_G1.csv')
        else:
            gallerycsv = os.path.join(self.protocoldir,'cs5_gallery_G2.csv')

        with open(searchcsv, 'r') as f:
            list_of_rows_header = [x.strip() for x in f.readline().split(' ')]  # header
            list_of_rows = [[x.strip() for x in r.split(' ')] for r in f.readlines() if int(r.split(' ')[1]) < 50]  # only valid retrievals
        h = list_of_rows_header
        scsv = list_of_rows
        gcsv = readcsv(gallerycsv, ',')[1:] # header
        pcsv = readcsv(probecsv, ',')[1:] # header

        gid_to_subject = { r[0]: r[1] for r in gcsv }
        pid_to_subject = { r[0]: r[1] for r in pcsv }

        pid = list(OrderedDict.fromkeys([x[0] for x in pcsv]))  # unique template ids, order preserving
        gid = list(OrderedDict.fromkeys([x[0] for x in gcsv]))  # unique template ids, order preserving
        did = list(set([r[2] for r in scsv if int(r[2]) >= minDistractorId]))  # unique distractor IDs for augmented gallery
        #gid = gid + did;  # append discractors to gallery

        pid_to_index = { p : k for (k,p) in enumerate(pid) }
        gid_to_index = { g : k for (k,g) in enumerate(gid) }
        z = gid_to_subject.copy();  z.update( {x:x for x in did} ); gid_to_subject = z.copy();  # distractor subject ID is template ID


        Y = [float(pid_to_subject[p] == gid_to_subject[g]) for (p,g) in product(pid, gid)]
        Y = np.array(Y, dtype=np.float32)
        Y.resize([len(pid), len(gid)])
        Y = np.hstack( (Y, np.zeros( (len(pid), 50) )) )

        Yhat = -1E3*np.ones_like(Y)
        k = h.index('SIMILARITY_SCORE')
        for r in scsv:
            if int(r[1]) < 50:
                if (int(r[2]) < minDistractorId):
                    (i,j) = (pid_to_index[r[0]], gid_to_index[r[2]])
                else:
                    (i,j) = (pid_to_index[r[0]], len(gid) + int(r[1]))
                Yhat[i,j] = float(r[k])

        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=True, hold=hold, topk=50, L=50)
                    

    # This now takes the metadata file as a parameter, so it's easier to call for mutant protocols
    def _detection_to_probe(self, detectioncsv, min_overlap=0.5,metadata='cs5_metadata.csv',  outfile=None):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [FILENAME,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probecsv file for use in 1:N search, analogous to protocols/cs5_1N_still.csv, images with no detections are rejected"""
        proberows, probedict = readcsvwithheader(detectionscsv)
        probeset = [ImageDetection(filename=x[probedict['FILENAME']]).boundingbox(xmin=x[probedict['FACE_X']],ymin=x[probedict['FACE_Y']],width=x[probedict['FACE_WIDTH']],height=x[probedict['FACE_HEIGHT']]) if len(x[1])>0 else ImageDetection(filename=x[0]) for x in proberows]
        # If the metadata file can be found without reference to the protocol directory, use it.
        if not os.path.isfile(metadata):
            metadata = os.path.join(self.protocoldir, metadata)
        print 'Truth from {}'.format(metadata)
        # This generates a set for everything in the metadata (more than we need, perhaps), keyed by subject ID
        truthset = [ImageDetection(filename=x[1], category=x[0]).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) for x in readcsv(metadata, separator=',')[1:]]
        # and a mapping to let us get from a filename to the ground truth in that file
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}  
        for imp in probeset:
            # Get ground truth
            truthgroup = d_filename_to_truthset[imp.filename()]
            iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
            if np.max(iou) > min_overlap:
                # Sets the subject ID whose ground truth in this frame has the largest overlap
                imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
            else: 
                imp = imp.category('-1')  # set unassigned category
        for (k,im) in enumerate(probeset):
            # print 'Probe {}: {}: @({}, {}) {} x {}'.format(k, im.filename(), im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height())
            if not im.bbox.isvalid() and not math.isnan(im.bbox.xmin):
                print ('{}: invalid bounding box @({}, {}) {} x {}'.format(im.filename(), im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()))
        # Template ID is row index (including header) in detectioncsv, subject ID from maximum overlap from ground truth, invalid boxes are discarded
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(k+1, im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(probeset) if im.bbox.isvalid()], get_outfile(outfile, 'csv'))

    # Add metadata as parameter
    def _detection_v2_to_probe(self, detectioncsv, probecsv, min_overlap=0.5, outfile=None, replace_underscore=True, metadata='cs5_metadata.csv'):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [TEMPLATE_ID,FILENAME,SUBJECT_ID,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probecsv file for use in 1:N search, analogous to protocols/cs4_1N_probe_mixed.csv, images with no detections are rejected"""
        if replace_underscore:
            detected_probeset = [ImageDetection(filename=x[1].replace('_','/'), attributes={'TEMPLATE_ID':x[0]}).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) if len(x[3])>0 else ImageDetection(filename=x[1].replace('_','/'), attributes={'TEMPLATE_ID':x[0]}) for x in readcsv(detectioncsv)[1:]]
        else:
            detected_probeset = [ImageDetection(filename=x[1], attributes={'TEMPLATE_ID':x[0]}).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) if len(x[3])>0 else ImageDetection(filename=x[1], attributes={'TEMPLATE_ID':x[0]}) for x in readcsv(detectioncsv)[1:]]
        filenames_probeset =  set([x[0] for x in readcsv(probecsv)[1:]])
        missing_probeset = filenames_probeset.difference(set([p.filename() for p in detected_probeset]))  # probe files not found in detectioncsv
        probeset = detected_probeset + [ImageDetection(x, attributes={'TEMPLATE_ID':1000000+int(k)}) for (k,x) in enumerate(missing_probeset)]  # append missing probes with invalid bboxes
        if not os.path.isfile(metadata):
            metadata = os.path.join(self.protocoldir, metadata)
        truthset = [ImageDetection(filename=x[1], category=x[0]).boundingbox(xmin=x[3],ymin=x[4],width=x[5],height=x[6]) for x in readcsv(metadata, separator=',')[1:]]
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}  
        for imp in probeset:
            truthgroup = d_filename_to_truthset[imp.filename()]
            iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
            if imp.bbox.isvalid() and (np.max(iou) > min_overlap):
                imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
            elif imp.bbox.isvalid(): 
                imp = imp.category('-1')  # set unassigned category for valid unassigned box
            else:
                imp = imp.category(d_filename_to_truthset[imp.filename()][0].category())  # set true category for filtered boxes
                imp = imp.boundingbox(xmin=0, ymin=0, width=1, height=1)  # set valid box to pass filter below

        # subject ID from maximum overlap from ground truth, invalid boxes are discarded        
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(im.attributes['TEMPLATE_ID'], im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(probeset) if im.bbox.isvalid()], get_outfile(outfile, extension='csv'))        

    # Add metadata as parameter
    def _detection_v3_to_probe(self, detectionCsv, probeCsv, min_overlap=0.5, outfile=None, metadata='cs5_metadata.csv'):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [TEMPLATE_ID,TEMPLATE_ROLE,FILENAME,FRAME_NUM,FACE_X,FACE_Y,FACE_WIDTH,FACE_HEIGHT,CONFIDENCE,BATCH_IDX,TEMPLATE_CREATION_TIME,TEMPLATE_SIZE]"""
        """Detection schema: [TEMPLATE_ID,FILENAME,SUBJECT_ID,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probeCsv file for use in 1:N search, analogous to protocols/cs4_1N_probe_mixed.csv, images with no detections are rejected"""
        detection_rows, detection_header = readcsvwithheader(detectionCsv, separator=',')

        # If metadata can be found, don't bother with protocol dir.
        if not os.path.isfile(metadata):
            metadata = os.path.join(self.protocoldir, metadata)
        truthset_rows, truthset_header = readcsvwithheader(metadata, separator=',')

        # Get offsets from the header.
        # In this case, we'll die if we can't find them, so no need to bother with get_index.
        treat_as_video = False
        DETECTION_FILENAME = detection_header['FILENAME']
        TRUTH_FILENAME = truthset_header['FILENAME']
        if 'FRAME_NUM' in detection_header and 'FRAME_NUM' in truthset_header:
            print 'Assuming video was used'
            treat_as_video = True
            DETECTION_FRAME = detection_header['FRAME_NUM']
            TRUTH_FRAME = truthset_header['FRAME_NUM']

        # if video, the "filename" gets the frame number appended.
        if treat_as_video:
            detected_probeset = [ImageDetection(filename=x[DETECTION_FILENAME] + '-' + ('0' if x[DETECTION_FRAME] == 'NaN' else x[DETECTION_FRAME]),
                                                attributes={'TEMPLATE_ID':x[detection_header['TEMPLATE_ID']]}).boundingbox(xmin=x[detection_header['FACE_X']],
                                                                                                                           ymin=x[detection_header['FACE_Y']],
                                                                                                                           width=x[detection_header['FACE_WIDTH']],
                                                                                                                           height=x[detection_header['FACE_HEIGHT']])
                                 for x in detection_rows]
        else:
            detected_probeset = [ImageDetection(filename=x[DETECTION_FILENAME],
                                                attributes={'TEMPLATE_ID':x[detection_header['TEMPLATE_ID']]}).boundingbox(xmin=x[detection_header['FACE_X']],
                                                                                                                           ymin=x[detection_header['FACE_Y']],
                                                                                                                           width=x[detection_header['FACE_WIDTH']],
                                                                                                                           height=x[detection_header['FACE_HEIGHT']])
                                 if len(x[4])>0 else ImageDetection(filename=x[DETECTION_FILENAME],
                                                                    attributes={'TEMPLATE_ID':x[detection_header['TEMPLATE_ID']]}) for x in detection_rows]

        # Done this way because when we're doing videos, the filenames in detected_probeset have been mangled so we
        # can match against the mangled truth filenames.
        filenames_detectset = set([x[DETECTION_FILENAME] for x in detection_rows])
        print '{} detections from {}'.format(len(detected_probeset), detectionCsv)
        # "Probe' is kind of a misnomer here--it's really the protocol file, which contains the files we ran detections on.
        probe_rows, probe_header = readcsvwithheader(probeCsv)
        filenames_probeset =  set([x[probe_header['FILENAME']] for x in probe_rows])
        print '{} probes, {} files from {}'.format(len(probe_rows), len(filenames_probeset), probeCsv)
        missing_probeset = filenames_probeset.difference(filenames_detectset)  # probe files not found in detectionCsv
        probeset = detected_probeset + [ImageDetection(x, attributes={'TEMPLATE_ID':1000000+int(k)}) for (k,x) in enumerate(missing_probeset)]  # append missing probes with invalid bboxes
        # truthset was collected above, where the header offsets were set.
        if treat_as_video:
            truthset = [ImageDetection(filename=x[TRUTH_FILENAME] + '-' + ('0' if x[TRUTH_FRAME] == 'NaN' else x[TRUTH_FRAME]),
                                       category=x[truthset_header['SUBJECT_ID']]).boundingbox(xmin=x[truthset_header['FACE_X']],
                                                                                              ymin=x[truthset_header['FACE_Y']],
                                                                                              width=x[truthset_header['FACE_WIDTH']],
                                                                                              height=x[truthset_header['FACE_HEIGHT']])
                        for x in truthset_rows]
        else:
            truthset = [ImageDetection(filename=x[TRUTH_FILENAME],
                                       category=x[truthset_header['SUBJECT_ID']]).boundingbox(xmin=x[truthset_header['FACE_X']],
                                                                                              ymin=x[truthset_header['FACE_Y']],
                                                                                              width=x[truthset_header['FACE_WIDTH']],
                                                                                              height=x[truthset_header['FACE_HEIGHT']])
                    for x in truthset_rows]
        print '{} true detections from {}'.format(len(truthset), metadata)
        # When we're running videos, the truthset filenames are <video-name>-<frame-num>, so this should be
        # grouped *by frame*.
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}
        for imp in probeset:
            iou = 0
            # With videos, a false alarm in an otherwise empty frame would otherwise crash
            try:
                truthgroup = d_filename_to_truthset[imp.filename()]
                iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
            except KeyError:
                pass
            if imp.bbox.isvalid() and (np.max(iou) > min_overlap):
                imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
            elif imp.bbox.isvalid(): 
                imp = imp.category('-1')  # set unassigned category for valid unassigned box
            else:
                try:
                    imp = imp.category(d_filename_to_truthset[imp.filename()][0].category())  # set true category for filtered boxes
                    imp = imp.boundingbox(xmin=0, ymin=0, width=1, height=1)  # set valid box to pass filter below
                except KeyError:
                    pass

        # subject ID from maximum overlap from ground truth, invalid boxes are discarded        
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(im.attributes['TEMPLATE_ID'], im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(probeset) if im.bbox.isvalid()], get_outfile(outfile, extension='csv'))        


    # Pretty much all of the important files can be supplied directly here, for greater flexibility.
    # - searchCsv is the s.candidates_list file.
    # - detectionCsv is the detector output used to generate the probes (can be ugly because it's one line/detection, not one/template, at least for videos).
    # - galleryCsv is the file that maps gallery templates to subject IDs in the metadata
    # - protocolCsv is the file that identifies the input files for the probes
    # - metadata is the truth, including subject IDs and the mapping from template ID to subject ID.
    def cs5_1N_wild_still_G1(self, searchCsv, detectionCsv, galleryCsv='cs5_gallery_G1.csv', protocolCsv='cs5_end_to_end_test9.csv', metadata='cs5_metadata.csv', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, detLegendSwap=True, cmcLegendSwap=False, outfile=None, probeOverlap=0.5):
        """searchCsv is s.candidate_lists output, detectionCsv is detection output, probe template IDs correspond to rows in detectionCsv"""        
        if not os.path.isfile(galleryCsv):
            galleryCsv = os.path.join(self.protocoldir, galleryCsv)
        if not os.path.isfile(protocolCsv):
            protocolCsv = os.path.join(self.protocoldir, protocolCsv)
        probeCsv = self._detection_v3_to_probe(detectionCsv, protocolCsv, outfile=outfile, metadata=metadata, min_overlap=probeOverlap)
        (Y, Yhat) = self._1N(searchCsv, galleryCsv, probeCsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=detLegendSwap, hold=hold, topk=50, L=50, outfile=outfile)

    def cs5_1N_wild_still_G2(self, searchCsv, detectionCsv, galleryCsv='cs5_gallery_G2.csv', protocolCsv='cs5_end_to_end_test9.csv', metadata='cs5_metadata.csv', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, detLegendSwap=True, cmcLegendSwap=False, outfile=None, probeOverlap=0.5):
        """searchCsv is s.candidate_lists output, detectionCsv is detection output, probe template IDs correspond to rows in detectionCsv"""        
        if not os.path.isfile(galleryCsv):
            galleryCsv = os.path.join(self.protocoldir, galleryCsv)
        if not os.path.isfile(protocolCsv):
            protocolCsv = os.path.join(self.protocoldir, protocolCsv)
        probeCsv = self._detection_v3_to_probe(detectionCsv, protocolCsv, outfile=outfile, metadata=metadata, min_overlap=probeOverlap)
        (Y, Yhat) = self._1N(searchCsv, galleryCsv, probeCsv)
        return ijba1N(Y=[Y], Yh=[Yhat], cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, detLegendSwap=detLegendSwap, hold=hold, topk=50, L=50, outfile=outfile)

    def cs5_1N_wild_still(self, G, searchCsv, detectionCsv, galleryCsv='cs5_gallery_G2.csv', protocolCsv='cs5_end_to_end_test9.csv', metadata='cs5_metadata.csv', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, detLegendSwap=True, cmcLegendSwap=False, outfile=None, probeOverlap=0.5):
        if G == 1:
            return self.cs5_1N_wild_still_G1(searchCsv, detectionCsv, galleryCsv=galleryCsv, protocolCsv=protocolCsv, metadata=metadata,
                                             cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, hold=hold,
                                             detLegendSwap=detLegendSwap, cmcLegendSwap=cmcLegendSwap, outfile=outfile, probeOverlap=probeOverlap)
        elif G == 2:
            return self.cs5_1N_wild_still_G2(searchCsv, detectionCsv, galleryCsv=galleryCsv, protocolCsv=protocolCsv, metadata=metadata,
                                             cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, hold=hold,
                                             detLegendSwap=detLegendSwap, cmcLegendSwap=cmcLegendSwap, outfile=outfile, probeOverlap=probeOverlap)

class CS6(CS5):


    # Add metadata as parameter
    def _detection_v3_to_probe(self, detectionCsv, probeCsv, minOverlap=0.5, outfile=None, metadata='cs5_metadata.csv'):
        """Greedy assignment of detections to subjects using ground truth metadata forming labeled probes for 1:N search"""
        """Detection schema: [TEMPLATE_ID,TEMPLATE_ROLE,FILENAME,FRAME_NUM,FACE_X,FACE_Y,FACE_WIDTH,FACE_HEIGHT,CONFIDENCE,BATCH_IDX,TEMPLATE_CREATION_TIME,TEMPLATE_SIZE]"""
        """Detection schema: [TEMPLATE_ID,FILENAME,SUBJECT_ID,XMIN,YMIN,WIDTH,HEIGHT] with header line"""
        """Returns temporary probeCsv file for use in 1:N search, analogous to protocols/cs4_1N_probe_mixed.csv, images with no detections are rejected"""
        detection_rows, detection_header = readcsvwithheader(detectionCsv, separator=',')

        # If metadata can be found, don't bother with protocol dir.
        if not os.path.isfile(metadata):
            metadata = os.path.join(self.protocoldir, metadata)
        truthset_rows, truthset_header = readcsvwithheader(metadata, separator=',')

        # Get offsets from the header.
        # In this case, we'll die if we can't find them, so no need to bother with get_index.
        treat_as_video = False
        DETECTION_FILENAME = detection_header['FILENAME']
        TRUTH_FILENAME = truthset_header['FILENAME']
        if 'FRAME_NUM' in detection_header and 'FRAME_NUM' in truthset_header:
            print 'Assuming video was used'
            treat_as_video = True
            DETECTION_FRAME = detection_header['FRAME_NUM']
            TRUTH_FRAME = truthset_header['FRAME_NUM']

        # if video, the "filename" gets the frame number appended.
        if treat_as_video:
            detected_probeset = [ImageDetection(filename=x[DETECTION_FILENAME] + '-' + ('0' if x[DETECTION_FRAME] == 'NaN' else x[DETECTION_FRAME]),
                                                attributes={'TEMPLATE_ID':x[detection_header['TEMPLATE_ID']]}).boundingbox(xmin=x[detection_header['FACE_X']],
                                                                                                                           ymin=x[detection_header['FACE_Y']],
                                                                                                                           width=x[detection_header['FACE_WIDTH']],
                                                                                                                           height=x[detection_header['FACE_HEIGHT']])
                                 for x in detection_rows]
        else:
            detected_probeset = [ImageDetection(filename=x[DETECTION_FILENAME],
                                                attributes={'TEMPLATE_ID':x[detection_header['TEMPLATE_ID']]}).boundingbox(xmin=x[detection_header['FACE_X']],
                                                                                                                           ymin=x[detection_header['FACE_Y']],
                                                                                                                           width=x[detection_header['FACE_WIDTH']],
                                                                                                                           height=x[detection_header['FACE_HEIGHT']])
                                 if len(x[4])>0 else ImageDetection(filename=x[DETECTION_FILENAME],
                                                                    attributes={'TEMPLATE_ID':x[detection_header['TEMPLATE_ID']]}) for x in detection_rows]

        # Done this way because when we're doing videos, the filenames in detected_probeset have been mangled so we
        # can match against the mangled truth filenames.
        filenames_detectset = set([x[DETECTION_FILENAME] for x in detection_rows])
        print '{} detections from {}'.format(len(detected_probeset), detectionCsv)
        # "Probe' is kind of a misnomer here--it's really the protocol file, which contains the files we ran detections on.
        probe_rows, probe_header = readcsvwithheader(probeCsv)
        filenames_probeset =  set([x[probe_header['FILENAME']] for x in probe_rows])
        print '{} probes, {} files from {}'.format(len(probe_rows), len(filenames_probeset), probeCsv)
        missing_probeset = filenames_probeset.difference(filenames_detectset)  # probe files not found in detectionCsv
        probeset = detected_probeset + [ImageDetection(x, attributes={'TEMPLATE_ID':1000000+int(k)}) for (k,x) in enumerate(missing_probeset)]  # append missing probes with invalid bboxes
        # truthset was collected above, where the header offsets were set.
        if treat_as_video:
            truthset = [ImageDetection(filename=x[TRUTH_FILENAME] + '-' + ('0' if x[TRUTH_FRAME] == 'NaN' else x[TRUTH_FRAME]),
                                       category=x[truthset_header['SUBJECT_ID']]).boundingbox(xmin=x[truthset_header['FACE_X']],
                                                                                              ymin=x[truthset_header['FACE_Y']],
                                                                                              width=x[truthset_header['FACE_WIDTH']],
                                                                                              height=x[truthset_header['FACE_HEIGHT']])
                        for x in truthset_rows]
        else:
            truthset = [ImageDetection(filename=x[TRUTH_FILENAME],
                                       category=x[truthset_header['SUBJECT_ID']]).boundingbox(xmin=x[truthset_header['FACE_X']],
                                                                                              ymin=x[truthset_header['FACE_Y']],
                                                                                              width=x[truthset_header['FACE_WIDTH']],
                                                                                              height=x[truthset_header['FACE_HEIGHT']])
                    for x in truthset_rows]
        print '{} true detections from {}'.format(len(truthset), metadata)
        # When we're running videos, the truthset filenames are <video-name>-<frame-num>, so this should be
        # grouped *by frame*.
        d_filename_to_truthset = {key:list(group) for (key, group) in bobo_groupby(truthset, lambda im: im.filename())}
        d_templateid_to_probegroup = {key:list(group) for (key, group) in bobo_groupby(probeset, lambda im: im.attributes['TEMPLATE_ID'])}
        assigned_probeset = []
        for (tid, probegroup) in d_templateid_to_probegroup.iteritems():
            # Best overlap of tracklet detection 
            for imp in probegroup:
                imp.category('-1')
                # With videos, a false alarm in an otherwise empty frame would otherwise crash
                try:
                    truthgroup = d_filename_to_truthset[imp.filename()]
                    iou = [imp.bbox.overlap(im.bbox) for im in truthgroup]
                except KeyError:
                    iou = 0  # no bounding box in this frame
                if imp.bbox.isvalid() and (np.max(iou) > minOverlap):
                    imp = imp.category(truthgroup[np.argmax(iou)].category())  # set category to maximum ground truth overlap
                    break  # found feasible assignment, use this one for whole tracklet
                elif imp.bbox.isvalid(): 
                    imp = imp.category('-1')  # set unassigned category for valid unassigned box
                else:
                    try:
                        imp = imp.category(d_filename_to_truthset[imp.filename()][0].category())  # set true category for filtered boxes
                        imp = imp.boundingbox(xmin=0, ymin=0, width=1, height=1)  # set valid box to pass filter below
                    except KeyError:
                        print 'keyerror2'
                        pass

            assigned_probeset.append(imp)

        # subject ID from maximum overlap from ground truth, invalid boxes are discarded        
        print len(assigned_probeset)
        return writecsv( [('TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT')] + 
                         [(im.attributes['TEMPLATE_ID'], im.category(), im.filename(), k+1, im.bbox.xmin, im.bbox.ymin, im.bbox.width(), im.bbox.height()) for (k,im) in enumerate(assigned_probeset) if im.bbox.isvalid()], get_outfile(outfile, extension='csv'))        


    def cs6_1N_wild_still_G1(self, searchCsv, detectionCsv, galleryCsv='cs5_gallery_G1.csv', protocolCsv='cs5_end_to_end_test9.csv', metadata='cs5_metadata.csv', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, detLegendSwap=True, cmcLegendSwap=False, outfile=None, probeOverlap=0.5):        
        return self.cs5_1N_wild_still_G1(searchCsv, detectionCsv, galleryCsv=galleryCsv, protocolCsv=protocolCsv, metadata=metadata, cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, hold=hold, detLegendSwap=detLegendSwap, cmcLegendSwap=cmcLegendSwap, outfile=outfile, probeOverlap=probeOverlap)

    def cs6_1N_wild_still_G2(self, searchCsv, detectionCsv, galleryCsv='cs5_gallery_G2.csv', protocolCsv='cs5_end_to_end_test9.csv', metadata='cs5_metadata.csv', cmcFigure=3, detFigure=4, prependToLegend='D4.0', hold=False, detLegendSwap=True, cmcLegendSwap=False, outfile=None, probeOverlap=0.5):        
        return self.cs5_1N_wild_still_G2(searchCsv, detectionCsv, galleryCsv=galleryCsv, protocolCsv=protocolCsv, metadata=metadata, cmcFigure=cmcFigure, detFigure=detFigure, prependToLegend=prependToLegend, hold=hold, detLegendSwap=detLegendSwap, cmcLegendSwap=cmcLegendSwap, outfile=outfile, probeOverlap=probeOverlap)
        

    def cs6_detection_per_image(self, detectioncsv, truthBase='cs6_face_detection_ground_truth', downsample=1, min_overlap=0.5, figure=1, prependToLegend='D4.1', logx=True, hold=False, transform=None, outfile=None, threshold=0.0, legendSwap=False):
        base, ext = os.path.splitext(truthBase)
        if ext != '.csv':
            truthPath = '{}.csv'.format(truthBase)
        else:
            truthPath = truthBase
        if transform != None:
            transformTruthPath = '{}_{}.csv'.format(truthBase, transform)
            if os.path.isfile(os.path.join(self.protocoldir, transformTruthPath)):
                truthPath = transformTruthPath
        elif not os.path.isfile(truthPath) and not os.path.isfile(os.path.join(self.protocoldir, truthPath)):
            truthPath = 'ijbc_face_detection.csv'
        if os.path.isfile(truthPath):
            truthFileName = truthPath
        else:
            truthFileName = os.path.join(self.protocoldir, truthPath)
        print 'Using ground truth from {} ({})'.format(truthFileName, os.path.join(self.protocoldir, '{}.csv'.format(truthBase)))
        print 'Using detections from {}'.format(detectioncsv)
        (Y,Yh,K) = greedy_bounding_box_assignment(detectioncsv, truthFileName, skipheader=True, min_overlap=min_overlap, threshold=threshold, downsample=downsample, imageIndex=True, isVideo=True)
        (fpr, tpr) = strpy.bobo.metrics.roc_per_image(Y, Yh, K)
        plot_roc(fpr=fpr[:-1], tpr=tpr[:-1], label=prependToLegend, figure=figure, logx=logx, hold=hold, xlabel='FPR/Image', legendSwap=legendSwap)
        return strpy.bobo.metrics.savefig(get_outfile(outfile), figure=figure)
        
        
    def cs6_detection(self, detectioncsv, truthBase='cs6_face_detection_ground_truth', downsample=1, min_overlap=0.2, figure=1, prependToLegend='D4.1', logx=True, hold=False, transform=None, outfile=None, threshold=0.0, legendSwap=False):
        """detectioncsv is face_detection.list"""
        base, ext = os.path.splitext(truthBase)
        if ext != '.csv':
            truthPath = '{}.csv'.format(truthBase)
        else:
            truthPath = truthBase
        if transform != None:
            transformTruthPath = '{}_{}.csv'.format(truthBase, transform)
            if os.path.isfile(os.path.join(self.protocoldir, transformTruthPath)):
                truthPath = transformTruthPath
        elif not os.path.isfile(truthPath) and not os.path.isfile(os.path.join(self.protocoldir, truthPath)):
            truthPath = 'ijbc_face_detection.csv'
        if os.path.isfile(truthPath):
            truthFileName = truthPath
        else:
            truthFileName = os.path.join(self.protocoldir, truthPath)
        print 'Using ground truth from {}'.format(truthFileName)
        print 'Using detections from {}'.format(detectioncsv)
        (Y,Yh) = greedy_bounding_box_assignment(detectioncsv, truthFileName, skipheader=True, min_overlap=min_overlap, threshold=threshold, downsample=downsample, isVideo=True)
        plot_roc(Y, Yh, label=prependToLegend, figure=figure, logx=logx, hold=hold, legendSwap=legendSwap)
        return strpy.bobo.metrics.savefig(get_outfile(outfile), figure=figure)
