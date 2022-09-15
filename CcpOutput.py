import os
import pyexcel as p
#import VarM_CCP_CodeGeneration

sheetName = "Config Output"
ROW_START = 2
ROW_END = 1000

ConfigName_Col = 0
ConfigDataType_Col = 1
RelatedCcpNumber_Col = 2
OutputValue_Col = 6

CcpOutput_CcpList = []

class clsConfigOutput:
    name = ""
    dataSource = ""
    relatedCcpNum = 0
    outputValueList = []

ConfigOutputList = []
    
def ParseConfigOutput(sheet):
    # Find the start row of current CCP
    startRow = ROW_START-1
    endRow = startRow
    tempRow = startRow
    while endRow < sheet.number_of_rows():
        if sheet[endRow, 0] == sheet[tempRow, 0]:
            tempRow = endRow
            endRow += 1
        else:
            ConfigOutputList.append(ParseConfig(sheet, endRow))
            tempRow += 1

    return ConfigOutputList

        
def ParseConfig(sheet, startRow):
    config = clsConfigOutput()
    config.outputValueList = []
    row = startRow
    config.name = sheet[row, ConfigName_Col]
    config.dataSource = sheet[row, ConfigDataType_Col]
    if config.dataSource == "CCP":
        config.relatedCcpNum = int(str(sheet[row, RelatedCcpNumber_Col]))
    else:
        config.relatedCcpNum = 0
    output = int(str(sheet[row, OutputValue_Col]), 16)
    config.outputValueList.append(output)
        
    row += 1
    while row < sheet.number_of_rows:
        if sheet[row, ConfigName_Col] == "":
            output = int(str(sheet[row, OutputValue_Col]), 16)
            config.outputValueList.append(output)
        else:
            break
        row += 1
    return config
    
def getConfigNum():
    return len(ConfigOutputList)
    
def getConfigOutputStr(ccpList):
    context = ""
    
    for ConfigOutput in ConfigOutputList:
        context += "\n\n/*{0:*^75}*/\n".format("")
        context += "/*{0: ^75}*/\n".format("Config Output: "+ConfigOutput.name)
        context += "/*{0:*^75}*/\n".format("")
        context += "static " + getConfigVariableName(ConfigOutput) + " = 0u;\n"
        context += "const uint8 " + getOutputListName(ConfigOutput) + "[" + str(len(ConfigOutput.outputValueList)) + "u] = {\n"
        for output in ConfigOutput.outputValueList:
            context += "  " + str(output) + "u,\n"
        context += "};\n"
        context += "const VarM_tstrCcpOutputConfig " + getCcpOutputConfigName(ConfigOutput) + " = \n{\n"
        context += "  &" + getConfigVariableName(ConfigOutput) + ",\n"
        context += "  VARM_CONFIG_OUTPUT_SRC_" + ConfigOutput.dataSource.upper() + ",\n"
        if ConfigOutput.dataSource == "CCP":
            context += "  " + str(getCcpIndex(ccpList, ConfigOutput.relatedCcpNum)) + "u,\n"
        else:
            context += "  VARM_INDEX_CCP_INVALID,\n"
        
        context += "  " + getOutputListName(ConfigOutput) + ",\n};\n\n"
        
    context += "/* comment: Configuration output structure list                               */\n"
    context += "const VarM_tstrCcpOutputConfig* VarM_astrCcpOutputConfigList[VARM_CONFIG_OUTPUT_NUMBER] = {\n"
    for ConfigOutput in ConfigOutputList:
        context += "  &{0},\n".format(getCcpOutputConfigName(ConfigOutput))
    context += "};\n"
    return context
    
def getConfigOutputIndexStr():
    string = ""
    index = 0
    for ConfigOutput in ConfigOutputList:
        string += "#define {0: <62} (uint8){1}u\n".format("VARM_CONFIG_OUTPUT_INDEX_"+ConfigOutput.name.upper(), str(index))
        index += 1
    string += "\n#define {0: <62} (uint8){1}u\n".format("VARM_CONFIG_OUTPUT_NUMBER", str(index))
    return string
def getConfigVariableName(config):
    name = "VarM_u16" + config.name
    return name
def getOutputListName(config):
    name = "kau8ConfigOutputList_" + config.name
    return name
def getCcpOutputConfigName(config):
    name = "VarM_strConfig_" + config.name
    return name
def getCcpIndex(ccpList, ccpNum):
    index = 0
    for ccp in ccpList:
        if ccp.number == ccpNum:
            break;
        index += 1
    return index