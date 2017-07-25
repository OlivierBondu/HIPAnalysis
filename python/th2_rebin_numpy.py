"""
TH2F-to-numpy conversion methods, and rebinning of TH2F
"""
__author__ = "Pieter David <pieter.david@uclouvain.be>"
__date__   = "July 2017"
__all__ = ("th2_to_ndarray", "ndarray_to_th2")

import numpy as np

def th2_to_ndarray(hist):
    """
    Convert a TH2 to numpy arrays
    
    Arguments
      hist  the TH2F to convert

    Returns: (xEdges, yEdges, contents, contentErrors), where
    xEdges and yEdges are one-dimensional numpy arrays with the bin edges
    and contents and contentErrors are the bin contents and corresponding
    sums of squared weights (if available), with the same indexes as in ROOT
    (0 is the underflow bin, [1,N] visible bins, and N+1 the overflow bin)
    """
    from itertools import product
    xEdges = np.array(list(
        (hist.GetXaxis().GetBinLowEdge(i), hist.GetXaxis().GetBinUpEdge(i))
        for i in xrange(hist.GetNbinsX()+2)
        )).reshape((hist.GetNbinsX()+2, 2), order="C")
    assert np.all( xEdges[1:,0] == xEdges[:-1,1] )
    xEdges = np.array(xEdges[1:,0]) ## remove lower of underflow and upper of underflow
    yEdges = np.array(list(
        (hist.GetYaxis().GetBinLowEdge(i), hist.GetYaxis().GetBinUpEdge(i))
        for i in xrange(hist.GetNbinsY()+2)
        )).reshape((hist.GetNbinsY()+2, 2))
    assert np.all( yEdges[1:,0] == yEdges[:-1,1] )
    yEdges = np.array(yEdges[1:,0])

    contArray = np.array(list(
        (hist.GetBinContent(i,j), ( hist.GetSumw2()[hist.GetBin(i,j)] if hist.GetSumw2N() > 0 else None ))
        for i,j in product(xrange(hist.GetNbinsX()+2), xrange(hist.GetNbinsY()+2))
        )).reshape((hist.GetNbinsX()+2, hist.GetNbinsY()+2, -1))
    contents  = contArray[:,:,0]
    if hist.GetSumw2N() > 0:
        sumw2 = contArray[:,:,1]
        return (xEdges, yEdges, contents, sumw2)
    else:
        return (xEdges, yEdges, contents)

def ndarray_to_th2(xEdges, yEdges, contents, sumw2=None, name=None, title=None, addXOverflow=False, addYOverflow=False):
    """
    Create a ROOT TH2F from a list of bin edges and contents (optionally also sumw2)
    
    Arguments:
      xEdges    x bin edges
      yEdges    y bin edges
      contents  2-dimensional numpy array with bin contents
    Keyword arguments:
      sumw2     (if given) a 2-dimensional numpy array with the same shape as contents
      name      optional name for the TH2F (otherwise it is created on the heap)
      title     optional title (if name is given, but not title, name is used instead)
      addXOverflow add zero bins for overflow (False by default)
      addYOverflow add zero bins for overflow (False by default)

    Returns the created TH2F
    """
    from itertools import product

    if sumw2 is not None:
        if contents.shape != sumw2.shape:
            raise ValueError("sumw2 array given with shape that is different from contents")

    if addXOverflow:
        emptyRow = np.zeros((1, contents.shape[1]))
        contents = np.concatenate((emptyRow, contents, emptyRow), axis=0)
        if sumw2 is not None:
            sumw2 = np.concatenate((emptyRow, sumw2, emptyRow), axis=0)
    if addYOverflow:
        emptyCol = np.zeros((contents.shape[0], 1))
        contents = np.concatenate((emptyCol, contents, emptyCol), axis=1)
        if sumw2 is not None:
            sumw2 = np.concatenate((emptyCol, sumw2, emptyCol), axis=1)

    if contents.shape != (len(xEdges)+1, len(yEdges)+1):
        raise ValueError("Shapes don't match: {0} from contents, while ({1:d}, {2:d}) from edges".format(contents.shape, len(xEdges)+1, len(yEdges)+1))

    import ROOT
    if name is not None:
        h = ROOT.TH2F(name, title if title is not None else name)
    else:
        h = ROOT.TH2F()

    if ( np.all( xEdges == np.linspace(xEdges[0], xEdges[-1], len(xEdges)) )
     and np.all( yEdges == np.linspace(yEdges[0], yEdges[-1], len(yEdges)) ) ):
        h.SetBins(len(xEdges), xEdges[0], xEdges[-1], len(yEdegs), yEdges[0], yEdges[-1])
    else:
        h.SetBins(len(xEdges)-1, xEdges, len(yEdges)-1, yEdges)

    if sumw2 is not None:
        h.Sumw2(True)
        for i,j in product(xrange(len(xEdges)+1), xrange(len(yEdges)+1)):
            h.SetBinContent(i,j, contents[i,j])
            h.GetSumw2()[h.GetBin(i,j)] = sumw2[i,j]
    else:
        h.Sumw2(False)
        for i,j in product(xrange(len(xEdges)+1), xrange(len(yEdges)+1)):
            h.SetBinContent(i,j, contents[i,j])

    return h

