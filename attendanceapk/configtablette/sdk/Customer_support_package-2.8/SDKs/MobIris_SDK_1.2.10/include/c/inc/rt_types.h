// Protection against multiple inclusions
#ifndef MPH_RT_TYPES_H_705548_INCLUDED
#define MPH_RT_TYPES_H_705548_INCLUDED

#if defined(_MSC_VER) && (_MSC_VER > 1000) /* parasoft-suppress  MISRA2004-19_11 "_MSC_VER has been checked in the same line" */
// Protection against multiple inclusions MSVC version. Provides speed-up in compilation
#pragma once
#endif

/* _BEGIN_FILE_HEADER_**********************************************************
*
*  PROJECT         :   URT Common Headers
*
*  MODULE          :   Types
*
*  LANGUAGE        :   C
*
*  PORTABILITY     :   Windows 2000; Windows XP ; Linux ; 32/64/ARM
*
*  DESCRIPTION     :   Provides standard types for all URT projects
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
#include "rt_compiler.h"
#include "rt_platform.h"
#include "rt_os.h"
#if RT_COMPILER_MSVC_AT_LEAST_VC6
#	if RT_COMPILER_MSVC_AT_LEAST_VC10
#		include <stdint.h>
#	else
#		include "win32/stdint.h"
#	endif
#	if RT_COMPILER_MSVC_AT_LEAST_VC12
#		include <inttypes.h>
#	else
#		include "win32/inttypes.h"
#	endif
#elif defined(RT_COMPILER_MSVC)
#	error This compiler is not supported
#else
#	include <stdint.h>
#	include <inttypes.h>
#endif
#if defined(RT_OS_INTEGRITY)
#	include <inttypes.h>
#endif
#include <limits.h>
#include <stddef.h> // to define size_t, offsetof
// specific includes:
#include "rt_attributes.h"

/* bug in Visual Studio 2010 x64 */
#if RT_COMPILER_MSVC_AT_LEAST_VC10 && !RT_COMPILER_MSVC_AT_LEAST_VC11 && defined(RT_PLATFORM_X64)
#	if defined(INTPTR_MAX) && (INTPTR_MAX != INT64_MAX)
#		undef INTPTR_MAX
#		define INTPTR_MAX  (INT64_MAX)
#	endif
#	if defined(INTPTR_MIN) && (INTPTR_MIN != INT64_MIN)
#		undef INTPTR_MIN
#		define INTPTR_MIN  (INT64_MIN)
#	endif
#	if defined(UINTPTR_MAX) && (UINTPTR_MAX != UINT64_MAX)
#		undef UINTPTR_MAX
#		define UINTPTR_MAX (UINT64_MAX)
#	endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

/** \defgroup @RTCH_TYPES Morpho RT Types
* @{
*/
// _____________________________INCLUDES_END________________________________

// _____________________________BEGIN_MACROS________________________________
#ifndef RT__W64
#	if defined(_MSC_VER) && (_MSC_VER < 1500) && !defined(_M_X64) // Only check Visual Studio < 2008, check for major version already done
#		define RT__W64 __w64
#	else
#		define RT__W64
#	endif
#endif

#if defined(RT_OS_WINDOWS) || defined(RT_OS_LINUX_CYGWIN)
/** \brief Callback function call convention */
#	define RT_CALLBACKCALL  __stdcall
/** \brief Alloc functions call convention */
#	define RT_ALLOCCALL     __cdecl
#else
/** \brief Callback function call convention */
#	define RT_CALLBACKCALL  
/** \brief Alloc functions call convention */
#	define RT_ALLOCCALL     
#endif

// ______________________________MACROS_END_________________________________

// ____________________________BEGIN_CONSTANTS______________________________
// _____________________________CONSTANTS_END_______________________________

// ______________________________BEGIN_TYPES________________________________

/** \brief 32 bits real */
typedef float  rt_real32;
RT_ATTRIBUTE_DEPRECATED typedef rt_real32 rt_real32_t;

/** \brief 64 bits real */
typedef double rt_real64;
RT_ATTRIBUTE_DEPRECATED typedef rt_real64 rt_real64_t;

