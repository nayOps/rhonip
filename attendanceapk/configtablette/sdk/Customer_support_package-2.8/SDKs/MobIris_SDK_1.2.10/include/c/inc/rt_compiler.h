// Protection against multiple inclusions
#ifndef MPH_RT_COMPILER_H_705548_INCLUDED
#define MPH_RT_COMPILER_H_705548_INCLUDED

#if defined(_MSC_VER) && (_MSC_VER > 1000) /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the same line" */
// Protection against multiple inclusions MSVC version. Provides speed-up in compilation
#	pragma once
#endif

/* _BEGIN_FILE_HEADER_**********************************************************
*
*  PROJECT         :   URT Common Headers
*
*  MODULE          :   Compiler identification macros
*
*  LANGUAGE        :   C
*
*  PORTABILITY     :   Windows 2000; Windows XP ; Linux ; 32/64bits
*
*  DESCRIPTION     :   
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

/** @defgroup compiler Compiler macros
 *  
 *  @{
 */

// _____________________________INCLUDES_END________________________________

// _____________________________BEGIN_MACROS________________________________

#if defined(_MSC_VER)
#	define RT_COMPILER_MSVC
#elif defined(__GNUC__)
# if defined(EMSCRIPTEN)
#  define RT_COMPILER_EMCC
# else
#	 define RT_COMPILER_GCC
# endif
#elif defined(__INTEGRITY)
#	define RT_COMPILER_GCC
#elif defined(__ARMCC_VERSION)
#	define RT_COMPILER_ARMCC
#else
#	define RT_COMPILER_UNKNOWN
#endif

#if defined(__INTEL_COMPILER) //Intel compiler set separately to reflect MSVC/GCC compatibility
#	define RT_COMPILER_ICC
#endif

#if defined(__clang__) // clang compiler set separately to reflect GCC compatibility
#	define RT_COMPILER_CLANG
#if defined(__epona__)
#	define RT_COMPILER_EPONA
#endif
#endif

/** \brief Macro to check GCC version
  *
  * @param[in] major Major version to check
  * @param[in] minor Minor version to check
  *
  * \warning Intel Compiler also acts as if it was a GCC compiler.
  */
#define RT_COMPILER_GCC_AT_LEAST(major, minor)   (defined(__GNUC__) && (__GNUC__ > (major) || __GNUC__ == (major) && __GNUC_MINOR__ >= (minor)))

/** \brief Macro to check Intel Compiler version
  *
  * @param[in] major Major version to check
  * @param[in] minor Minor version to check
  */
#define RT_COMPILER_ICC_AT_LEAST(major, minor) (defined(__INTEL_COMPILER) && (__INTEL_COMPILER >= (((major) * 10 + (minor))*10)))

/** \brief Set to 1 when compiler is Microsoft Visual C 6.0 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC6 0

/** \brief Set to 1 when compiler is Microsoft Visual C 7.0 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC7 0

/** \brief Set to 1 when compiler is Microsoft Visual C 7.1 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC71 0

/** \brief Set to 1 when compiler is Microsoft Visual C 8.0 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC8 0

/** \brief Set to 1 when compiler is Microsoft Visual C 9.0 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC9 0

/** \brief Set to 1 when compiler is Microsoft Visual C 9.0 RTM or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC9_RTM 0

/** \brief Set to 1 when compiler is Microsoft Visual C 9.0 SP1 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC9_SP1 0

/** \brief Set to 1 when compiler is Microsoft Visual C 10.0 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC10 0

/** \brief Set to 1 when compiler is Microsoft Visual C 10.0 RTM or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC10_RTM 0

/** \brief Set to 1 when compiler is Microsoft Visual C 10.0 SP1 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC10_SP1 0

/** \brief Set to 1 when compiler is Microsoft Visual C 11.0 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC11 0

/** \brief Set to 1 when compiler is Microsoft Visual C 11.0 RTM or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC11_RTM 0

/** \brief Set to 1 when compiler is Microsoft Visual C 11.0 U1 CTP or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC11_U1_CTP 0

/** \brief Set to 1 when compiler is Microsoft Visual C 11.0 U1 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC11_U1 0

/** \brief Set to 1 when compiler is Microsoft Visual C 11.0 U4 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC11_U4 0

/** \brief Set to 1 when compiler is Microsoft Visual C 12.0 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC12 0

/** \brief Set to 1 when compiler is Microsoft Visual C 12.0 U1 or newer. 0 otherwise.
  *
  * \warning Intel Compiler also acts as if it was a MSVC compiler.
  */
#define RT_COMPILER_MSVC_AT_LEAST_VC12_U1 0

