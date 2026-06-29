// Protection against multiple inclusions
#ifndef MPH_RT_ATTRIBUTES_H_705548_INCLUDED
#define MPH_RT_ATTRIBUTES_H_705548_INCLUDED

#if defined(_MSC_VER) && (_MSC_VER > 1000) /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the same line" */
// Protection against multiple inclusions MSVC version. Provides speed-up in compilation
#	pragma once
#endif

/* _BEGIN_FILE_HEADER_**********************************************************
*
*  PROJECT         :   URT Common Headers
*
*  MODULE          :   Miscellaneous Files
*
*  LANGUAGE        :   C
*
*  PORTABILITY     :   Windows 2000; Windows XP ; Linux ; 32/64bits
*
*  DESCRIPTION     :   Provides attributes macros for different compilers
*
*  ENVIRONMENT     :   
*
*  MODIFICATIONS   :   
*      05/30/2011 Matthieu DARBOIS (G073678) - URT creation
*      mm/dd/yyyy modif_author_name modif description ...
*
************************************************************_FILE_HEADER_END_*/

// ____________________________BEGIN_INCLUDES_______________________________
// system includes:
// specific includes:
#include "rt_compiler.h"
#include "rt_os.h"
// _____________________________INCLUDES_END________________________________

// _________________________BEGIN_DOCUMENTATION_____________________________

/** @defgroup attributes Attributes macros
 *  
 *  @{
 *
 * Macros defining attributes :
 * - RT_ATTRIBUTE_FORCELINE : Tells the compiler to always inline the function
 * - RT_ATTRIBUTE_DEPRECATED : Tells the compiler the function is deprecated
 * .
 *
 ** @} */

// __________________________DOCUMENTATION_END______________________________

// _____________________________BEGIN_MACROS________________________________

#if defined(RT_OS_INTEGRITY)
#	define RT_ATTRIBUTE_FORCELINE inline
#	define RT_ATTRIBUTE_DEPRECATED __attribute__((deprecated))
#	define RT_ATTRIBUTE_PUBLIC
#	define RT_ATTRIBUTE_HIDDEN
#	define RT_ATTRIBUTE_STATIC_TPL_SPEC static
#	define RT_ATTRIBUTE_MAY_BE_UNUSED __attribute__ ((unused))
#elif defined(RT_COMPILER_MSVC) // including ICC in MSVC compatibility mode
#	define RT_ATTRIBUTE_FORCELINE __forceinline
#	if RT_COMPILER_MSVC_AT_LEAST_VC7 
#		define RT_ATTRIBUTE_DEPRECATED __declspec(deprecated) /* parasoft-suppress  MISRA2004-19_4_mod "attribute macro should not be enclosed in parentheses" */
#	else
#		define RT_ATTRIBUTE_DEPRECATED
#	endif
#	define RT_ATTRIBUTE_PUBLIC 
#	define RT_ATTRIBUTE_HIDDEN  
#	define RT_ATTRIBUTE_STATIC_TPL_SPEC static
#	define RT_ATTRIBUTE_MAY_BE_UNUSED
#elif defined(RT_COMPILER_GCC) || defined (RT_COMPILER_EMCC) // GCC including ICC in GCC compatibility mode
#	if defined(__NO_INLINE__)
#		define RT_ATTRIBUTE_FORCELINE
#	else
#		define RT_ATTRIBUTE_FORCELINE __inline__ __attribute__((always_inline)) /* parasoft-suppress  MISRA2004-19_4_mod "attribute macro should not be enclosed in parentheses" */
#	endif
#	define RT_ATTRIBUTE_DEPRECATED __attribute__((__deprecated__)) /* parasoft-suppress  MISRA2004-19_4_mod "attribute macro should not be enclosed in parentheses" */
#	if (RT_COMPILER_GCC_AT_LEAST(4,0) || defined (RT_COMPILER_EMCC)) && !defined(RT_OS_LINUX_CYGWIN)
#		define RT_ATTRIBUTE_PUBLIC __attribute__ ((visibility ("default")))
#		define RT_ATTRIBUTE_HIDDEN __attribute__ ((visibility ("hidden")))
#	else
#		define RT_ATTRIBUTE_PUBLIC 
#		define RT_ATTRIBUTE_HIDDEN 
#	endif
#	if (RT_COMPILER_GCC_AT_LEAST(4,3) || ((defined(RT_OS_MACOS) || defined(RT_OS_IOS) || defined(RT_OS_BROWSER)) && defined(RT_COMPILER_CLANG) && RT_COMPILER_GCC_AT_LEAST(4,2)))
#		define RT_ATTRIBUTE_STATIC_TPL_SPEC
#	else
#		define RT_ATTRIBUTE_STATIC_TPL_SPEC static
#	endif
#	define RT_ATTRIBUTE_MAY_BE_UNUSED __attribute__ ((unused))
#elif defined(RT_COMPILER_ARMCC)
#	if __ARMCC_VERSION >= 400000
#		define RT_ATTRIBUTE_FORCELINE __forceinline
#	else
#		define RT_ATTRIBUTE_FORCELINE __inline
#	endif
#	define RT_ATTRIBUTE_DEPRECATED
#	define RT_ATTRIBUTE_PUBLIC 
#	define RT_ATTRIBUTE_HIDDEN 
#	define RT_ATTRIBUTE_STATIC_TPL_SPEC static
#	define RT_ATTRIBUTE_MAY_BE_UNUSED
#else
#	error This compiler is not supported
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

// ________________________BEGIN_CLASS_DEFINITIONS__________________________

// _________________________CLASS_DECLARATION_END___________________________

// End of protection against multiple inclusions
#endif // !defined(MPH_RT_ATTRIBUTES_H_705548_INCLUDED)
