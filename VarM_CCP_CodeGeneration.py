#import xlrd
import os
import shutil
import config
import time
import CcpOutput
import pyexcel as p


CPPExcel_FileName = "Car Configuration Management.xlsx"
OutpurFolder = "Generated"
VarM_CcpCfg_h_fileName = "\\" + OutpurFolder + "\VarM_CcpCfg.h"
VarM_CcpCfg_c_fileName = "\\" + OutpurFolder + "\VarM_CcpCfg.c"

sheetNames = ["CCP Configuration"]
ROW_START = 2
ROW_END = 1000

variantNames = [];
VARIANT_NUMBER = 1
VARIANT_START_COL = 8
VARIANT_COL_NUM = 5

ParameterNumber_Col = 1
ParameterName_Col = 2
ParameterValue_Col = 3
ParameterValueName_Col = 4
ParameterValueDesc_Col = 5
ParameterNvmPosition_Col = 6
ValidValueForDiag_Col = 7

ValidValueForVariant_Col_Offset = 0
DefaultValueUsedAnyway_Col_Offset = 1
DefaultValue_Col_Offset = 2


class clsValueProperty:
    val = 0
    name = ""
    desc = ""

class clsVariantValueConfig:
    ValidValueList = []
    defaultValueUsedAnyway = False
    variantdefaultValue = 0
    
    
class clsCCPProperty:
    startRow = 0
    number = 0
    name = ""
    NvmPos = 0
    valueList = []    #all value list
    variantValueConfigList = [] #value config list for all variant

#Process a sheet in the excel
def SheetProcess(sheetName):
    ccpList = []
    SearchVariant(sheetName)
    ccpList = SearchCcp(sheetName)
    # if sheetName = "Config Output" is used make this function active
    # CcpOutput.ParseConfigOutput(sheetName)
    GenerateCode(ccpList)
    
    
    return
    
#search variant name
def SearchVariant(sheetName):
    col = VARIANT_START_COL
    while col < sheetName.number_of_columns():
        if sheetName[0, col] != "":
            variantNames.append(sheetName[0, col])
            col += VARIANT_COL_NUM
        else:
            break

#Search the CCP number in the sheet
def SearchCcp(sheetName):
    startRow = ROW_START-1
    endRow = startRow
    tempRow = startRow
    ccpList = []

    #Find the start row of current CCP
    while endRow < sheetName.number_of_rows():
        if sheetName[endRow, 0] == sheetName[tempRow, 0]:
            tempRow = endRow
            endRow += 1
        else:
            ccpList.append(ParseCcp(sheetName, endRow))
            tempRow += 1

    return ccpList

