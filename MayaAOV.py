# Create AOVs based on Shot requirements AOVcreation_studio
# Changelog
# v002
#   - Fixed duplicate creation of crytomatte aov,if script were to be re-run while cryptomatte was existing in the scene
# v003
#   - Added WorldPosition, ObjectSpacePosition, bumpnormals, zdepth, diffilter, diflight, Shadows and SpecularLighting
#   - Fixed CyrptoObj not being created if CryptoMat existed prior in the scene.
# v004
#   - Fixed Incan shd unable to create Emission aov
# v005
#   - adding a Render Layer check to see if any were created without the cryto override collection
#   - added custom AOV UTL_AO creation
# v006
#   - adding motion vector AOV option
# v008
#   - fixing issue when script is run but crypto/AO/motion vectors already exist
# v011 15/02/22 (Raj Sandhu)
#   - Refactored code to use functions
#   - Importing in Color to AOV script to as one tool
#   - Added UI


import maya.cmds as cmds
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.override as override
import maya.api.OpenMaya as OpenMaya
import maya.mel as mel

aov_list = []
color_to_aov_list = []
name_space_list = []
rgb_to_color_list = []


def setColor2Aov():
    global color_to_aov_list
    color_to_aov_list = cmds.ls(type="RedshiftStoreColorToAOV")


def getColor2Aov():
    global color_to_aov_list
    aovs = color_to_aov_list
    return aovs


def setAovs():
    global aov_list
    aov_list = cmds.ls(type="RedshiftAOV")


def getAovs():
    global aov_list
    aovs = aov_list
    return aovs