def _rebinOneAxis(arr, axis, oldEdges, newEdges):
    """ Implementation helper for rebinX and rebinY
    
    will rebin a 2D array along axis and assume it contains under- and overflow bins
    """
    from itertools import izip, count

    if ( len(oldEdges) < len(newEdges) ) or not all( nE in oldEdges for nE in newEdges ):
        raise ValueError("Can only rebin to existing bin edges")

    def makeTupleWith(length, otherElm, pos, elm):
        """ tuple with all equal elements, except the one at a specific position """
        return tuple((elm if i == pos else otherElm) for i in xrange(length))

    lineShape = makeTupleWith(len(arr.shape), -1, axis, 1)
    oldEdges = list(oldEdges)
    indices_edges_ext = np.array([ 0 ] + [ oldEdges.index(nE)+1 for nE in newEdges ] + [ -1 ])

    ## replaced by possibly faster (but slightly less readable, ymmv) implementation below
    ##return np.concatenate(tuple(
    ##    np.sum(arr[makeTupleWith(2, slice(None,None), axis, slice(iBegin,iEnd))], axis=axis).reshape(lineShape)
    ##        for iBegin,iEnd in izip(indices_edges_ext[:-1], indices_edges_ext[1:])
    ##    ), axis=axis)
    newShape = list(arr.shape)
    newShape[axis] = len(newEdges)+1
    newArr = np.zeros(newShape)
    for iDest,iBegin,iEnd in izip(count(), indices_edges_ext[:-1], indices_edges_ext[1:]):
        newArr[makeTupleWith(2, slice(None, None), axis, slice(iDest,iDest+1))] = np.sum(
                arr[makeTupleWith(2, slice(None,None), axis, slice(iBegin,iEnd))]
                , axis=axis).reshape(lineShape)
    return newArr
    
def _TH2F_rebinX(hist, newXEdges, name=None, title=None):
    """
    Rebin a TH2F along the X-axis

    Arguments:
      hist      the histogram to rebin
      newXEdges new X-axis bin edges
    Keyword arguments:
      name      name for the new TH2F object
      title     title for the new TH2F object (if name is given but not title, name is used instead)
    """
    ret = th2_to_ndarray(hist)

    newsumw2 = None
    if len(ret) > 3: ## with sumw
        xEdges, yEdges, contents, sumw2 = ret
        newsumw2 = _rebinOneAxis(sumw2, 0, xEdges, newXEdges)
    else:            ## without sumw2
        xEdges, yEdges, contents = ret

    newContents = _rebinOneAxis(contents, 0, xEdges, newXEdges)

    return ndarray_to_th2(np.array(newXEdges), yEdges, newContents, sumw2=newsumw2, name=name, title=title)

def _TH2F_rebinY(hist, newYEdges, name=None, title=None):
    """
    Rebin a TH2F along the Y-axis

    Arguments:
      hist      the histogram to rebin
      newYEdges new Y-axis bin edges
    Keyword arguments:
      name      name for the new TH2F object
      title     title for the new TH2F object (if name is given but not title, name is used instead)
    """
    ret = th2_to_ndarray(hist)

    newsumw2 = None
    if len(ret) > 3: ## with sumw
        xEdges, yEdges, contents, sumw2 = ret
        newsumw2 = _rebinOneAxis(sumw2, 1, yEdges, newYEdges)
    else:            ## without sumw2
        xEdges, yEdges, contents = ret

    newContents = _rebinOneAxis(contents, 1, yEdges, newYEdges)

    return ndarray_to_th2(xEdges, np.array(newYEdges), newContents, sumw2=newsumw2, name=name, title=title)

## decorate TH2F
import ROOT
ROOT.TH2F.rebinX = _TH2F_rebinX
ROOT.TH2F.rebinY = _TH2F_rebinY

if __name__ == "__main__":
    ## Test #1 : create a TH2F from an array, and back again
    ct  = np.array([ [ 1.,  2., 1. ]
                   , [ 2.,  4., 2. ] ])
    err = np.array([ [ 1.,  2., 1. ]
                   , [ 2.,  4., 2. ]  ])

    xEdges = np.array([ -1.,  0., 2. ])
    yEdges = np.array([ -3., -1., 1., 3. ])
    
    #hist = ndarray_to_th2(xEdges, yEdges, ct, addXOverflow=True, addYOverflow=True) ## without errors
    hist = ndarray_to_th2(xEdges, yEdges, ct, sumw2=err**2, addXOverflow=True, addYOverflow=True) ## with errors
    
    import ROOT
    cv1 = ROOT.TCanvas("c1")
    hist.Draw("COLZ,TEXT")
    cv1.Print("test.pdf")

    ## and back again
    conv = th2_to_ndarray(hist)
    print conv

    ## Test #2: now rebin along y, the last two bins together
    hist2 = hist.rebinY([-3., -1., 3.])
    cv2 = ROOT.TCanvas("c2")
    hist2.Draw("COLZ,TEXT")
    cv2.Print("test2.pdf")
