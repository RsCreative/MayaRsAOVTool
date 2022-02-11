# # AOV creation driven by "colorToAOV" node presence in the scene file
# v001 28/01/22 (Raj Sandhu)
# 	- initial code creation
# v002 03/02/22 (Raj Sandhu)
#   - fixed AOVs being placed in wrong channel


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
def getConnections(node):
    aovnamelist = cmds.listAttr('{node}.aov_input_list'.format(node=node), m=True, st="name")
    connect = {}

    for i in range(len(aovnamelist)):
        index = i
        name = cmds.getAttr("{node}.aov_input_list[{i}].name".format(node=node, i=i))
        connect.update({index: name})

    return connect


# Updates AOV list and connects AOV to hypershade node
def createAOV(nodes):
    setColorAOVNodeList(nodes)
    nodelist = getColorAOVNodeList()
    for node in nodelist:
        print("[INFO]" + node)
        checkLookName(node)
        connections = getConnections(node)
        for i, connection in connections.items():
            print("[INFO]" + str(connection))
            if connection == "None":
                continue
            elif i == 0:
                createAovName("rsAov_UvObjp", "U_UVOBJP_uvobjprgb")
                cmds.setAttr("{node}.aov_input_list[{i}].name".format(node=node, i=i),
                             "U_UVOBJP_uvobjprgb", type="string")
                continue
            else:
                createAovName("rsAOV_RGBAOV{i}".format(i=i + 1), "U_RGBAOV_rbgtoaov{i}".format(i=i + 1))
                cmds.setAttr("{node}.aov_input_list[{i}].name".format(node=node, i=i),
                             "U_RGBAOV_rbgtoaov{i}".format(i=i + 1), type="string")
                continue


createAOV(color_to_aov_list)

print("[INFO]Reseting UI")
mel.eval("unifiedRenderGlobalsWindow;")
mel.eval("deleteUI unifiedRenderGlobalsWindow;")
mel.eval("unifiedRenderGlobalsWindow;")
print("[INFO]UI Rest")