/** \brief Set to 1 when compiler is Microsoft Visual C 12.0 U3 or newer. 0 otherwise.
*
* \warning Intel Compiler also acts as if it was a MSVC compiler.
*/
#define RT_COMPILER_MSVC_AT_LEAST_VC12_U3 0

/** \brief Set to 1 when compiler is Microsoft Visual C 12.0 U4 or newer. 0 otherwise.
*
* \warning Intel Compiler also acts as if it was a MSVC compiler.
*/
#define RT_COMPILER_MSVC_AT_LEAST_VC12_U4 0

/** \brief Set to 1 when compiler is Microsoft Visual C 12.0 U5 or newer. 0 otherwise.
*
* \warning Intel Compiler also acts as if it was a MSVC compiler.
*/
#define RT_COMPILER_MSVC_AT_LEAST_VC12_U5 0

/** \brief Set to 1 when compiler is Microsoft Visual C 14.0 or newer. 0 otherwise.
*
* \warning Intel Compiler also acts as if it was a MSVC compiler.
*/
#define RT_COMPILER_MSVC_AT_LEAST_VC14 0

/** \brief Set to 1 when compiler is Microsoft Visual C 14.0 U3 or newer. 0 otherwise.
*
* \warning Intel Compiler also acts as if it was a MSVC compiler.
*/
#define RT_COMPILER_MSVC_AT_LEAST_VC14_U3 0

#ifdef _MSC_VER
#	if _MSC_VER >= 1200
#		undef RT_COMPILER_MSVC_AT_LEAST_VC6
#		define RT_COMPILER_MSVC_AT_LEAST_VC6 1
#	endif
#	if _MSC_VER >= 1300 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC7
#		define RT_COMPILER_MSVC_AT_LEAST_VC7 1
#	endif
#	if _MSC_VER >= 1310 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC71
#		define RT_COMPILER_MSVC_AT_LEAST_VC71 1
#	endif
#	if _MSC_VER >= 1400 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC8
#		define RT_COMPILER_MSVC_AT_LEAST_VC8 1
#	endif
#	if _MSC_VER >= 1500 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC9
#		define RT_COMPILER_MSVC_AT_LEAST_VC9 1
#	endif
#	if ((_MSC_VER > 1500) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 150021022) || ((_MSC_FULL_VER == 150021022) && (_MSC_BUILD >= 8))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC9_RTM
#		define RT_COMPILER_MSVC_AT_LEAST_VC9_RTM 1
#	endif
#	if ((_MSC_VER > 1500) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 150030729) || ((_MSC_FULL_VER == 150030729) && (_MSC_BUILD >= 1))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC9_SP1
#		define RT_COMPILER_MSVC_AT_LEAST_VC9_SP1 1
#	endif
#	if _MSC_VER >= 1600 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC10
#		define RT_COMPILER_MSVC_AT_LEAST_VC10 1
#	endif
#	if ((_MSC_VER > 1600) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 160030319) || ((_MSC_FULL_VER == 160030319) && (_MSC_BUILD >= 1))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC10_RTM
#		define RT_COMPILER_MSVC_AT_LEAST_VC10_RTM 1
#	endif
#	if ((_MSC_VER > 1600) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 160040219) || ((_MSC_FULL_VER == 160040219) && (_MSC_BUILD >= 1))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC10_SP1
#		define RT_COMPILER_MSVC_AT_LEAST_VC10_SP1 1
#	endif
#	if _MSC_VER >= 1700 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC11
#		define RT_COMPILER_MSVC_AT_LEAST_VC11 1
#	endif
#	if ((_MSC_VER > 1700) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 170050727) || ((_MSC_FULL_VER == 170050727) && (_MSC_BUILD >= 1))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC11_RTM
#		define RT_COMPILER_MSVC_AT_LEAST_VC11_RTM 1
#	endif
#	if ((_MSC_VER > 1700) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 170051020) || ((_MSC_FULL_VER == 170051020) && (_MSC_BUILD >= 1))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC11_U1_CTP
#		define RT_COMPILER_MSVC_AT_LEAST_VC11_U1_CTP 1
#	endif
#	if ((_MSC_VER > 1700) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 170051106) || ((_MSC_FULL_VER == 170051106) && (_MSC_BUILD >= 1))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC11_U1
#		define RT_COMPILER_MSVC_AT_LEAST_VC11_U1 1
#	endif
#	if ((_MSC_VER > 1700) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 170061030) || ((_MSC_FULL_VER == 170061030) && (_MSC_BUILD >= 0))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC11_U4
#		define RT_COMPILER_MSVC_AT_LEAST_VC11_U4 1
#	endif
#	if _MSC_VER >= 1800 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC12
#		define RT_COMPILER_MSVC_AT_LEAST_VC12 1
#	endif
#	if ((_MSC_VER > 1800) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 180021005) || ((_MSC_FULL_VER == 180021005) && (_MSC_BUILD >= 1))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC12_U1
#		define RT_COMPILER_MSVC_AT_LEAST_VC12_U1 1
#	endif
#	if ((_MSC_VER > 1800) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 180030723) || ((_MSC_FULL_VER == 180030723) && (_MSC_BUILD >= 0))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC12_U3
#		define RT_COMPILER_MSVC_AT_LEAST_VC12_U3 1
#	endif
#	if ((_MSC_VER > 1800) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 180031101) || ((_MSC_FULL_VER == 180031101) && (_MSC_BUILD >= 0))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC12_U4
#		define RT_COMPILER_MSVC_AT_LEAST_VC12_U4 1
#	endif
#	if ((_MSC_VER > 1800) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 180040629) || ((_MSC_FULL_VER == 180040629) && (_MSC_BUILD >= 0))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC12_U5
#		define RT_COMPILER_MSVC_AT_LEAST_VC12_U5 1
#	endif
#	if ((_MSC_VER >= 1900)) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC14
#		define RT_COMPILER_MSVC_AT_LEAST_VC14 1
#	endif
#	if ((_MSC_VER > 1900) || (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && ((_MSC_FULL_VER > 190024210) || ((_MSC_FULL_VER == 190024210) && (_MSC_BUILD >= 0))))) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		undef RT_COMPILER_MSVC_AT_LEAST_VC14_U3
#		define RT_COMPILER_MSVC_AT_LEAST_VC14_U3 1
#	endif
#endif

