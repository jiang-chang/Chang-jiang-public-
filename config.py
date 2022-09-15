import os

VarM_CcpCfg_c_fileContext = '''/******************************************************************************
 * %PCMS_HEADER_SUBSTITUTION_START%/
 * COMPANY : What  You Want
 *
 * PROJECT  : %PP%:User Defined
 *
 ******************************************************************************
 * !File            : %PM%
 *
 * !Component       : <Component name>
 * !Description     :
 *   Describe here the component <Component name>
 *   Precise the <Component IDentifier ("CompID")>
 *     if different from <Component name>
 *   Possibility to use several lines
 *
 * !Module          : <Module name>
 * !Description     :
 *   Describe here the module <Module name>
 *   Possibility to use several lines
 *
 *
 * !Author          : %AUTHOR%                   !Date: %DATE%
 * !Coding Language : C
 *
 * !COPYRIGHT 
 * All rights reserved
 ******************************************************************************
 ******************************************************************************
 * EVOLUTIONS (automatic update under DIMENSIONS)
 ******************************************************************************
 * Current revision : %PR%
 *
 * %PL%
 * %PCMS_HEADER_SUBSTITUTION_END%
 *****************************************************************************/

/*****************************************************************************/
/* INCLUDE FILES                                                             */
/*****************************************************************************/

/*********************** Definition of common types **************************/


/****************** Sources to be used within the module *********************/


/***************** Headers implemented within the module *********************/
%INCLUDE%

/*****************************************************************************/
/* CONSTANTS, MACROS                                                         */
/*****************************************************************************/


/*****************************************************************************/
/* TYPES                                                                     */
/*****************************************************************************/


/*****************************************************************************/
/* PRIVATE FUNCTIONS PROTOTYPES                                              */
/*****************************************************************************/

/*****************************************************************************/
/* PRIVATE VARIABLES                                                         */
/*****************************************************************************/
%CCP_CONFIGURATION%

%CONFIGURATION_OUTPUT%

'''

