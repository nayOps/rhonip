#include "rt_types.h"


/**
	@brief Iris attributes section - input params
	*/
typedef enum{
	IRIS_ATTR_OUTPUT_FORMAT					= (int32_t)0x00000001, //expected output format //full picture/K7
	IRIS_ATTR_TIMEOUT						= (int32_t)0x00000002, //maximum time for acquisition (in milli-seconds)
	IRIS_ATTR_RECORD_OUTPUT_FILEPATH		= (int32_t)0x00000003, //output camera stream on filesystem path for replay/debug
	IRIS_ATTR_PREVIEW_ENCODING				= (int32_t)0x00000004, //image preview encoding	
	IRIS_ATTR_REFERENCE_TEMPLATE_LEFT		= (int32_t)0x00000005, //template for matching 
	IRIS_ATTR_REFERENCE_TEMPLATE_RIGHT		= (int32_t)0x00000006, //template for matching 
	IRIS_ATTR_REFERENCE_TEMPLATE_FORMAT		= (int32_t)0x00000007, //template format for matching 
	IRIS_ATTR_PREVIEW_CONTEXT				= (int32_t)0x00000008, //user context passed on preview callback 
	IRIS_ATTR_OUTPUT_SIZE					= (int32_t)0x00000009, //expected ouput size for JPEG200 kind7 
	IRIS_ATTR_LOG_FILE						= (int32_t)0x0000000A, //log file 
	IRIS_ATTR_LOG_CONTEXT					= (int32_t)0x0000000B, //log file 
	IRIS_ATTR_LICENSE_FILE_PATH				= (int32_t)0x0000000C, //LKMS license file path
	IRIS_ATTR_LKMS_URL						= (int32_t)0x0000000D, //LKMS url
	IRIS_ATTR_LKMS_SP_URL					= (int32_t)0x0000000E, //LKMS service provider
	IRIS_ATTR_TEMPLATESLIST					= (int32_t)0x00000010, //matching templates
	IRIS_ATTR_TEMPLATESLIST_LEN				= (int32_t)0x00000020, //matching templates size
	IRIS_ATTR_MATCH_MODE					= (int32_t)0x00000030, //matching mode (unique/continuous)
	IRIS_ATTR_REVERT_IMG					= (int32_t)0x00000040, //revert image on capture
	IRIS_ATTR_EXPECTED_IRIS_RADIUS			= (int32_t)0x00000050, //expected iris size (default 127)
	IRIS_ATTR_EARLY_EXIT					= (int32_t)0x00000060, //enable early exit on acquisition (default false)
	IRIS_ATTR_CAMPAIGN_OUTPUT				= (int32_t)0x00000070, //prefix for campaign mode output (enable campaign mode :frame list / continue record after early exit)
	IRIS_ATTR_MATCH_SCORE					= (int32_t)0x00000080, //prefix for campaign mode output (enable campaign mode :frame list / continue record after early exit)

	IRIS_ATTR_RECORD_INPUT_FILEPATH			= (int32_t)0xF0000005, //output camera on filesystem path for replay/debug
	IRIS_ATTR_INVALID						= (int32_t)0x7FFFFFFF  ///< Do not use
} IRIS_ATTRIBUTE_ENUM;


/**
	@brief Iris flag section - output result image format
	*/
typedef enum{
	IRIS_MATCH_SINGLE						= (int32_t)0x00000001, //iris image format
	IRIS_MATCH_MULTI						= (int32_t)0x00000002, //kind7 format compressed JPEG 2000
	IRIS_MATCH_INVALID						= (int32_t)0x7FFFFFFF  ///< Do not use
}IRIS_MATCH_MODE;

/**
	@brief Iris flag section - output result image format
	*/
typedef enum{
	IRIS_FLAG_IMAGE							= (int32_t)0x00000001, //iris image format
	IRIS_FLAG_KIND7_J2K						= (int32_t)0x00000002, //kind7 format compressed JPEG 2000
	IRIS_FLAG_TEMPLATE						= (int32_t)0x00000004, //template
	IRIS_FLAG_INVALID						= (int32_t)0x7FFFFFFF  ///< Do not use
}IRIS_FORMAT;

/**
	@brief Iris attributes section - output results
	*/
