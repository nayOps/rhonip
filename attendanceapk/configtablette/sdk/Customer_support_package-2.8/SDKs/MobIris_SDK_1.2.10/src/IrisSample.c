#include "IrisInterface.h"

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <android/log.h>
#include <pthread.h>

#define _countof(_Array) (sizeof(_Array) / sizeof(_Array[0]))

void RT_CALLBACKCALL logCallback(rt_loglevel i__level, const rt_string* i__message, void* io__userContext){
    android_LogPriority priority;
    switch(i__level) {
        case RT_LOGLEVEL_DEBUG:
            priority=ANDROID_LOG_DEBUG;
            break;
        case RT_LOGLEVEL_INFO:
            priority=ANDROID_LOG_INFO;
            break;
        case RT_LOGLEVEL_WARNING:
            priority=ANDROID_LOG_WARN;
            break;
        case RT_LOGLEVEL_ERROR:
            priority=ANDROID_LOG_ERROR;
            break;
    }
    __android_log_print(priority, "IrisInterface", "%s", i__message->string);
    return;
}

uint32_t previewCallback(rt_image *i_img,IrisLocation i_IrisLeft,IrisLocation i_IrisRight,uint32_t i_Status, void *io_context){//[IN] callback used for GUI video display and abort

    return IRIS_ERR_SUCCESS;
}

int main_iris(int argc, char **argv){

    /*****************
    Inputs
    */
    char outputFilePath[]="/sdcard/IrisSample/";
    char replayFilePath[]="/sdcard/IrisSample/RC_20150131_062113.rtv";//RC_20170223_103712.smv";//RC_20170223_103853.smv";//RC_20161017_154903.smv";
    char providerURL[]="http://localhost:29080/lkms/LicenseRequest?profileId=demoSecureIdentity";
    char lkmsURL[]="http://localhost:29081/lkms-server-app/v1/licenses";
    char licenseFilePath[]="/sdcard/IrisSample/LKMSLicence.dat";

    char filename[256];
    uint32_t timeout=25000;
    uint32_t i;
    IRIS_FORMAT outputFormat=IRIS_FLAG_KIND7_J2K;

    void *previewContext=NULL;
    void *logContext=NULL;

    IRIS_ATTRIBUTE i_attributesArray[]={
            //replay mode
            { IRIS_ATTR_RECORD_INPUT_FILEPATH, replayFilePath, sizeof(replayFilePath) },
            //acquisition params
            //{ IRIS_ATTR_RECORD_OUTPUT_FILEPATH, outputFilePath, sizeof(outputFilePath) },
            { IRIS_ATTR_TIMEOUT, &timeout, sizeof(uint32_t) },
            { IRIS_ATTR_OUTPUT_FORMAT, &outputFormat, sizeof(IRIS_FORMAT) },
            { IRIS_ATTR_PREVIEW_CONTEXT, previewContext,  sizeof(void *) },
            { IRIS_ATTR_LOG_CONTEXT, logContext,  sizeof(void *) },
            { IRIS_ATTR_LICENSE_FILE_PATH, licenseFilePath, sizeof(licenseFilePath)  },
            { IRIS_ATTR_LKMS_SP_URL, providerURL, sizeof(providerURL)  },
            { IRIS_ATTR_LKMS_URL, lkmsURL, sizeof(lkmsURL)  }
    };
    uint32_t i_attributesArrayLength=_countof(i_attributesArray);

    /******************
    Outputs
    */
    IRIS_RESULT *o_attributesArray=NULL;
    uint32_t o_attributesArrayLength;
    uint32_t o_result;
    FILE *f;
    rt_buffer *o_buffer;

    /******************
    Workflow
    */
    o_result = IrisInitialize(i_attributesArray,i_attributesArrayLength,previewCallback,logCallback);
    if(o_result){
        fprintf(stderr,"IrisInitialize error:%d",o_result);
        exit(0);
    }


    //start preview before acquisition
    o_result = IrisStartPreview(i_attributesArray,i_attributesArrayLength);
    if(o_result){
        fprintf(stderr,"IrisStartPreview error:%d",o_result);
        exit(0);
    }

    //start acquisition
    o_result = IrisAcquisition(i_attributesArray,i_attributesArrayLength, &o_attributesArray,&o_attributesArrayLength);
    if(o_result){
        fprintf(stderr,"IrisAcquisition error:%d",o_result);
        exit(0);
    }

    /******************
    Look at result
    */
    for(i=0;i<o_attributesArrayLength;i++){
        memset(filename,0,sizeof(filename));
        if(o_attributesArray[i].type==IRIS_RESULT_LEFT){
            sprintf(filename,"%s/kind7_%s.j2k",outputFilePath,"Left");
        }
        else if(o_attributesArray[i].type==IRIS_RESULT_RIGHT){
            sprintf(filename,"%s/kind7_%s.j2k",outputFilePath,"Right");
        }
        if(filename[0]){
            f = fopen(filename,"wb");
            if(f)
            {
                o_buffer=(rt_buffer*)(o_attributesArray[i].pValue);
                fwrite(o_buffer->data,o_buffer->size,1,f);
                fclose(f);
            }
        }
        if(o_attributesArray[i].type==IRIS_DEVICE_ID) {
            rt_string id={o_attributesArray[i].pValue,o_attributesArray[i].ulValueLen};
            logCallback(RT_LOGLEVEL_INFO,&id,NULL );
        }
    }

    /******************
    Finalize
    */
    //Free results
    IrisFreeResults(o_attributesArray,o_attributesArrayLength);

    //Finalize, release camera
    o_result = IrisFinalize();
    if(o_result){
        fprintf(stderr,"IrisFinalize error:%d",o_result);
        //exit(0);
    }
};