VarM_CcpCfg_h_fileContext = '''
/******************************************************************************
 * %PCMS_HEADER_SUBSTITUTION_START%
 * COMPANY : What  You Want
 *
 * PROJECT  : %PP%:110xxxxx(none)
 *
 ******************************************************************************
 * !File            : %PM%
 *
 * !Component       : <Component name>
 * !Description     :
 *   Describe here the component <Component name>
 *   Precise the <Component IDentifier ("CompID")>
 *     if different from <Component name>
 *   Possibility to use several lines
 *
 * !Module          : <Module name>
 * !Description     :
 *   Describe here the module <Module name>
 *   Possibility to use several lines
 *
 *
 * !Author          : %AUTHOR%                   !Date: %DATE%
 * !Coding Language : C
 *
 * !COPYRIGHT 2018 
 * All rights reserved
 ******************************************************************************
 ******************************************************************************
 * EVOLUTIONS (automatic update under DIMENSIONS)
 ******************************************************************************
 * Current revision : %PR%
 *
 * %PL%
 * %PCMS_HEADER_SUBSTITUTION_END%
 ******************************************************************************/

/***************** Protections against multiple inclusions ********************/
#ifndef VARM_CCPCFG_H
#define VARM_CCPCFG_H

/******************************************************************************/
/* INCLUDE FILES                                                              */
/******************************************************************************/
#include "Platform_Types.h"

/******************************************************************************/
/* TYPES                                                                      */
/******************************************************************************/

/*
 * CCC Parameter configuration structure
 */
typedef struct{
    /*comment: the CCC Parameter number                                       */
    uint16 u16ParaNumber;
    /*comment: all valid CCC parameter values                                 */
    const uint8* pu8ParaValues;
    /*comment: all valid CCC parameter values count                           */
    uint8  u8ParaValuesCount;
    /*comment: NVM position in block CCC_PARAMETERS1 and CCC_PARAMETERS2      */
    uint8 u8NvmPosition;
}VarM_tstrCccParaConfig;


/*
 * CCC Parameter configuration structure for each variant
 */
typedef struct
{
    /*comment: the valid CCC Parameter values for a variant                   */
    const uint8*   pu8ValidParaValues;
    /*comment: the valid CCC Parameter values count for a variant             */
    const uint8*   pu8ValidParaValuesCount;
    /*comment: the default CCC Parameter value for a variant                  */
    const uint8*   pu8DefaultValue;
    /*comment: Whether default value shall be used no matter any value are received*/
    const boolean* pbAlwaysUseDefValue;
}VarM_tstrCccParaVariantConfig;

typedef enum
{
    /*comment: The configuration output calculation is based on CCP           */
    VARM_CONFIG_OUTPUT_SRC_CCP = 1,
    /*comment: The configuration output calculation is based on PartNumber    */
    VARM_CONFIG_OUTPUT_SRC_PARTNUMBER = 2,
}VarM_tenuConfigOutputSrc;


/*
 *    Configuration output structure
 */
typedef struct
{
    /*comment: The pointer to the configuration variable                      */
    uint16* pu16ConfigOutput;
    /*comment: the source to calculate configuration output                   */
    VarM_tenuConfigOutputSrc enuConfigOutputSrc;
    /*comment: The Index to calculate configuration output                    */
    uint8   u8CcpIndex;
    /*comment: The configuration output map array                             */
    const uint8*  pu8OutputValArray;
}VarM_tstrCcpOutputConfig;

/******************************************************************************/
/* CONSTANTS, MACROS                                                          */
/******************************************************************************/

#define VARM_CCP_INVALID_VALUE                                           (uint8)(0u)

%CONST%


/******************************************************************************/
/* PUBLIC VARIABLES                                                           */
/******************************************************************************/
%PUBLIC_VARIABLE%


/******************************************************************************/
/* PUBLIC FUNCTIONS                                                           */
/******************************************************************************/


#endif /* VARM_CCPCFG_H */

'''

def getVarM_CcpCfg_c_fileContext(FileName, CompName, Author, Date, IncludeFileList, ConstStr, TypeStr,CcpConfigStr, ConfigOutputStr):
    
    Context = VarM_CcpCfg_c_fileContext.replace("%PM%", FileName, 1)
    Context = Context.replace("<Component name>", CompName, 1)
    Context = Context.replace("<Module name>", CompName, 1)
    Context = Context.replace("%AUTHOR%", Author, 1)
    Context = Context.replace("%DATE%", Date, 1)
    Context = Context.replace("%CCP_CONFIGURATION%", CcpConfigStr, 1)
    Context = Context.replace("%CONFIGURATION_OUTPUT%", ConfigOutputStr, 1)
    
    
    includeFileStr = ""
    for file in IncludeFileList:
        includeFileStr += "#include \""+ file + "\"\n"
    
    Context = Context.replace("%INCLUDE%", includeFileStr, 1)
    
    return Context
    
def getVarM_CcpCfg_h_fileContext(FileName, CompName, Author, Date, IncludeFileList, ConstStr, TypeStr, PublicVariable):
    Context = VarM_CcpCfg_h_fileContext.replace("%PM%", FileName, 1)
    Context = Context.replace("<Component name>", CompName, 1)
    Context = Context.replace("<Module name>", CompName, 1)
    Context = Context.replace("%AUTHOR%", Author, 1)
    Context = Context.replace("%DATE%", Date, 1)
    Context = Context.replace("%CONST%", ConstStr, 1)

    includeFileStr = ""
    for file in IncludeFileList:
        includeFileStr += "#include \""+ file + "\"\n"
    
    Context = Context.replace("%INCLUDE%", includeFileStr, 1)
    
    Context = Context.replace("%PUBLIC_VARIABLE%", PublicVariable, 1)
    
    return Context