#if defined (__INTEL_COMPILER)
#	if __INTEL_COMPILER == 910
#		define RT_COMPILER_NAME "Intel Compiler 9.1"
#		define RT_COMPILER_SHORTNAME "icc9.1"
#	elif __INTEL_COMPILER == 1010
#		define RT_COMPILER_NAME "Intel Compiler 10.1"
#		define RT_COMPILER_SHORTNAME "icc10.1"
#	elif __INTEL_COMPILER == 1100
#		define RT_COMPILER_NAME "Intel Compiler 11.0"
#		define RT_COMPILER_SHORTNAME "icc11.0"
#	elif __INTEL_COMPILER == 1110
#		define RT_COMPILER_NAME "Intel Compiler 11.1"
#		define RT_COMPILER_SHORTNAME "icc11.1"
#	else
#		define RT_COMPILER_NAME "Intel Compiler"
#		define RT_COMPILER_SHORTNAME "icc"
// Message to inform the developer
#		pragma message("Unknown Intel compiler version. Please update RT_Headers or request support for this version")
#	endif
#elif defined(_MSC_VER)
#	if _MSC_VER == 1200 /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the surrounding block" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 6.0"
#		define RT_COMPILER_SHORTNAME "vc6"
#	elif _MSC_VER == 1300
#		define RT_COMPILER_NAME "Microsoft Visual C++ 7.0"
#		define RT_COMPILER_SHORTNAME "vc70"
#	elif _MSC_VER == 1310
#		define RT_COMPILER_NAME "Microsoft Visual C++ 7.1"
#		define RT_COMPILER_SHORTNAME "vc7"
#	elif _MSC_VER == 1400
#		define RT_COMPILER_NAME "Microsoft Visual C++ 8.0"
#		define RT_COMPILER_SHORTNAME "vc8"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 150021022 && _MSC_BUILD == 8) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 9.0 RTM"
#		define RT_COMPILER_SHORTNAME "vc9rtm"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 150030729 && _MSC_BUILD == 1) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 9.0 SP1"
#		define RT_COMPILER_SHORTNAME "vc9sp1"
#	elif _MSC_VER == 1500
#		define RT_COMPILER_NAME "Microsoft Visual C++ 9.0"
#		define RT_COMPILER_SHORTNAME "vc9"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 160030319 && _MSC_BUILD == 1) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 10.0 RTM"
#		define RT_COMPILER_SHORTNAME "vc10rtm"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 160040219 && _MSC_BUILD == 1) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 10.0 SP1"
#		define RT_COMPILER_SHORTNAME "vc10sp1"
#	elif _MSC_VER == 1600
#		define RT_COMPILER_NAME "Microsoft Visual C++ 10.0"
#		define RT_COMPILER_SHORTNAME "vc10"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 170050727 && _MSC_BUILD == 1) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 11.0 RTM"
#		define RT_COMPILER_SHORTNAME "vc11rtm"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 170051106 && _MSC_BUILD == 1) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 11.0 Update 1"
#		define RT_COMPILER_SHORTNAME "vc11u1"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 170061030 && _MSC_BUILD == 0) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 11.0 Update 4"
#		define RT_COMPILER_SHORTNAME "vc11u4"
#	elif _MSC_VER == 1700
#		define RT_COMPILER_NAME "Microsoft Visual C++ 11.0"
#		define RT_COMPILER_SHORTNAME "vc11"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 180021005 && _MSC_BUILD == 1) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 12.0 Update 1"
#		define RT_COMPILER_SHORTNAME "vc12u1"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 180030723 && _MSC_BUILD == 0) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 12.0 Update 3"
#		define RT_COMPILER_SHORTNAME "vc12u3"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) &&_MSC_FULL_VER == 180031101 && _MSC_BUILD == 0) /* parasoft-suppress  MISRA2004-19_11 "macros existence checked in the same line" */
#		define RT_COMPILER_NAME "Microsoft Visual C++ 12.0 Update 4"
#		define RT_COMPILER_SHORTNAME "vc12u4"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) &&_MSC_FULL_VER == 180040629 && _MSC_BUILD == 0)
#		define RT_COMPILER_NAME "Microsoft Visual C++ 12.0 Update 5"
#		define RT_COMPILER_SHORTNAME "vc12u5"
#	elif _MSC_VER == 1800
#		define RT_COMPILER_NAME "Microsoft Visual C++ 12.0"
#		define RT_COMPILER_SHORTNAME "vc12"
#	elif (defined(_MSC_FULL_VER) && defined(_MSC_BUILD) && _MSC_FULL_VER == 190024210 && _MSC_BUILD == 0)
#		define RT_COMPILER_NAME "Microsoft Visual C++ 14.0 Update 3"
#		define RT_COMPILER_SHORTNAME "vc14u3"
#	elif _MSC_VER == 1900
#		define RT_COMPILER_NAME "Microsoft Visual C++ 14.0"
#		define RT_COMPILER_SHORTNAME "vc14"
#	else
#		define RT_COMPILER_NAME "Microsoft Visual C++"
#		define RT_COMPILER_SHORTNAME "vc"
// Message to inform the developer
#		pragma message("Unknown Microsoft compiler version. Please update RT_Headers or request support for this version")
#	endif
#elif defined(__clang__)
#	define LOCAL_RT_COMPILER_STR2(a) #a
#	define LOCAL_RT_COMPILER_STR(a) LOCAL_RT_COMPILER_STR2(a)
// JFM : for epona we should check __VERSION__ to have the real version number
#	if defined(__clang_version__)
#		define RT_COMPILER_NAME "clang " __clang_version__ /* parasoft-suppress  MISRA2004-19_4_mod "constant string needs to be defined without parentheses" */
#	elif defined(__clang_patchlevel__)
#		define RT_COMPILER_NAME "clang " LOCAL_RT_COMPILER_STR(__clang_major__) "." LOCAL_RT_COMPILER_STR(__clang_minor__) "." LOCAL_RT_COMPILER_STR(__clang_patchlevel__) /* parasoft-suppress  MISRA2004-19_4_mod "constant string needs to be defined without parentheses" */ /* parasoft-suppress  MISRA2004-19_13 "# operator works with GCC, ICC, MSVC" */ /* parasoft-suppress  MISRA2004-19_12 "# operator works with ICC, GCC, MSVC" */
#	else
#		define RT_COMPILER_NAME "clang " LOCAL_RT_COMPILER_STR(__clang_major__) "." LOCAL_RT_COMPILER_STR(__clang_minor__) /* parasoft-suppress  MISRA2004-19_4_mod "constant string needs to be defined without parentheses" */ /* parasoft-suppress  MISRA2004-19_13 "# operator works with GCC, ICC, MSVC" */ /* parasoft-suppress  MISRA2004-19_12 "# operator works with ICC, GCC, MSVC" */
#	endif
#	if defined(__clang_patchlevel__)
#		define RT_COMPILER_SHORTNAME "clang" LOCAL_RT_COMPILER_STR(__clang_major__) "." LOCAL_RT_COMPILER_STR(__clang_minor__) "." LOCAL_RT_COMPILER_STR(__clang_patchlevel__)
#	else
#		define RT_COMPILER_SHORTNAME "clang" LOCAL_RT_COMPILER_STR(__clang_major__) "." LOCAL_RT_COMPILER_STR(__clang_minor__)
#	endif
#elif defined(__GNUC__)
#	define LOCAL_RT_COMPILER_STR2(a) #a
#	define LOCAL_RT_COMPILER_STR(a) LOCAL_RT_COMPILER_STR2(a)
#	if defined(__VERSION__)
#		define RT_COMPILER_NAME "GCC " __VERSION__ /* parasoft-suppress  MISRA2004-19_4_mod "constant string needs to be defined without parentheses" */
#	elif defined(__GNUC_PATCHLEVEL__)
#		define RT_COMPILER_NAME "GCC " LOCAL_RT_COMPILER_STR(__GNUC__) "." LOCAL_RT_COMPILER_STR(__GNUC_MINOR__) "." LOCAL_RT_COMPILER_STR(__GNUC_PATCHLEVEL__) /* parasoft-suppress  MISRA2004-19_4_mod "constant string needs to be defined without parentheses" */ /* parasoft-suppress  MISRA2004-19_13 "# operator works with GCC, ICC, MSVC" */ /* parasoft-suppress  MISRA2004-19_12 "# operator works with ICC, GCC, MSVC" */
#	else
#		define RT_COMPILER_NAME "GCC " LOCAL_RT_COMPILER_STR(__GNUC__) "." LOCAL_RT_COMPILER_STR(__GNUC_MINOR__) /* parasoft-suppress  MISRA2004-19_4_mod "constant string needs to be defined without parentheses" */ /* parasoft-suppress  MISRA2004-19_13 "# operator works with GCC, ICC, MSVC" */ /* parasoft-suppress  MISRA2004-19_12 "# operator works with ICC, GCC, MSVC" */
#	endif
#	if defined(__GNUC_PATCHLEVEL__)
#		define RT_COMPILER_SHORTNAME "gcc" LOCAL_RT_COMPILER_STR(__GNUC__) "." LOCAL_RT_COMPILER_STR(__GNUC_MINOR__) "." LOCAL_RT_COMPILER_STR(__GNUC_PATCHLEVEL__)
#	else
#		define RT_COMPILER_SHORTNAME "gcc" LOCAL_RT_COMPILER_STR(__GNUC__) "." LOCAL_RT_COMPILER_STR(__GNUC_MINOR__)
#	endif
#elif defined(__ARMCC_VERSION)
#	define LOCAL_RT_COMPILER_STR2(a) #a
#	define LOCAL_RT_COMPILER_STR(a) LOCAL_RT_COMPILER_STR2(a)
#	if __ARMCC_VERSION >= 100000 && __ARMCC_VERSION < 200000
#		if __ARMCC_VERSION < 110000
#			if __ARMCC_VERSION==100156
#				define RT_COMPILER_NAME "ARMCC 1.0.0.156"
#			else
#				define RT_COMPILER_NAME "ARMCC 1.0 (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#			endif
#		elif __ARMCC_VERSION < 120000
#			define RT_COMPILER_NAME "ARMCC 1.1 (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#		elif __ARMCC_VERSION < 130000
#			define RT_COMPILER_NAME "ARMCC 1.2 (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#		elif __ARMCC_VERSION < 140000
#			define RT_COMPILER_NAME "ARMCC 1.3 (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#		else
#			define RT_COMPILER_NAME "ARMCC 1.x (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#		endif
#	elif __ARMCC_VERSION >= 400000 && __ARMCC_VERSION < 500000
#		if __ARMCC_VERSION < 410000
#			if __ARMCC_VERSION==400400
#				define RT_COMPILER_NAME "ARMCC 4.0.0.400"
#			else
#				define RT_COMPILER_NAME "ARMCC 4.0 (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#			endif
#		elif __ARMCC_VERSION < 420000
#			define RT_COMPILER_NAME "ARMCC 4.1 (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#		else
#			define RT_COMPILER_NAME "ARMCC 4.x (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#		endif
#	else
#		define RT_COMPILER_NAME "Unknown ARMCC version (" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION) ")"
#	endif
#	define RT_COMPILER_SHORTNAME "armcc" LOCAL_RT_COMPILER_STR(__ARMCC_VERSION)
#else
/** \brief Get the compiler name string  */
#	define RT_COMPILER_NAME "Unknown compiler"
#	define RT_COMPILER_SHORTNAME "unk"
// Message to inform the developer
#	pragma message("Unknown compiler. Please update RT_Headers or request support for this compiler")
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

/** @} */ // end of mutex

// End of protection against multiple inclusions
#endif // !defined(MPH_RT_COMPILER_H_705548_INCLUDED)
