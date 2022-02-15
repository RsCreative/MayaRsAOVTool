# # AOV creation driven by "colorToAOV" node presence in the scene file
# v001 28/01/22 (Raj Sandhu)
# 	- initial code creation
# v002 03/02/22 (Raj Sandhu)
#   - fixed AOVs being placed in wrong channel
# v003 03/02/22 (Raj Sandhu)
#     - fixed that no all AOV where being created
#     - fixed the issue where node would added extra inputs
#     - fixed naming so that empty aov where not being created
# v004 15/02/22 (Raj Sandhu)
#   -Removed unsed code

import maya.cmds as cmds
import maya.mel as mel

color_to_aov_list = cmds.ls(type="RedshiftStoreColorToAOV")
name_space_list = []
rgb_to_color_list = []


# Check if look is on pipe
def checkLookName(node):
    if ":" not in node:
        check = False
        print("[ERROR]{node} is not on pipe".format(node=node))
        cmds.error("[ERROR]{node} is not on pipe".format(node=node))
    else:
        check = True

    return check


# Create list of color to AOV nodes with proper look names
def setColorAOVNodeList(nodelist):
    if nodelist is not None and len(nodelist) != 0:
        for node in nodelist:
            if checkLookName(node):
                rgb_to_color_list.append(node)


# Get AOV node list
def getColorAOVNodeList():
    global rgb_to_color_list
    nodelist = rgb_to_color_list
    return nodelist


# Create AOV for render setting list
def createAovName(claovname, aovrendername):
    # check if AOV name exists
    if not cmds.objExists(claovname):
        # Create node name for AOV
        cmds.rsCreateAov(name=claovname, type="Custom")
        # Create render name for AOV
        cmds.setAttr("{claovname}.name".format(claovname=claovname), aovrendername, type="string")
        # Logging
        print("[INFO]Setting Connection for {claovname}".format(claovname=claovname))
        # connect look to AOV


# Creates a dictionary of index and connections in AOV input list
def checkAOVexist():
    nodelist = cmds.ls(type="RedshiftStoreColorToAOV")
    aovnode = {}
    dex = 0
    for node in nodelist:
        aovnamelist = cmds.listAttr('{node}.aov_input_list'.format(node=node), m=True, st="name")

        for i, connection in enumerate(aovnamelist):
            name = cmds.getAttr("{node}.{connection}".format(node=node, connection=connection))
            if name not in aovnode.values():
                aovnode.update({dex: name})
                dex = dex + 1
    return aovnode


def getConnections(node):
    global index
    aovnamelist = cmds.listAttr('{node}.aov_input_list'.format(node=node), m=True, st="name")
    connect = {}
    aovnode = checkAOVexist()

    for i, connection in enumerate(aovnamelist):
        name = cmds.getAttr("{node}.{connection}".format(node=node, connection=connection))
        if name != "None":
            if name in aovnode.values():
                aovdex = aovnode.keys()[aovnode.values().index(name)]
                connect.update({aovdex: connection})

    for key, value in connect.items():
        print (int(key), str(value))

    return connect


# Updates AOV list and connects AOV to hypershade node
def createAOV(nodes):
    for node in nodes:
        print ''
        print("[INFO]" + node)
        checkLookName(node)
        connections = getConnections(node)
        for key, value in connections.items():
            if str(value) == "aov_input_list[0].name":
                createAovName("rsAov_UvObjp", "U_UVOBJP_uvobjprgb")
                cmds.setAttr("{node}.aov_input_list[0].name".format(node=node),
                             "U_UVOBJP_uvobjprgb", type="string")
                print "[AOV Name]rsAov_UvObjp"
                print "[AOV Display]U_UVOBJP_uvobjprgb"
                print ("[Connect]{i}".format(i=value))
            else:
                createAovName("rsAOV_RGBAOV{key}".format(key=key), "U_RGBAOV_rbgtoaov{key}".format(key=key))
                cmds.setAttr("{node}.{value}".format(node=node, value=str(value)),
                             "U_RGBAOV_rbgtoaov{key}".format(key=key), type="string")

