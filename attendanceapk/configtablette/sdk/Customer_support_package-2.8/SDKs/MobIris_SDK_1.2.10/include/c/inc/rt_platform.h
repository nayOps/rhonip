// Protection against multiple inclusions
#ifndef MPH_RT_PLATFORM_H_705548_INCLUDED
#define MPH_RT_PLATFORM_H_705548_INCLUDED

#if defined(_MSC_VER) && (_MSC_VER > 1000) /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the same line" */
// Protection against multiple inclusions MSVC version. Provides speed-up in compilation
#pragma once
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
*  DESCRIPTION     :   Provides platform/endianess macros for different compilers
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

#ifdef __cplusplus
extern "C" {
#endif
// _____________________________INCLUDES_END________________________________

// _________________________BEGIN_DOCUMENTATION_____________________________

/** @defgroup platform Platform macros, types & functions
 *  
 *  @{
 *
 * Macros defining CPU architecture (only one is defined) :
 * - RT_PLATFORM_X86   : Defined for x86/x86-64 processor in 32bits mode
 * - RT_PLATFORM_X64   : Defined for x86-64 in 64bits mode
 * - RT_PLATFORM_IA64  : Defined for Itanium processor
 * - RT_PLATFORM_ARM   : Defined for ARM
 * - RT_PLATFORM_ARM64 : Defined for ARM64
 * - RT_PLATFORM_PPC64 : Defined for PPC64
 * .
 *
 * Macros defining CPU endianness (only one is defined) :
 * - RT_ENDIANNESS_LE : Defined for little endian
 * - RT_ENDIANNESS_BE : Defined for big endian
 *
 */

// __________________________DOCUMENTATION_END______________________________

// _____________________________BEGIN_MACROS________________________________
#if defined(RT_COMPILER_MSVC)
#	if defined(_M_IX86) && !defined(_M_X64)
#		define RT_PLATFORM_X86
#	elif defined(_M_X64)
#		define RT_PLATFORM_X64
#	elif defined(_M_IA64)
#		define RT_PLATFORM_IA64
#	elif defined(_M_ARM)
#		define RT_PLATFORM_ARM
#	else
#		define RT_PLATFORM_UNKNOWN
#	endif
#elif defined(RT_COMPILER_GCC)
#	if defined(i386) || defined(__i386__)
#		define RT_PLATFORM_X86
#	elif defined(__x86_64) || defined(__x86_64__) || defined(__amd64) || defined(__amd64__)
#		define RT_PLATFORM_X64
#	elif defined(__ia64__) || defined(__IA64__) || defined(_IA64)
#		define RT_PLATFORM_IA64
#	elif defined(__AARCH64EL__) || defined(__AARCH64EB__) || defined(__aarch64__) || defined(__arm64) || defined(__arm64__)
#		define RT_PLATFORM_ARM64
#	elif defined(__ARM_EABI__) || defined(__ARMEL__) || defined(__ARMEB__) || defined(__ARMv7__)
//#		if defined(__ARM_ARCH_7A__)
#		define RT_PLATFORM_ARM
//#		else
//#			define RT_PLATFORM_ARM_UNKNOWN
//#		endif
#	elif defined(__PPC64__) || defined(__powerpc64__)
#		define RT_PLATFORM_PPC64
#	else
#		define RT_PLATFORM_UNKNOWN
#	endif
//#elif defined (RT_COMPILER_IBMC) //__IBMC__
//#	define RT_PLATFORM_UNKNOWN
#elif defined(RT_COMPILER_ARMCC)
#	define RT_PLATFORM_ARM
#elif defined(RT_COMPILER_EMCC)
# define RT_PLATFORM_UNKNOWN
# define RT_ENDIANNESS_LE
#else
#	define RT_PLATFORM_UNKNOWN
#endif

#if   defined(RT_PLATFORM_X86)
#	define RT_ENDIANNESS_LE
#elif defined(RT_PLATFORM_X64)
#	define RT_ENDIANNESS_LE
#elif defined(RT_PLATFORM_ARM) || defined(RT_PLATFORM_ARM64)
#	if defined(__ARMEB__) || defined(__AARCH64EB__) || (defined(__BYTE_ORDER__) && defined(__ORDER_BIG_ENDIAN__) && (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)) || defined(__BIG_ENDIAN__)
#		define RT_ENDIANNESS_BE
#	elif defined(__ARMEL__) || defined(__AARCH64EL__) || (defined(__BYTE_ORDER__) && defined(__ORDER_LITTLE_ENDIAN__) && (__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__)) || defined(__LITTLE_ENDIAN__)
#		define RT_ENDIANNESS_LE
#	elif defined(RT_COMPILER_MSVC)
#		define RT_ENDIANNESS_LE /* Assume little endian on windows */
#	else
#		define RT_ENDIANNESS_UNKNOWN
#	endif
//#	define RT_PLATFORM_INTERNAL_LITTLE_ENDIAN 0x41424344UL 
//#	define RT_PLATFORM_INTERNAL_BIG_ENDIAN    0x44434241UL
//#	define RT_PLATFORM_INTERNAL_ENDIAN_ORDER  ('ABCD')
//#	if ENDIAN_ORDER==LITTLE_ENDIAN
//#		define RT_ENDIANNESS_LE
//#	elif ENDIAN_ORDER==BIG_ENDIAN
//#		define RT_ENDIANNESS_BE
//#	else
//#   define RT_ENDIANNESS_UNKNOWN
//#	endif
#elif defined(RT_PLATFORM_PPC64)
#	if (defined(__BYTE_ORDER__) && defined(__ORDER_LITTLE_ENDIAN__) && (__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__)) || defined(__LITTLE_ENDIAN__)
#		define RT_ENDIANNESS_LE
#	elif (defined(__BYTE_ORDER__) && defined(__ORDER_BIG_ENDIAN__) && (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)) || defined(__BIG_ENDIAN__)
#		define RT_ENDIANNESS_BE
#	else
#		define RT_ENDIANNESS_UNKNOWN
#	endif
#elif defined(RT_PLATFORM_IA64)
#	define RT_ENDIANNESS_UNKNOWN
#else
#	define RT_ENDIANNESS_UNKNOWN
#endif
// ______________________________MACROS_END_________________________________

// ____________________________BEGIN_CONSTANTS______________________________
// _____________________________CONSTANTS_END_______________________________

// ______________________________BEGIN_TYPES________________________________
/** \brief CPU type */
typedef enum enum_rt_cpu_type
{
	RT_CPU_DEFAULT       = 0x00000000, ///< Default CPU, represent a "no optimization" path

	RT_CPU_X86           = 0x10000000, ///< x86(-64) CPU
	RT_CPU_X86_FPU       = 0x10000001, ///< x86(-64) CPU has FPU
	RT_CPU_X86_CMOV      = 0x10000002, ///< x86(-64) CPU has CMOV Instruction
	RT_CPU_X86_MMX       = 0x10000004, ///< x86(-64) CPU supports MMX instruction set
	RT_CPU_X86_3DNOW     = 0x10000008, ///< x86(-64) CPU supports 3DNow instruction set
	RT_CPU_X86_3DNOW_EXT = 0x10000010, ///< x86(-64) CPU supports 3DNowExt instruction set
	RT_CPU_X86_SSE       = 0x10000020, ///< x86(-64) CPU supports SSE instruction set
	RT_CPU_X86_SSE2      = 0x10000040, ///< x86(-64) CPU supports SSE2 instruction set
	RT_CPU_X86_SSE3      = 0x10000080, ///< x86(-64) CPU supports SSE3 instruction set
	RT_CPU_X86_SSSE3     = 0x10000100, ///< x86(-64) CPU supports SSSE3 instruction set
	RT_CPU_X86_SSE41     = 0x10000200, ///< x86(-64) CPU supports SSE41 instruction set
	RT_CPU_X86_SSE4A     = 0x10000400, ///< x86(-64) CPU supports SSE4A instruction set
	RT_CPU_X86_SSE42     = 0x10000800, ///< x86(-64) CPU supports SSE42 instruction set
	RT_CPU_X86_POPCNT    = 0x10001000, ///< x86(-64) CPU has POPCNT instruction
	RT_CPU_X86_ABM       = 0x10002000, ///< x86(-64) CPU supports Advanced Bit Manipulation instruction set
	RT_CPU_X86_AES       = 0x10004000, ///< x86(-64) CPU supports AES instruction set
	RT_CPU_X86_AVX       = 0x10008000, ///< x86(-64) CPU supports AVX instruction set
	RT_CPU_X86_MOVBE     = 0x10010000, ///< x86(-64) CPU has MOVBE instruction
	RT_CPU_X86_FMA3      = 0x10020000, ///< x86(-64) CPU supports FMA3 instruction set
	RT_CPU_X86_FMA4      = 0x10040000, ///< x86(-64) CPU supports FMA4 instruction set
	RT_CPU_X86_XOP       = 0x10080000, ///< x86(-64) CPU supports XOP instruction set
	RT_CPU_X86_AVX2      = 0x10100000, ///< x86(-64) CPU supports AVX2 instruction set
	RT_CPU_X86_CLMUL     = 0x10200000, ///< x86(-64) CPU supports CLMUL instruction set

	RT_CPU_ARM           = 0x40000000, ///< ARM(64) CPU
	RT_CPU_ARM_VFP       = 0x40000001, ///< ARM(64) CPU supports VFP
	RT_CPU_ARM_VFPv3     = 0x40000002, ///< ARM(64) CPU supports VFPv3
	RT_CPU_ARM_VFPv3D16  = 0x40000004, ///< ARM(64) CPU supports VFPv3 with 16 registers (instead of 32)
	RT_CPU_ARM_NEON      = 0x40000010, ///< ARM(64) CPU supports NEON
	RT_CPU_ARM_V7A       = 0x40000020, ///< ARM(64) CPU at least V7A
	RT_CPU_ARM_V8A       = 0x40000040, ///< ARM(64) CPU at least V8A
	RT_CPU_ARM_AES       = 0x40000100, ///< ARM(64) CPU supports AES extensions
	RT_CPU_ARM_CRC32     = 0x40000200, ///< ARM(64) CPU supports CRC32 extensions
	RT_CPU_ARM_SHA1      = 0x40000400, ///< ARM(64) CPU supports CRC32 extensions
	RT_CPU_ARM_SHA2      = 0x40000800, ///< ARM(64) CPU supports CRC32 extensions
	RT_CPU_ARM_PMULL     = 0x40001000, ///< ARM(64) CPU supports PMULL and PMULL2 extensions

	RT_CPU_PPC           = 0x80000000, ///< PPC(64) CPU

	RT_CPU_MAX           = 0xFFFFFFFF  ///< Maximum CPU, special flag to set "best optimization path supported by the CPU"
}rt_cpu_type;
// _______________________________TYPES_END_________________________________

// ___________________BEGIN_GLOBAL_VARIABLES_DEFINITIONS____________________
// ____________________GLOBAL_VARIABLES_DEFINITIONS_END_____________________

// ______________________BEGIN_FUNCTIONS_DEFINITIONS________________________
// _______________________FUNCTIONS_DEFINITIONS_END_________________________

 /** @} */
 
#ifdef __cplusplus
}
#endif

// End of protection against multiple inclusions
#endif // !defined(MPH_RT_ATTRIBUTES_H_705548_INCLUDED)