def setAovList(aovs):
    MatCheck = cmds.ls(type=(
    "RedshiftMaterial", "RedshiftCarPaint", "RedshiftHair", "RedshiftSubSurfaceScatter", "RedshiftArchitectural",
    "RedshiftIncandescent", "RedshiftSkin", "RedshiftVolume", "RedshiftVolumeScattering"))
    # print(MatCheck)

    gi = int()
    gi_01 = int()
    gi_02 = int()
    reflect = int()
    refract = int()
    sss = int()
    caustic = None
    emission = int()
    translu = int()
    volume = int()

    # Check for GI
    gi_01 += cmds.getAttr("redshiftOptions.primaryGIEngine")
    gi_02 += cmds.getAttr("redshiftOptions.secondaryGIEngine")
    gi = gi_01 + gi_02

    # Check for Caustics
    caustic = cmds.getAttr("redshiftOptions.photonCausticsEnable")

    for i in MatCheck:
        if cmds.nodeType(i) == "RedshiftMaterial":
            reflect += cmds.getAttr(i + ".refl_weight")
            reflect += cmds.getAttr(i + ".coat_weight")
            refract += cmds.getAttr(i + ".refr_weight")
            refract += cmds.getAttr(i + ".ss_amount")
            sss += cmds.getAttr(i + ".ms_amount")
            translu += cmds.getAttr(i + ".transl_weight")
            emission += cmds.getAttr(i + ".emission_weight")
        if cmds.nodeType(i) == "RedshiftHair":
            reflect += cmds.getAttr(i + ".irefl_weight")
            reflect += cmds.getAttr(i + ".trans_weight")
            reflect += cmds.getAttr(i + ".refl_weight")
        if cmds.nodeType(i) == "RedshiftArchitectural":
            reflect += cmds.getAttr(i + ".reflectivity")
            reflect += cmds.getAttr(i + ".refl_base")
            refract += cmds.getAttr(i + ".transparency")
            translu += cmds.getAttr(i + ".refr_trans_weight")
        if cmds.nodeType(i) == "RedShiftCarPaint":
            reflect += 1
        if cmds.nodeType(i) == "RedshiftSubSurfaceScatter":
            sss += 1
        if cmds.nodeType(i) == "RedshiftSkin":
            sss += 1
        if cmds.nodeType(i) == "RedshiftVolume":
            volume += 1
        if cmds.nodeType(i) == "RedshiftVolumeScattering":
            volume += 1
        if cmds.nodeType(i) == "RedshiftIncandescent":
            emission += 1
        else:
            continue

    LitCheck = cmds.ls(type="RedshiftPhysicalLight")

    for lit in LitCheck:
        if cmds.getAttr(lit + ".areaVisibleInRender") == True:
            emission += 1

    if "rsAov_BumpNormals" not in aovs:
        cmds.rsCreateAov(name="rsAov_BumpNormals", type="Bump Normals")
        cmds.setAttr("rsAov_BumpNormals.name", "U_NORBMP_normalbump", type="string")
    if "rsAov_Depth" not in aovs:
        cmds.rsCreateAov(name="rsAov_Depth", type="Depth")
        cmds.setAttr("rsAov_Depth.name", "U_DPTBSE_zdepth", type="string")
        cmds.setAttr("rsAov_Depth.useCameraNearFar", 0)
        cmds.setAttr("rsAov_Depth.depthMode", 1)
    if "rsAov_Shadows" not in aovs:
        cmds.rsCreateAov(name="rsAov_Shadows", type="Shadows")
        cmds.setAttr("rsAov_Shadows.name", "P_SHWBSE_shadow", type="string")
    if gi > 0 and "rsAov_GI" not in aovs:
        cmds.rsCreateAov(name="rsAov_GI", type="Global Illumination")
        cmds.setAttr("rsAov_GI.name", "P_GILBSE_gi", type="string")
        cmds.setAttr("rsAov_GI.allLightGroups", 1)
        cmds.setAttr("rsAov_GI.globalAov", 2)
    if "rsAov_DifFilter" not in aovs:
        cmds.rsCreateAov(name="rsAov_DifFilter", type="Diffuse Filter")
        cmds.setAttr("rsAov_DifFilter.name", "P_DIFFIL_difFilter", type="string")
    if "rsAov_DifLight" not in aovs:
        cmds.rsCreateAov(name="rsAov_DifLight", type="Diffuse Lighting")
        cmds.setAttr("rsAov_DifLight.name", "P_DIFLIT_difLit", type="string")
        cmds.setAttr("rsAov_DifLight.allLightGroups", 1)
        cmds.setAttr("rsAov_DifLight.globalAov", 2)
    if reflect > 0 and "rsAov_Reflect" not in aovs:
        cmds.rsCreateAov(name="rsAov_Reflect", type="Reflections")
        cmds.setAttr("rsAov_Reflect.name", "P_RFLBSE_reflect", type="string")
        cmds.setAttr("rsAov_Reflect.allLightGroups", 1)
        cmds.setAttr("rsAov_Reflect.globalAov", 2)
    if reflect > 0 and "rsAov_Spec" not in aovs:
        cmds.rsCreateAov(name="rsAov_Spec", type="Specular Lighting")
        cmds.setAttr("rsAov_Spec.name", "P_SPCBSE_specular", type="string")
        cmds.setAttr("rsAov_Spec.allLightGroups", 1)
        cmds.setAttr("rsAov_Spec.globalAov", 2)
    if refract > 0 and "rsAov_Refract" not in aovs:
        cmds.rsCreateAov(name="rsAov_Refract", type="Refractions")
        cmds.setAttr("rsAov_Refract.name", "P_RFRBSE_refract", type="string")
        cmds.setAttr("rsAov_Refract.allLightGroups", 1)
        cmds.setAttr("rsAov_Refract.globalAov", 2)
    if sss > 0 and "rsAov_SSS" not in aovs:
        cmds.rsCreateAov(name="rsAov_SSS", type="Sub Surface Scatter")
        cmds.setAttr("rsAov_SSS.name", "P_SSSBSE_subsurface", type="string")
        cmds.setAttr("rsAov_SSS.allLightGroups", 1)
        cmds.setAttr("rsAov_SSS.globalAov", 2)
    if caustic == True and "rsAov_Caustics" not in aovs:
        cmds.rsCreateAov(name="rsAov_Caustics", type="Caustics")
        cmds.setAttr("rsAov_Caustics.name", "P_CAUBSE_caustics", type="string")
    if emission > 0 and "rsAov_Emission" not in aovs:
        cmds.rsCreateAov(name="rsAov_Emission", type="Emission")
        cmds.setAttr("rsAov_Emission.name", "P_EMIBSE_emission", type="string")
        cmds.setAttr("rsAov_Emission.allLightGroups", 1)
        cmds.setAttr("rsAov_Emission.globalAov", 2)
    if translu > 0 and "rsAov_TransTotal" not in aovs:
        cmds.rsCreateAov(name="rsAov_TransTotal", type="Total Translucency Lighting Raw")
        cmds.setAttr("rsAov_TransTotal.name", "P_TRSRAW_transTotal", type="string")
    if volume > 0 and "rsAov_VolLight" not in aovs:
        cmds.rsCreateAov(name="rsAov_VolLight", type="Volume Lighting")
        cmds.setAttr("rsAov_VolLight.name", "P_VOLLIT_volumeLit", type="string")
        cmds.setAttr("rsAov_VolLight.allLightGroups", 1)
        cmds.setAttr("rsAov_VolLight.globalAov", 2)