#Parse CCP properties
def ParseCcp(sheetName, startRow):
    ccp = clsCCPProperty()
    ccp.valueList = []
    ccp.variantValueConfigList = []
    
    #Find the end row of current CCP
    endRow = startRow + 1
    while endRow < sheetName.number_of_rows() and sheetName[endRow, 0] == sheetName[startRow, 0]:
        if endRow != sheetName.number_of_rows():
            endRow += 1

    row = startRow
    ccp.startRow = row
    ccp.number = int(sheetName[row, ParameterNumber_Col])
    ccp.name = sheetName[row, ParameterName_Col].replace(' ', '_')
    ccp.NvmPos = int(sheetName[row, ParameterNvmPosition_Col])
    while row < endRow:
        value = clsValueProperty()
        paraValue = int(str(sheetName[row, ParameterValue_Col]), 16)
        value.val = paraValue
        value.name = sheetName[row, ParameterValueName_Col]
        value.desc = sheetName[row, ParameterValueDesc_Col]
        ccp.valueList.append(value)
        row += 1

    variantValueConfigList = []
    variantIndex = 0
    while variantIndex < VARIANT_NUMBER:
        row = startRow
        variantValueConfig = clsVariantValueConfig()
        variantValueConfig.ValidValueList = []
        
        ValidValueForVariant_Col = VARIANT_START_COL + ValidValueForVariant_Col_Offset + VARIANT_COL_NUM * variantIndex
        DefaultValueUsedAnyway_Col = VARIANT_START_COL + DefaultValueUsedAnyway_Col_Offset + VARIANT_COL_NUM * variantIndex
        DefaultValue_Col = VARIANT_START_COL + DefaultValue_Col_Offset + VARIANT_COL_NUM * variantIndex
        while row < endRow:
            value = clsValueProperty()
            value.val = int(str(sheetName[row, ParameterValue_Col]), 16)
            value.name = sheetName[row, ParameterValueName_Col]
            value.desc = sheetName[row, ParameterValueDesc_Col]
            if sheetName[row, ValidValueForVariant_Col] == "Y":
                variantValueConfig.ValidValueList.append(value)

            if sheetName[row, DefaultValueUsedAnyway_Col] == "Y":
                variantValueConfig.defaultValueUsedAnyway = True
            else:
                variantValueConfig.defaultValueUsedAnyway = False
                    
            if sheetName[row, DefaultValue_Col] == "Y":
                variantValueConfig.variantdefaultValue = value
            row += 1
        variantValueConfigList.append(variantValueConfig)
        variantIndex += 1

    ccp.variantValueConfigList = variantValueConfigList
    return ccp

def GenerateCode(ccpList):
    GenerateFile_CcpCfg_c(ccpList)
    GenerateFile_CcpCfg_h(ccpList)
    
    variantIndex = 0
    while variantIndex < 1:
        GenerateFile_Variant(variantIndex, ccpList)
        variantIndex += 1

    return

#File VarM_CcpCfg.c
def GenerateFile_CcpCfg_c(ccpList):    
    file = open(currPath+VarM_CcpCfg_c_fileName, "w")
    includeFileList = ["VarM_CcpCfg.h"]
    CcpConfigStr = ""
    ConfigOutputStr = ""
    
    for ccp in ccpList:
        CcpConfigStr += Generate_CCPConfig(ccp)
    CcpConfigStr += "const VarM_tstrCccParaConfig* VarM_apstrCccParaConfig[VARM_CCP_PARA_NUMBER] = {\n"
    for ccp in ccpList:
        CcpConfigStr += "  /* " + "{0: <72}".format("CCCParameter#" + str(ccp.number)) + "*/\n"
        CcpConfigStr += "  &" + get_CCPConfig_StrName(ccp) + ",\n"
    CcpConfigStr += "};\n\n"
    
    fileContext = config.getVarM_CcpCfg_c_fileContext(VarM_CcpCfg_c_fileName, 
                                                                    "VarM", 
                                                                    "Chang Jiang",
                                                                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                                    includeFileList,
                                                                    "",
                                                                    "",
                                                                    CcpConfigStr,
                                                                    ConfigOutputStr)
                                                                    
    file.writelines(fileContext)
    file.close()
    return
    
