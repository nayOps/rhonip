// Protection against multiple inclusions
#ifndef MPH_RT_VERSION_H_705548_INCLUDED
#define MPH_RT_VERSION_H_705548_INCLUDED

#if defined(_MSC_VER) && (_MSC_VER > 1000) /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked on the same line" */
// Protection against multiple inclusions MSVC version, provides speed-up in compilation
#	pragma once
#endif

/* _BEGIN_FILE_HEADER_**********************************************************
*
*  PROJECT         :   URT Common Headers
*
*  MODULE          :   Version identifier
*
*  LANGUAGE        :   C
*
*  PORTABILITY     :   Windows 2000; Windows XP; Linux ; 32/64bits
*
*  DESCRIPTION     :   
*
*  ENVIRONMENT     :   
*
*  MODIFICATIONS   :   
*      04/19/2010 Matthieu DARBOIS (G073678) - URT creation
*      mm/dd/yyyy modif_author_name modif description ...
*
************************************************************_FILE_HEADER_END_*/

// ____________________________BEGIN_INCLUDES_______________________________
// system includes:
// specific includes:
#include "rt_svnrevision.h"
// _____________________________INCLUDES_END________________________________

// _____________________________BEGIN_MACROS________________________________
#define RT_VERSION_STRINGIFY2(arg) #arg /* parasoft-suppress  MISRA2004-19_13 "# operator works with ICC, GCC, MSVC" */ /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
#define RT_VERSION_STRINGIFY(arg) RT_VERSION_STRINGIFY2(arg) /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */

#define RT_MAJOR_VERSION 1
#define RT_MINOR_VERSION 19
#define RT_PATCH_VERSION 0

#ifdef _DEBUG
#	ifdef RT_SVN_NEED_UPDATE
#		define RT_BUILD_VERSION2(x) 30##x /* parasoft-suppress  MISRA2004-19_13 "# operator works with ICC, GCC, MSVC" */ /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
#	else
#		define RT_BUILD_VERSION2(x) 10##x /* parasoft-suppress  MISRA2004-19_13 "# operator works with ICC, GCC, MSVC" */ /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
#	endif
#else
#	ifdef RT_SVN_NEED_UPDATE
#		define RT_BUILD_VERSION2(x) 20##x /* parasoft-suppress  MISRA2004-19_13 "# operator works with ICC, GCC, MSVC" */ /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
#	else
#		define RT_BUILD_VERSION2(x) x     /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */ /* parasoft-suppress  MISRA2004-19_10 "x Need not to be enclosed in parentheses to work" */
#	endif
#endif
#define RT_BUILD_VERSION3(x) RT_BUILD_VERSION2(x) /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
#define RT_BUILD_VERSION RT_BUILD_VERSION3(RT_PATCH_VERSION) /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */

#define RT_MAJOR_VERSION_STR RT_VERSION_STRINGIFY(RT_MAJOR_VERSION) /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
#define RT_MINOR_VERSION_STR RT_VERSION_STRINGIFY(RT_MINOR_VERSION) /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
#define RT_BUILD_VERSION_STR RT_VERSION_STRINGIFY(RT_BUILD_VERSION) /* parasoft-suppress  MISRA2004-19_4_mod "Need not to be enclosed in parentheses to work" */
// ______________________________MACROS_END_________________________________

// ____________________________BEGIN_CONSTANTS______________________________
// _____________________________CONSTANTS_END_______________________________

// ______________________________BEGIN_TYPES________________________________
// _______________________________TYPES_END_________________________________

// ___________________BEGIN_GLOBAL_VARIABLES_DEFINITIONS____________________
// ____________________GLOBAL_VARIABLES_DEFINITIONS_END_____________________

// ______________________BEGIN_FUNCTIONS_DEFINITIONS________________________

// _______________________FUNCTIONS_DEFINITIONS_END_________________________

// End of protection against multiple inclusions
#endif // !defined(MPH_RT_VERSION_H_705548_INCLUDED)
