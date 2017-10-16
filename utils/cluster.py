from maya import cmds
from .curve import numCVs

def getClusterPosition(cluster):
    """
    Get the origin position of a cluster, positions are rounded to 6 
    decimals to be able to match positions.
    
    :param str cluster:
    :return: origin position of cluster
    :rtype: list
    """
    pos = cmds.getAttr("{0}.origin".format(cluster))[0]
    return [round(p, 6) for p in pos]
    
# ----------------------------------------------------------------------------
    
def clusterCurve(curve, name):
    """
    Create a cluster on each cv of a curve.

    :param str curve: 
    :param str name: 
    :return: List of created clusters
    :rtype: list of strings
    """
    clusters = []

    # get num cvs on curve
    num = numCVs(curve)

    # create clusters
    for i in range(num):
        # create cluster
        clusterShape, clusterTransform = cmds.cluster(
            "{0}.cv[{1}]".format(
                curve, 
                i
            )
        )

        # rename shape and transform
        clusterShape = cmds.rename(
            clusterShape, 
            "{0}_clusterShape_{1:03d}".format(name, i+1)
        )
        clusterTransform = cmds.rename(
            clusterTransform, 
            "{0}_cluster_{1:03d}".format(name, i+1)
        )
        
        # set and lock visibility
        cmds.setAttr("{0}.visibility".format(clusterTransform), 0)
        cmds.setAttr("{0}.visibility".format(clusterTransform), lock=True)

        # store transform
        clusters.append(clusterTransform)

    return clusters