#File VarM_CcpCfg.h
def GenerateFile_CcpCfg_h(ccpList):    
    file = open(currPath+VarM_CcpCfg_h_fileName, "w")
    includeFileList = ["VarM_CcpCfg.h"]
    
    PublicVariable = "/* " + "{0: <74}".format("comment: All CCP configuration array") + " */\n"
    PublicVariable += "extern const VarM_tstrCccParaConfig* VarM_apstrCccParaConfig[VARM_CCP_PARA_NUMBER];\n"
    
    ConstStr = "\n"
    
    for ccp in ccpList:
        ConstStr += "/*" + "{0:*^83}".format("CCP#" + str(ccp.number) + ": " + ccp.name) + "*/\n"
        ConstStr += "{0: <70}".format("#define " + get_CcpNumberMacroName(ccp)) + " (uint16)" + str(ccp.number) + "\n\n"
        for value in ccp.valueList:
            ConstStr += "/*{0: <83}*/\n".format(value.desc)
            ConstStr += "{0: <70}".format("#define " + get_CcpValueMacroName(ccp, value)) + " (uint8)" + str(value.val) + "\n"
        ConstStr += "\n\n"
    
    ConstStr += "/*{0:*^83}*/\n".format("")
    ConstStr += "/*{0: ^83}*/\n".format("CCP Index Defination")
    ConstStr += "/*{0:*^83}*/\n".format("")
    ccpIndex = 0
    for ccp in ccpList:
        ConstStr += "{0: <70}".format("#define " + get_CcpIndexMacroName(ccp)) + " (uint8)" + str(ccpIndex) + "\n"
        ccpIndex += 1
    ConstStr += "\n{0: <70} (uint8){1}\n".format("#define VARM_CCP_PARA_NUMBER",str(ccpIndex))
    ConstStr += "\n{0: <70} (uint8)255\n\n".format("#define VARM_INDEX_CCP_INVALID")
    
    ConstStr += "/*{0:*^83}*/\n".format("")
    ConstStr += "/*{0: ^83}*/\n".format("Configuration Output Index Defination")
    ConstStr += "/*{0:*^83}*/\n".format("")
    ConstStr += CcpOutput.getConfigOutputIndexStr()
    
    PublicVariable += "/* " + "{0: <74}".format("comment: Variant CCP configuration for each variant") + " */\n"
    PublicVariable += "extern const VarM_tstrCccParaVariantConfig* VarM_apstrCccParaVariantConfig_Variant[VARM_CCP_PARA_NUMBER];\n"
    #for variantName in variantNames:
    #    PublicVariable += "extern const VarM_tstrCccParaVariantConfig* " + get_VarM_apstrCccParaVariantConfig_Variant(variantName) + "[VARM_CCP_PARA_NUMBER];\n"
    PublicVariable += "/* " + "{0: <74}".format("comment: Configuration output structure list") + " */\n"
    PublicVariable += "extern const VarM_tstrCcpOutputConfig* VarM_astrCcpOutputConfigList[VARM_CONFIG_OUTPUT_NUMBER];\n"
    
    fileContext = config.getVarM_CcpCfg_h_fileContext(VarM_CcpCfg_h_fileName, 
                                                                    "VarM", 
                                                                    "Chang Jiang",
                                                                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                                    includeFileList,
                                                                    ConstStr,
                                                                    "",
                                                                    PublicVariable)
    file.writelines(fileContext)
    file.close()
    return
#File VarM_CcpCfg_xxxx.c    
def GenerateFile_Variant(variantIndex, ccpList):
    fileName = "VarM_CcpCfg_Variant.c"
    file = open(currPath+"\\" + OutpurFolder + "\\" + fileName, "w")
    includeFileList = ["Platform_Types.h", "VarM_CcpCfg.h"]
    CcpConfigStr = ""
    ConfigOutputStr = ""

    
    VarM_astrCccVariantConfig_xxx = []
    VarM_astrCccVariantConfig_xxx_string  = "\n\nconst VarM_tstrCccParaVariantConfig* " + get_VarM_apstrCccParaVariantConfig_Variant(variantNames[variantIndex]) + "[VARM_CCP_PARA_NUMBER] = {\n"
    
    for ccp in ccpList:
        CcpConfigStr += Generate_VariantCCPConfig(ccp, variantIndex)
        VarM_astrCccVariantConfig_xxx_string += "  /*CCCParameter#" + str(ccp.number) + " */\n"
        VarM_astrCccVariantConfig_xxx_string += "  &" + get_astrCccVariantConfig_CCP_xxx_name(ccp, variantIndex) + ",\n"
    
    VarM_astrCccVariantConfig_xxx_string += "};\n"
    CcpConfigStr += VarM_astrCccVariantConfig_xxx_string
    fileContext = config.getVarM_CcpCfg_c_fileContext(fileName, 
                                                    "VarM", 
                                                    "Chang Jiang",
                                                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                    includeFileList,
                                                    "",
                                                    "",
                                                    CcpConfigStr,
                                                    ConfigOutputStr)
    file.writelines(fileContext)
    file.close()
    return
    
