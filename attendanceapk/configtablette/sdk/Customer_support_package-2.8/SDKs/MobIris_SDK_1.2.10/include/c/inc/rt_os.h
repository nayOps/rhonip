// Protection against multiple inclusions
#ifndef MPH_RT_OS_H_705548_INCLUDED
#define MPH_RT_OS_H_705548_INCLUDED

#if defined(_MSC_VER) && (_MSC_VER > 1000) /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the same line" */
// Protection against multiple inclusions MSVC version. Provides speed-up in compilation
#pragma once
#endif

/* _BEGIN_FILE_HEADER_**********************************************************
*
*  PROJECT         :   URT_CommonTest
*
*  MODULE          :   URT_CommonTest
*
*  LANGUAGE        :   C
*
*  PORTABILITY     :   Windows 2000; Windows XP ; Linux ; 32/64bits
*
*  DESCRIPTION     :   Provide OS Macro
*
*  ENVIRONMENT     :   
*
*  MODIFICATIONS   :   
*      05/31/2011 Matthieu DARBOIS (G073678) - URT creation
*      mm/dd/yyyy modif_author_name modif description ...
*
************************************************************_FILE_HEADER_END_*/

// ____________________________BEGIN_INCLUDES_______________________________
// system includes:
// specific includes:
#include "rt_compiler.h"
#include "rt_platform.h"
// _____________________________INCLUDES_END________________________________

// _________________________BEGIN_DOCUMENTATION_____________________________

/** @defgroup os OS macros
 *  
 *  @{
 *
 * Macros defining OS (only one defined - except for cygwin) :
 * - RT_OS_WINDOWS : Windows
 * - RT_OS_LINUX : Linux (or Cygwin)
 * - RT_OS_LINUX_CYGWIN : Cygwin
 * - RT_OS_ANDROID : Android
 * - RT_OS_UNIX_RS6000 : AIX
 * - RT_OS_MACOS : Mac OS X 
 * - RT_OS_IOS : iOS 
 * - RT_OS_SOLARIS : SOLARIS
 * - RT_OS_INTEGRITY : Integrity RTOS
 * - RT_OS_UNKNOWN : Unknown OS
 * .
 *
 ** @} */

// __________________________DOCUMENTATION_END______________________________

// _____________________________BEGIN_MACROS________________________________
#if defined(_WIN32) || defined(_WIN64) // always set by compilers (MSVC, ICC, MING) under windows
#	define RT_OS_WINDOWS
#elif defined(__ANDROID__) || defined(ANDROID)
#	define RT_OS_ANDROID
#elif defined(__linux__) // defined by gcc for linux
#	define RT_OS_LINUX
#elif defined(__CYGWIN__)
#	define RT_OS_LINUX // to be compatible with current makefile
#	define RT_OS_LINUX_CYGWIN // Enhanced info if system related functionnality needs to be implemented
#elif defined(_AIX) || defined(__TOS_AIX__)
#	define RT_OS_UNIX_RS6000 // makefile coherence
#elif defined(__APPLE__) && defined(__MACH__)
#	if defined(__ENVIRONMENT_IPHONE_OS_VERSION_MIN_REQUIRED__)
#		define RT_OS_IOS // for iOS
#	elif defined(__ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__)
#		define RT_OS_MACOS // for OS X
#	else
#		define RT_OS_UNKNOWN
#	endif
#elif defined(sun) || defined(__sun)
#	define RT_OS_SOLARIS
//#		if defined(__SVR4) || defined(__svr4__)
//#			define RT_OS_SOLARIS
//#		else
//#			define RT_OS_SUNOS
//#		endif
#elif defined(RT_OS_MORPHO_CBM)
//#	define RT_OS_MORPHO_CBM
#	if !(defined(RT_COMPILER_ARMCC) && defined(RT_PLATFORM_ARM))
#		error OS_CONFIGURATION_ERROR_CBM
#	endif
#elif defined(RT_OS_MORPHO_NEMO)
//#	define RT_OS_MORPHO_NEMO
#	if !(defined(RT_COMPILER_GCC) && defined(RT_PLATFORM_ARM))
#		error OS_CONFIGURATION_ERROR_NEMO
#	endif
#elif defined(RT_OS_TEE)
//#	define RT_OS_TEE
#elif defined(EMSCRIPTEN)
# define RT_OS_BROWSER
#elif defined(__INTEGRITY)
# define RT_OS_INTEGRITY
#else
#	define RT_OS_UNKNOWN
#endif
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
#endif // !defined(MPH_RT_OS_H_705548_INCLUDED)
