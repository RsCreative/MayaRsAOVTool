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
#   - adding motion vector AOV option v008 - fixing issue when script is run but crypto/AO/motion vectors already exist

import maya.cmds as cmds
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.override as override
import maya.api.OpenMaya as OpenMaya
import maya.mel as mel
import customAOV
from customAOV import *

aov_list = cmds.ls(type="RedshiftAOV")
gi = int()
reflect = int()
refract = int()
sss = int()
caustic = None
emission = int()
translu = int()
volume = int()
color_to_aov_list = cmds.ls(type="RedshiftStoreColorToAOV")


def materialCheck(aov_gi, aov_reflect, aov_refract, aov_sss, aov_caustic, aov_emission, aov_translu, aov_volume):
    MatCheck = cmds.ls(type=(
        "RedshiftMaterial", "RedshiftCarPaint", "RedshiftHair", "RedshiftSubSurfaceScatter", "RedshiftArchitectural",
        "RedshiftIncandescent", "RedshiftSkin", "RedshiftVolume", "RedshiftVolumeScattering"))
    LitCheck = cmds.ls(type="RedshiftPhysicalLight")
    gi_01 = int()
    gi_02 = int()
    # Check for GI
    gi_01 += cmds.getAttr("redshiftOptions.primaryGIEngine")
    gi_02 += cmds.getAttr("redshiftOptions.secondaryGIEngine")
    aov_gi = gi_01 + gi_02
    # Check for Caustics
    aov_caustic = cmds.getAttr("redshiftOptions.photonCausticsEnable")

    for i in MatCheck:
        if cmds.nodeType(i) == "RedshiftMaterial":
            aov_reflect += cmds.getAttr(i + ".refl_weight")
            aov_reflect += cmds.getAttr(i + ".coat_weight")
            aov_refract += cmds.getAttr(i + ".refr_weight")
            aov_refract += cmds.getAttr(i + ".ss_amount")
            aov_sss += cmds.getAttr(i + ".ms_amount")
            aov_translu += cmds.getAttr(i + ".transl_weight")
            aov_emission += cmds.getAttr(i + ".emission_weight")
        if cmds.nodeType(i) == "RedshiftHair":
            aov_reflect += cmds.getAttr(i + ".irefl_weight")
            aov_reflect += cmds.getAttr(i + ".trans_weight")
            aov_reflect += cmds.getAttr(i + ".refl_weight")
        if cmds.nodeType(i) == "RedshiftArchitectural":
            aov_reflect += cmds.getAttr(i + ".reflectivity")
            aov_reflect += cmds.getAttr(i + ".refl_base")
            aov_refract += cmds.getAttr(i + ".transparency")
            aov_translu += cmds.getAttr(i + ".refr_trans_weight")
        if cmds.nodeType(i) == "RedShiftCarPaint":
            aov_reflect += 1
        if cmds.nodeType(i) == "RedshiftSubSurfaceScatter":
            aov_sss += 1
        if cmds.nodeType(i) == "RedshiftSkin":
            aov_sss += 1
        if cmds.nodeType(i) == "RedshiftVolume":
            aov_volume += 1
        if cmds.nodeType(i) == "RedshiftVolumeScattering":
            aov_volume += 1
        if cmds.nodeType(i) == "RedshiftIncandescent":
            aov_emission += 1
        else:
            continue

    for lit in LitCheck:
        if cmds.getAttr(lit + ".areaVisibleInRender"):
            aov_emission += 1


def setAovList(aovs):
    # List of AOVs in the scene

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
    if "rsAov_CryptoMat" not in aovs or "rsAov_CryptoObj" not in aovs:
        title = "Create Cryptomatte AOV?"
        message = "Create Cryptomatte AOV?"
        button1 = "Yes"
        button2 = "No"
        crypto = cmds.confirmDialog(title=title, message=message, button=[button1, button2], cancelButton=button2,
                                    dismissString=button2)

        if crypto == "Yes":
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
        title = "Create AO AOV?"
        message = "Create Ambient Occlussion AOV?"
        button1 = "Yes"
        button2 = "No"
        aoAOV = cmds.confirmDialog(title=title, message=message, button=[button1, button2], cancelButton=button2,
                                   dismissString=button2)

        if aoAOV == "Yes":
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
        title = "Create Motion Vector AOV?"
        message = "Create Motion Vector AOV?"
        button1 = "Yes"
        button2 = "No"
        mvAOV = cmds.confirmDialog(title=title, message=message, button=[button1, button2], cancelButton=button2,
                                   dismissString=button2)

        if mvAOV == "Yes":
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


def run():
    materialCheck(gi, reflect, refract, sss, caustic, emission, translu, volume)
    setAovList(aov_list)
    # UV RGB position custom AOV creation driven by "colorToAOV" node presence in the scene file
    customAOV.createAOV(color_to_aov_list)
    setCryptoMat(aov_list)
    setAO(aov_list)
    setMoVector(aov_list)
    resetAOVWindow()


run()