def Generate_CCPConfig(ccp):
    Context  = "/*" + "{0:*^75}".format("") + "*/\n"
    Context += "/*" + "{0: <74}".format("CCP Number: "+str(ccp.number)) + " */\n"
    Context += "/*" + "{0: <74}".format("CCP Name: "+str(ccp.name)) + " */\n"
    Context += "/*" + "{0:*^75}".format("") + "*/\n"
    au8ParameterRange = "au8Ccp" + str(ccp.number) + "_" + ccp.name + "_Values"
    Context += "const uint8 "+ au8ParameterRange + "[" + str(len(ccp.valueList)) + "u] = {\n"
    for value in ccp.valueList:
        Context += "  " + get_CcpValueMacroName(ccp, value) + ",  /* " + value.desc + " */\n"
    Context += "};\n"
    
    Context += "const VarM_tstrCccParaConfig " + get_CCPConfig_StrName(ccp) + " = {\n"
    Context += "  /* " + "{0: <72}".format("!Comment : uint16 u16ParaNumber") + "*/\n"
    Context += "  " + get_CcpNumberMacroName(ccp) + ",\n" 
    Context += "  /* " + "{0: <72}".format("!Comment : uint8* pu8ParaValues") + "*/\n"
    Context += "  " + au8ParameterRange + ",\n" 
    Context += "  /* " + "{0: <72}".format("!Comment : uint8  u8ParaValuesCount") + "*/\n"
    Context += "  " + str(len(ccp.valueList))+ "u,\n" 
    Context += "  /* " + "{0: <72}".format("!Comment : uint8  u8NvmPosition") + "*/\n"
    Context += "  " + str(ccp.NvmPos)+ "u,\n" 
    Context += "};\n\n"
    
    return Context
    
def Generate_VariantCCPConfig(ccp, variantIndex):
    Context  = "/*" + "{0:*^75}".format("") + "*/\n"
    Context += "/*" + "{0: <74}".format("CCP Number: "+str(ccp.number)) + " */\n"
    Context += "/*" + "{0:*^75}".format("") + "*/\n"
    Context += "__attribute__((section(\".ROM_UNCHANGE_PARA\")))\n"
    Context += "const uint8 "+ get_pu8ValidParaValues_name(ccp, variantIndex) + "["+ str(len(ccp.valueList)) +"u] = {\n"
    for value in ccp.variantValueConfigList[variantIndex].ValidValueList:
        Context += "  " + get_CcpValueMacroName(ccp, value) + ", /*" + value.desc + " */\n"
    index = len(ccp.variantValueConfigList[variantIndex].ValidValueList)
    while index < len(ccp.valueList):
        Context += "  VARM_CCP_INVALID_VALUE,\n" 
        index += 1
    Context += "};\n\n"
    
    Context += "__attribute__((section(\".ROM_UNCHANGE_PARA\")))\n"
    Context += "const uint8 " + get_ku8ValidParaValuesCount_name(ccp) + " = " + str(len(ccp.variantValueConfigList[variantIndex].ValidValueList))+ "u;\n\n"
    
    Context += "__attribute__((section(\".ROM_UNCHANGE_PARA\")))\n"
    Context += "const uint8 " + get_ku8DefaultValue_name(ccp) + " = " + get_CcpValueMacroName(ccp, ccp.variantValueConfigList[variantIndex].variantdefaultValue) + ";\n\n"
    
    Context += "__attribute__((section(\".ROM_UNCHANGE_PARA\")))\n"
    Context += "const boolean " + get_kbAlwaysUseDefValue(ccp) + " = " + str(ccp.variantValueConfigList[variantIndex].defaultValueUsedAnyway).upper() + ";\n\n"
    
    
    
    Context += "const VarM_tstrCccParaVariantConfig " + get_astrCccVariantConfig_CCP_xxx_name(ccp, variantIndex) + " = {\n"
    Context += "  /* " + "{0: <72}".format("!Comment : const uint8*  pu8ValidParaValues") + "*/\n"
    Context += "  " + get_pu8ValidParaValues_name(ccp, variantIndex) + ",\n"
    Context += "  /* " + "{0: <72}".format("!Comment : const uint8*  pu8ValidParaValuesCount") + "*/\n"
    Context += "  &" + get_ku8ValidParaValuesCount_name(ccp) + ",\n"
    Context += "  /* " + "{0: <72}".format("!Comment : const uint8*  pu8DefaultValue") + "*/\n"
    Context += "  &" + get_ku8DefaultValue_name(ccp) + ",\n"
    Context += "  /* " + "{0: <72}".format("!Comment : const boolean*  pbAlwaysUseDefValue") + "*/\n"
    Context += "  &" + get_kbAlwaysUseDefValue(ccp) + ",\n"
    Context += "};\n"
    return Context
    