def setCryptoMat(aovs):
    if "rsAov_CryptoMat" not in aovs:
        cmds.rsCreateAov(name="rsAov_CryptoMat", type="Cryptomatte")
        cmds.setAttr("rsAov_CryptoMat.name", "U_CRYMAT_matte", type="string")
        cmds.setAttr("rsAov_CryptoMat.idType", 1)
        cmds.setAttr("rsAov_CryptoMat.cryptomatteDepth", 10)
        cmds.setAttr("rsAov_CryptoMat.filePrefix", "<BeautyPath>_<RenderPass>/<BeautyFile>_<RenderPass>",
                     type="string")
    if "rsAov_CryptoObj" not in aovs:
        cmds.rsCreateAov(name="rsAov_CryptoObj", type="Cryptomatte")
        cmds.setAttr("rsAov_CryptoObj.name", "U_CRYOBJ_matte", type="string")
        cmds.setAttr("rsAov_CryptoObj.idType", 0)
        cmds.setAttr("rsAov_CryptoObj.cryptomatteDepth", 10)
        cmds.setAttr("rsAov_CryptoObj.filePrefix", "<BeautyPath>_<RenderPass>/<BeautyFile>_<RenderPass>",
                     type="string")

    # checking the existence of a "crypto_or" collection in current render layers
    rlsall = cmds.ls(type="renderSetupLayer")
    rlstoexclude = []
    rlstofix = []

    # pull all "collections" with "*_crypto_off*" in the name
    cryptoOR = cmds.ls("*_crypto_off*", type="collection")
    for node in cryptoOR:
        # pull all connections to the node "collection" that is a "renderSetupLayer"
        nodeConnections = (cmds.listConnections(node, type="renderSetupLayer"))
        for nodeRL in nodeConnections:
            if nodeRL not in rlstoexclude:
                # add RLs to the exclude list
                rlstoexclude.append(nodeRL)
    print rlstoexclude
    # pull check all RLs against the exclude list to build the list of RLs that need the crypto override
    for renderlayer in rlsall:
        if renderlayer not in rlstoexclude:
            rlstofix.append(renderlayer)

    print rlstofix
    # add RL overrides to all RLs in "rlstofix"
    for rlname in rlstofix:
        rs = renderSetup.instance()
        rl = rs.getRenderLayer(rlname)
        c102 = rl.createCollection(rlname + '_crypto_off')
        cmds.setAttr(c102.name() + 'Selector.typeFilter', 8)
        c102.getSelector().setCustomFilterValue('RedshiftAOV')
        cmds.setAttr(c102.name() + "Selector.staticSelection", "rsAov_CryptoMat rsAov_CryptoObj", type="string")
        or102 = c102.createOverride(rlname + '_crypto_off', OpenMaya.MTypeId(0x58000378))
        or102.setAttributeName("enabled")
        or102.finalize("enabled")
        cmds.setAttr(or102.name() + ".attrValue", 0)
        cmds.setAttr(c102.name() + '.selfEnabled', 0)


def setAO(aovs):
    # prompt user, create Ambient Occlussion AOV and shader
    if "rsAov_AO" not in aovs or cmds.objExists("aov_ao_shd") is False or cmds.objExists("aov_ao_mat") is False:

        if "rsAov_AO" not in aovs:
            cmds.rsCreateAov(name="rsAov_AO", type="Custom")
            cmds.setAttr("rsAov_AO.name", "U_AMBOCC_ao", type="string")
        if not cmds.objExists("aov_ao_shd"):
            cmds.shadingNode("RedshiftAmbientOcclusion", asTexture=True, name="aov_ao_shd")
        if not cmds.objExists("aov_ao_mat"):
            cmds.shadingNode("RedshiftIncandescent", asShader=True, name="aov_ao_mat")

        if not cmds.isConnected("aov_ao_shd.outColor", "aov_ao_mat.color"):
            cmds.connectAttr("aov_ao_shd.outColor", "aov_ao_mat.color")
        if not cmds.isConnected("aov_ao_shd.outColor", "rsAov_AO.defaultShader"):
            cmds.connectAttr("aov_ao_shd.outColor", "rsAov_AO.defaultShader")