/** \brief pointer type */
typedef void*  rt_ptr;
RT_ATTRIBUTE_DEPRECATED typedef rt_ptr rt_ptr_t;

/** \brief char type */
typedef char  rt_char;
/** \brief C string type */
typedef char *rt_cstring;

RT_ATTRIBUTE_DEPRECATED typedef rt_char rt_char_t;
RT_ATTRIBUTE_DEPRECATED typedef rt_cstring rt_cstring_t;

/** \brief boolean type */
typedef uint8_t  rt_bool;
RT_ATTRIBUTE_DEPRECATED typedef rt_bool rt_bool_t;

/** \brief string type */
typedef struct s_rt_string
{
	const rt_char* string; ///< NUL terminated C string
	size_t         size;   ///< Buffer size
}rt_string;

/** \brief Data buffer type */
typedef struct s_rt_buffer
{
	uint8_t* data; ///< Data buffer
	size_t   size; ///< Buffer size
}rt_buffer;

/** \brief Const Data buffer type */
typedef struct s_rt_constbuffer
{
	const uint8_t * data; ///< Const Data buffer
	size_t          size; ///< Buffer size
}rt_constbuffer;

/** \brief Extended Data buffer type */
typedef struct s_rt_buffer_ext
{
	uint8_t* data; ///< Data buffer
	size_t   size; ///< Actual size of the information in the buffer (must be <= allocated_size)
	size_t   allocated_size; ///<Total Buffer size (allocated)
} rt_buffer_ext;

/** \brief Const Extended Data buffer type */
typedef struct s_rt_constbuffer_ext
{
	const uint8_t* data; ///< Data buffer
	size_t   size; ///< Actual size of the information in the buffer (must be <= allocated_size)
	size_t   allocated_size; ///<Total Buffer size (allocated)
} rt_constbuffer_ext;

/** \brief Version type */
typedef struct s_rt_version
{
	uint32_t  major;       ///< Major version of the component
	uint32_t  minor;       ///< Minor version of the component
	uint32_t  patch;       ///< Patch version of the component
	uint32_t  revision;    ///< Revision of the component (might be SVN revision or other, component specific)
	rt_string details;     ///< Other version information
}rt_version;

/** \brief Allocator structure */
typedef struct s_rt_allocator
{
	void * (RT_ALLOCCALL *malloc)(size_t i__size);       ///< pointer to a malloc function
	void   (RT_ALLOCCALL *free)(void * io__memoryBlock); ///< pointer to a free function
}rt_allocator;

/** \brief Log level type */
typedef enum e_rt_loglevel
{
	RT_LOGLEVEL_DEBUG   = (int32_t)0x00000000, ///< Debug message
	RT_LOGLEVEL_INFO    = (int32_t)0x00000001, ///< Informative message
	RT_LOGLEVEL_WARNING = (int32_t)0x00000002, ///< Warning message
	RT_LOGLEVEL_ERROR   = (int32_t)0x00000003, ///< Error message
	RT_LOGLEVEL_INVALID = (int32_t)0xFFFFFFFF  ///< Do not use
} rt_loglevel;

/** \brief Log message callback function type */
typedef void (RT_CALLBACKCALL *rt_logfunction)(rt_loglevel i__level, const rt_string* i__message, void* io__userContext);
/** \brief Log message callback function type for binary data */
typedef void (RT_CALLBACKCALL *rt_logbinaryfunction)(rt_loglevel i__level, const rt_string* i__description, const rt_buffer* i__buffer, void* io__userContext);
/** \brief Binary callback function type */
typedef void (RT_CALLBACKCALL *rt_binarycallback)(const rt_buffer* i__buffer, void* io__userContext);