def get_pu8ValidParaValues_name(ccp, variantIndex):
    pu8ValidParaValues = "kau8ValidValues_" + ccp.name
    return pu8ValidParaValues
def get_ku8ValidParaValuesCount_name(ccp):
    name = "ku8ValidParaValuesCount_" + ccp.name
    return name
def get_ku8DefaultValue_name(ccp):
    name = "ku8DefaultValue_" + ccp.name
    return name
def get_kbAlwaysUseDefValue(ccp):
    name = "kbAlwaysUseDefValue_" + ccp.name
    return name
def get_astrCccVariantConfig_CCP_xxx_name(ccp, variantIndex):
    pu8ValidParaValues = "kstrCccVarConfig_" + ccp.name 
    return pu8ValidParaValues
#get variable name of CCP Config in VarM_CcpCfg.c
def get_CCPConfig_StrName(ccp):
    name = "kstrCCP" + str(ccp.number) + "_" + ccp.name
    return name
def get_VarM_apstrCccParaVariantConfig_Variant(variantName):
    str = "VarM_apstrCccParaVariantConfig_Variant"
    return str
def get_CcpNumberMacroName(ccp):
    st = "VARM_CCP" + str(ccp.number) + "_" + ccp.name
    return st
def get_CcpValueMacroName(ccp, value):
    name = value.name.replace(" ", "_")
    name = name.replace("(", "_")
    name = name.replace(")", "_")
    name = name.replace(".", "_")
    name = name.replace(",", "_")
    name = name.replace("/", "_")
    name = name.replace("&", "_")
    name = name.replace("-", "_")
    name = name.replace("+", "_")
    name = name.upper()  # Convert all lowercase letters to uppercase
    name = name.strip('_')  # Remove spaces or special characters before and after (left and right) of a string
    name = "VARM_CCP" + str(ccp.number) + "_VAL_" + name

    # isOccurred used as a flag,do what? newName is not changed so name equal to newName
    index = 0
    isOccurred = False
    newName = ""
    while index < len(name):
        if name[index] == "_":
            if isOccurred == False:
                isOccurred = True
                newName += name[index]
        else:
            newName += name[index]
            isOccurred = False
        index += 1
    
    return newName
def get_CcpIndexMacroName(ccp):
    name = "VARM_INDEX_CCP" + str(ccp.number) + "_" + ccp.name
    return name
    

##############################################################################################################
#Entry

#Open the CCP excel
workBook = p.get_sheet(file_name='Car Configuration Management.xlsx')
#Current work path
currPath = os.getcwd()

#Generate VarM folder
if not os.path.exists(OutpurFolder):
    os.mkdir(OutpurFolder)
else:
    shutil.rmtree(OutpurFolder)
    os.mkdir(OutpurFolder)

SheetProcess(workBook)
##############################################################################################################