def setMoVector(aovs):
    # prompt user, create motion vector AOV
    if "rsAov_MoVector" not in aovs:
        if "rsAov_MoVector" not in aovs:
            cmds.rsCreateAov(name="rsAov_MoVector", type="Motion Vectors")
            cmds.setAttr("rsAov_MoVector.name", "U_MOVECT_motionVectors", type="string")
            cmds.setAttr("rsAov_MoVector.outputRawVectors", 1)
            cmds.setAttr("redshiftOptions.motionBlurEnable", 0)


def resetAOVWindow():
    # reload rendersetting UI to dispaly changes
    print("[INFO]Reseting UI")
    mel.eval("unifiedRenderGlobalsWindow;")
    mel.eval("deleteUI unifiedRenderGlobalsWindow;")
    mel.eval("unifiedRenderGlobalsWindow;")
    print("[INFO]UI Rest")

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


def btn_setAOVs(*args):
    setAovs()
    aovs = getAovs()
    setAovList(aovs)
    resetAOVWindow()


def btn_setAO(*args):
    setAovs()
    aovs = getAovs()
    setAO(aovs)
    resetAOVWindow()


def btn_setCrypto(*args):
    setAovs()
    aovs = getAovs()
    setCryptoMat(aovs)
    resetAOVWindow()


def btn_setMoVec(*args):
    setAovs()
    aovs = getAovs()
    setCryptoMat(aovs)
    resetAOVWindow()


def btn_setColor2AOV(*args):
    setColor2Aov()
    aovs = getColor2Aov()
    createAOV(aovs)
    resetAOVWindow()


def ui():
    if cmds.window('AOV Generator', ex=True):
        cmds.deleteUI('AOV Generator')

    window = cmds.window(title="AOV Generator", rtf=True)
    layout_MainUI = cmds.rowColumnLayout(numberOfColumns=1, cs=[1, 2], rs=[1, 10])
    spacer = cmds.text(p=layout_MainUI, label='')
    label_title = cmds.text(p=layout_MainUI, fn='boldLabelFont', label="Maya AOV Creation", align='left')
    spacer = cmds.text(p=layout_MainUI, label='')

    layout_AddAOV = cmds.rowLayout(parent=layout_MainUI, numberOfColumns=2, columnWidth2=(150, 150))

    label_addAov = cmds.text(p=layout_AddAOV, label="Set Standard AOVs", align='right')
    btn_addAov = cmds.button("createAOV", p=layout_AddAOV, l=" Create AOVs", c=btn_setAOVs,
                             aop=False, align='center', w=150)

    layout_AddCrypto = cmds.rowLayout(parent=layout_MainUI, numberOfColumns=2, columnWidth2=(150, 150))

    label_addCrypto = cmds.text(p=layout_AddCrypto, label="Set Crypto Matte and OBJ", align='right')
    btn_addCrypto = cmds.button("createCrypto", p=layout_AddCrypto, l="Create Crypto", c=btn_setCrypto,
                                aop=False, align='center', w=150)

    layout_AddAO = cmds.rowLayout(parent=layout_MainUI, numberOfColumns=2, columnWidth2=(150, 150))

    label_addAo = cmds.text(p=layout_AddAO, label="Set AO AOV", align='right')
    btn_addAo = cmds.button("createAO", p=layout_AddAO, l="Create AO", c=btn_setAO,
                            aop=False, align='center', w=150)

    layout_AddMoVec = cmds.rowLayout(p=layout_MainUI, numberOfColumns=2, columnWidth2=(150, 150))
    label_addMoVec = cmds.text(p=layout_AddMoVec, label="Set Motion Vector", align='right')
    btn_addMoVec = cmds.button("createMoVec", p=layout_AddMoVec, l="Create MoVec", c=btn_setMoVec,
                               aop=False, align='center', w=150)

    layout_addc2aov = cmds.rowLayout(p=layout_MainUI, numberOfColumns=2, columnWidth2=(150, 150))
    label_addc2aov = cmds.text(p=layout_addc2aov, label='Set Color To AOV', align='right')
    btn_addColor2aov = cmds.button("creatC2A", p=layout_addc2aov, l="Create Color To AOV", c=btn_setColor2AOV,
                                   aop=False, align='center', w=150)
    spacer = cmds.text(p=layout_MainUI, label='')


    cmds.showWindow(window)


def run():
    ui()


run()