/** \brief Color Space type */
typedef enum e_rt_colorspace
{
	RT_COLORSPACE_Y8      = (int32_t)0x00000000, ///< Grayscale 8bpp image.
	RT_COLORSPACE_Y16LE   = (int32_t)0x00000001, ///< Grayscale 16bpp image (Little Endian).
	RT_COLORSPACE_BGR24   = (int32_t)0x00000002, ///< Color 24bpp BGR image (BMP like memory layout).
	RT_COLORSPACE_RGB24   = (int32_t)0x00000003, ///< Color 24bpp RGB image (reversed memory layout compared to RT_COLORSPACE_BGR24).
	RT_COLORSPACE_RGBA32  = (int32_t)0x00000004, ///< Color 32bpp RGBA image
	RT_COLORSPACE_NV12    = (int32_t)0x00000005, ///< Color. 1 Y 8bpp plane & 1 U/V interleaved plane. Chroma planes are subsampled in both the horizontal and vertical dimensions by a factor of 2.
	RT_COLORSPACE_NV21    = (int32_t)0x00000006, ///< Color. 1 Y 8bpp plane & 1 V/U interleaved plane. Chroma planes are subsampled in both the horizontal and vertical dimensions by a factor of 2.
	RT_COLORSPACE_YUV444  = (int32_t)0x00000007, ///< Color 24bpp format 8 Bit YUV 444 with order YUV (Data: Y0 U0 V0 Y1 U1 V1 ...).
	RT_COLORSPACE_AYUV444 = (int32_t)0x00000008, ///< Color 32bpp format 8 Bit YUV 444 with order AYUV (Data: A0 Y0 U0 V0 A1 Y1 U1 V1 ...).
	RT_COLORSPACE_A8Y8    = (int32_t)0x00000009, ///< Color 16bpp format 8 Bit A8Y8 with order AY (Data: A0 Y0 A1 Y1 ...).
	RT_COLORSPACE_INVALID = (int32_t)0xFFFFFFFF ///< Do not use
} rt_colorspace;

/** \brief Image type

 \remark For #RT_COLORSPACE_NV12 and #RT_COLORSPACE_NV21 color spaces, the U/V (resp. V/U) plane follows the Y plane in memory. The stride of the U/V (resp V/U) plane is equal to the stride of the Y plane.
 */
typedef struct s_rt_image
{
	rt_colorspace colorSpace;    ///< Image ColorSpace
	rt_buffer     data;          ///< Image raw data block.
	int32_t       stride;        ///< Size in bytes to go from one line to the next.
	uint32_t      width;         ///< Width of the image
	uint32_t      height;        ///< Height of the image
	rt_real32     resolutionDPI; ///< Resolution in DPI. Set to +0.0F when unknown.
} rt_image;

/** \brief Biometric modality */
typedef enum e_rt_biometricmodality
{
	RT_BIOMETRICMODALITY_UNKNOWN       = (int32_t)0x00000000, ///< Unknown biometric modality
	RT_BIOMETRICMODALITY_IRIS          = (int32_t)0x00001000, ///< Iris biometric
	RT_BIOMETRICMODALITY_FACE          = (int32_t)0x00002000, ///< Face biometric
	RT_BIOMETRICMODALITY_TATTOO        = (int32_t)0x00003000, ///< Tattoo biometric
	RT_BIOMETRICMODALITY_VEIN          = (int32_t)0x00004000, ///< Vein biometric
	RT_BIOMETRICMODALITY_FRICTIONRIDGE = (int32_t)0x00005000, ///< Friction ridge biometric (fingerprint, palmprint)
	RT_BIOMETRICMODALITY_INVALID       = (int32_t)0xFFFFFFFF  ///< Do not use
}rt_biometricmodality;