typedef enum{
	IRIS_RESULT_LEFT						= (int32_t)0x00000001,  
	IRIS_RESULT_RIGHT						= (int32_t)0x00000002,
	IRIS_RESULT_WIDTH						= (int32_t)0x00000003,
	IRIS_RESULT_HEIGHT						= (int32_t)0x00000004,
	IRIS_RESULT_ENCODING					= (int32_t)0x00000005,
	IRIS_RESULT_MATCHING_SCORE				= (int32_t)0x00000006,
	IRIS_DEVICE_ID							= (int32_t)0x00000007,
    IRIS_TEMPLATE_LEFT						= (int32_t)0x00000008,
    IRIS_TEMPLATE_RIGHT						= (int32_t)0x00000009,
    IRIS_PICTURE_LEFT						= (int32_t)0x0000000A,
    IRIS_PICTURE_RIGHT						= (int32_t)0x0000000B,
	IRIS_RESULT_MATCHING_INDEX				= (int32_t)0x0000000C,
	IRIS_RESULT_ACQUISITION_QUALITY			= (int32_t)0x0000000D,
	IRIS_RESULT_TEMPLATE_LEFT_QUALITY		= (int32_t)0x00000018,
	IRIS_RESULT_TEMPLATE_RIGHT_QUALITY		= (int32_t)0x00000019,

	IRIS_RESULT_INVALID						= (int32_t)0x7FFFFFFF
} IRIS_RESULT_ENUM;


/**
	@brief Iris status section bit field - used by preview callback
	*/
#define IRIS_STATUS_PREVIEW						0x00000001 //preview only
#define IRIS_STATUS_TIMEOUT						0x00000002 //timeout occured
#define IRIS_STATUS_IRIS_PENDING				0x00000004 //looking for iris
#define IRIS_STATUS_IRIS_FOUND					0x00000008 //iris found
#define IRIS_STATUS_IRIS_LEFT_FOUND				0x00000010 //iris left found
#define IRIS_STATUS_IRIS_RIGHT_FOUND			0x00000020 //iris right found
#define IRIS_STATUS_IRIS_LEFT_ACQUIRED			0x00000040 //iris left acquired
#define IRIS_STATUS_IRIS_RIGHT_ACQUIRED			0x00000080 //iris right acquired

/**
	@brief Iris errors section
	*/
#define IRIS_ERR_SUCCESS						0x00000000 //OK
#define IRIS_ERR_UNSPECIFIED					0x00000001 //unspecified error
#define IRIS_ERR_LICENCE						0x00000002 //licence violation
#define IRIS_ERR_INVALID_PARAM					0x00000003 //invalid parameter
#define IRIS_ERR_UNINITIALIZED					0x00000004 //iris module not initialized
#define IRIS_ERR_ALREADY_INITIALIZED			0x00000005 //iris module already initialized
#define IRIS_ERR_CAMERA_UNAVAILABLE				0x00000006 //camera unavailable
// ...
#define IRIS_EXTERNAL_SPECIFIC_ERROR_MASK		0x80000000

#define IRIS_EXTERNAL_SPECIFIC_WARN_MASK		0x40000000
#define IRIS_WARN_CAMERA_OTP_READ				(IRIS_EXTERNAL_SPECIFIC_WARN_MASK | 0x00000001)
#define IRIS_WARN_CAPTURE_ON_TIMEOUT			(IRIS_EXTERNAL_SPECIFIC_WARN_MASK | 0x00000002)

/**
	@brief Iris param type
	*/
typedef struct {
  IRIS_ATTRIBUTE_ENUM type;
  void*			pValue;
  uint32_t		ulValueLen;  /* in bytes */
} IRIS_ATTRIBUTE;

/**
	@brief Iris result type
	*/
typedef struct {
  IRIS_RESULT_ENUM type;
  void*			pValue;
  uint32_t		ulValueLen;  /* in bytes */
} IRIS_RESULT;

/**
	@brief Iris location type
	*/
typedef struct {
	uint32_t x;
	uint32_t y;
	uint32_t radius;
}IrisLocation;

/**
	@brief Callback for camera preview
	@param rt_image *i_img [in] : image from camera
	@param IrisLocation i_IrisLeft [in] : location of left iris if localized
	@param IrisLocation i_IrisRight [in] : location of right iris if localized
	@param uint32_t i_Status [in] : status of preview @ref "status section bit field"
	@param void *io_Context [in/out] : user context
	@return error code
	*/