/** \brief Biometric location */
typedef enum e_rt_biometriclocation
{
	// Iris
	RT_BIOMETRICLOCATION_IRIS_UNKNOWN = (int32_t)0x00001000, ///< Unknown iris
	RT_BIOMETRICLOCATION_IRIS_RIGHT   = (int32_t)0x00001001, ///< Right iris
	RT_BIOMETRICLOCATION_IRIS_LEFT    = (int32_t)0x00001002, ///< Left iris
	RT_BIOMETRICLOCATION_IRIS_BOTH    = (int32_t)0x00001003, ///< Both irises

	// Face
	RT_BIOMETRICLOCATION_FACE_UNKNOWN = (int32_t)0x00002000, ///< Unknown face
	RT_BIOMETRICLOCATION_FACE_FRONTAL = (int32_t)0x00002001, ///< Frontal face

	// Tattoo
	RT_BIOMETRICLOCATION_TATTOO_UNKNOWN = (int32_t)0x00003000, ///< Unknown tattoo

	// Vein
	RT_BIOMETRICLOCATION_VEIN_UNKNOWN = (int32_t)0x00004000, ///< Unknown vein
    
	// Fingerprint
	RT_BIOMETRICLOCATION_FINGER_UNKNOWN      = (int32_t)0x00005000, ///< Unknown finger
	RT_BIOMETRICLOCATION_FINGER_RIGHT_THUMB  = (int32_t)0x00005001, ///< Right thumb
	RT_BIOMETRICLOCATION_FINGER_RIGHT_INDEX  = (int32_t)0x00005002, ///< Right index finger
	RT_BIOMETRICLOCATION_FINGER_RIGHT_MIDDLE = (int32_t)0x00005003, ///< Right middle finger
	RT_BIOMETRICLOCATION_FINGER_RIGHT_RING   = (int32_t)0x00005004, ///< Right ring finger
	RT_BIOMETRICLOCATION_FINGER_RIGHT_LITTLE = (int32_t)0x00005005, ///< Right little finger
	RT_BIOMETRICLOCATION_FINGER_LEFT_THUMB   = (int32_t)0x00005006, ///< Left thumb
	RT_BIOMETRICLOCATION_FINGER_LEFT_INDEX   = (int32_t)0x00005007, ///< Left index finger
	RT_BIOMETRICLOCATION_FINGER_LEFT_MIDDLE  = (int32_t)0x00005008, ///< Left middle finger
	RT_BIOMETRICLOCATION_FINGER_LEFT_RING    = (int32_t)0x00005009, ///< Left ring finger
	RT_BIOMETRICLOCATION_FINGER_LEFT_LITTLE  = (int32_t)0x0000500A, ///< Left little finger

	RT_BIOMETRICLOCATION_FINGER_UNKNWON_FOUR = (int32_t)0x00006000, ///< Unknown four finger slap
	RT_BIOMETRICLOCATION_FINGER_RIGHT_FOUR   = (int32_t)0x00006001, ///< Right four finger slap
	RT_BIOMETRICLOCATION_FINGER_LEFT_FOUR    = (int32_t)0x00006002, ///< Left four finger slap
	RT_BIOMETRICLOCATION_FINGER_BOTH_THUMBS  = (int32_t)0x00006003, ///< Both thumbs slap
	RT_BIOMETRICLOCATION_FINGER_BOTH_INDEX   = (int32_t)0x00006004, ///< Both index fingers slap

	RT_BIOMETRICLOCATION_PALM_UNKNOWN      = (int32_t)0x00007000, ///< Unknown palm
	RT_BIOMETRICLOCATION_PALM_RIGHT_UPPER  = (int32_t)0x00007001, ///< Right upper palm
	RT_BIOMETRICLOCATION_PALM_RIGHT_LOWER  = (int32_t)0x00007002, ///< Right lower palm
	RT_BIOMETRICLOCATION_PALM_RIGHT_WRITER = (int32_t)0x00007003, ///< Right writer palm
	RT_BIOMETRICLOCATION_PALM_LEFT_UPPER   = (int32_t)0x00007004, ///< Left upper palm
	RT_BIOMETRICLOCATION_PALM_LEFT_LOWER   = (int32_t)0x00007005, ///< Left lower palm
	RT_BIOMETRICLOCATION_PALM_LEFT_WRITER  = (int32_t)0x00007006, ///< Left writer palm

	RT_BIOMETRICLOCATION_HAND_UNKNOWN = (int32_t)0x00008000, ///< Unknown hand
	RT_BIOMETRICLOCATION_HAND_RIGHT   = (int32_t)0x00008001, ///< Right hand
	RT_BIOMETRICLOCATION_HAND_LEFT    = (int32_t)0x00008002, ///< Left hand

	RT_BIOMETRICLOCATION_FRICTIONRIDGE_UNKNOWN = (int32_t)0x00009000, ///< Unknown friction ridge

	RT_BIOMETRICLOCATION_INVALID = (int32_t)0xFFFFFFFF ///< Do not use
}rt_biometriclocation;


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
#endif // !defined(MPH_RT_TYPES_H_705548_INCLUDED)