typedef uint32_t (*PreviewCallback) (rt_image *i_img,IrisLocation i_IrisLeft,IrisLocation i_IrisRight,uint32_t i_Status, void *io_Context);//[IN] callback used for GUI video display and abort

/**
	@brief Initialization method : initialize aquisition engine
	@param const IRIS_ATTRIBUTE *i_attributesArray [in] : input params
	@param uint32_t i_attributesArrayLength [in] : count of input params
	@param PreviewCallback i_previewCallback [in] : pointer to preview callback function
	@param rt_logfunction i_logCallback [in] : pointer to log callback function
	@return error code
	*/
uint32_t IrisInitialize(const IRIS_ATTRIBUTE *i_attributesArray,uint32_t i_attributesArrayLength, PreviewCallback i_previewCallback, rt_logfunction i_logCallback);

/**
	@brief IrisStartPreview method : start preview, attach to camera module
	@param const IRIS_ATTRIBUTE *i_attributesArray [in] : input params
	@param uint32_t i_attributesArrayLength [in] : count of input params
	@return error code
	*/
uint32_t IrisStartPreview(const IRIS_ATTRIBUTE *i_attributesArray,uint32_t i_attributesArrayLength);

/**
	@brief IrisAcquisition method : look for iris on video stream
	@param const IRIS_ATTRIBUTE *i_attributesArray [in] : input params
	@param uint32_t i_attributesArrayLength [in] : count of input params
	@param IRIS_RESULT **o_attributesArray [out] : output results
	@param uint32_t *o_attributesArrayLength [out] : count of output results
	@return error code
	*/
uint32_t IrisAcquisition(const IRIS_ATTRIBUTE *i_attributesArray,uint32_t i_attributesArrayLength, IRIS_RESULT **o_attributesArray,uint32_t *o_attributesArrayLength);

/**
	@brief IrisAcquisitionAndMatching method : look for iris on video stream and try to match with iris template
	@param const IRIS_ATTRIBUTE *i_attributesArray [in] : input params
	@param uint32_t i_attributesArrayLength [in] : count of input params
	@param IRIS_RESULT **o_attributesArray [out] : output results
	@param uint32_t *o_attributesArrayLength [out] : count of output results
	@return error code
	*/
uint32_t IrisAcquisitionAndMatching(const IRIS_ATTRIBUTE *i_attributesArray,uint32_t i_attributesArrayLength, IRIS_RESULT **o_attributesArray,uint32_t *o_attributesArrayLength);

/**
	@brief IrisFinalize method : release aquisition engine and camera
	@return error code
	*/
uint32_t IrisFinalize();

/**
	@brief IrisFreeResults method : free previous results
	@param IRIS_RESULT *i_attributesArray [in] : input results to free
	@param uint32_t i_attributesArrayLength [in] : count of input results
	@return error code
	*/
uint32_t IrisFreeResults(IRIS_RESULT *i_attributesArray,uint32_t i_attributesArrayLength);


/**
	@brief IrisGetDeviceId method :  return internal device id (IrisInitialize has to be called before)
 	@param char o_id [out] return array storing device id in hexa format without string ending 0
 	@return error code
 */
uint32_t IrisGetDeviceId(char o_id[64]);

/**
	@brief IrisGetCameraId method :  return internal camera id (IrisInitialize has to be called before)
 	@param const unsigned char** o_id [out] : return array storing camera id
 	@param uint32_t *o_idSize [out] : return size of camera id
 	@return error code
 */
uint32_t IrisGetCameraId(const unsigned char** o_id, uint32_t *o_idSize);

/**
	@brief IrisGetCameraModelId method :  return internal camera id (IrisInitialize has to be called before)
 	@param const char** o_id [out] : return array storing camera model id string
 	@return error code
 */
uint32_t IrisGetCameraModelId(const char** o_id);

/**
	@brief IrisGetVersion method :  return version of MobIris
 	@return version string
 */
const char *IrisGetVersion();

/**
	@brief getMachingScore method : return matching score on ident mode
	@return error code
	*/
uint32_t getMachingScore();

/**
	@brief getMachingId method : return matching ID on ident mode
	@return ID or 0 if not available
	*/
uint32_t getMachingId();

