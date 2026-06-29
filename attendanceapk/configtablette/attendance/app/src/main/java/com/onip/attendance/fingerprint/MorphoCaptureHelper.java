package com.onip.attendance.fingerprint;

import android.util.Log;
import com.morpho.morphosmart.sdk.CallbackMask;
import com.morpho.morphosmart.sdk.Coder;
import com.morpho.morphosmart.sdk.DetectionMode;
import com.morpho.morphosmart.sdk.EnrollmentType;
import com.morpho.morphosmart.sdk.ErrorCodes;
import com.morpho.morphosmart.sdk.LatentDetection;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.morpho.morphosmart.sdk.Template;
import com.morpho.morphosmart.sdk.TemplateFVPType;
import com.morpho.morphosmart.sdk.TemplateList;
import com.morpho.morphosmart.sdk.TemplateType;
import java.util.Observer;

/**
 * Accès sérialisé au capteur Morpho — évite les blocages (capture + init concurrentes).
 */
public final class MorphoCaptureHelper {

    private static final String TAG = "MorphoCaptureHelper";
    public static final Object DEVICE_LOCK = new Object();

    private MorphoCaptureHelper() {
    }

    public static void cancelAcquisition(MorphoDevice device) {
        if (device == null) {
            return;
        }
        synchronized (DEVICE_LOCK) {
            try {
                int ret = device.cancelLiveAcquisition();
                Log.d(TAG, "cancelLiveAcquisition ret=" + ret);
            } catch (Exception e) {
                Log.w(TAG, "cancelLiveAcquisition: " + e.getMessage());
            }
        }
    }

    public static void closeDevice(MorphoDevice device) {
        if (device == null) {
            return;
        }
        synchronized (DEVICE_LOCK) {
            cancelAcquisition(device);
            try {
                int ret = device.closeDevice();
                Log.d(TAG, "closeDevice ret=" + ret);
            } catch (Exception e) {
                Log.w(TAG, "closeDevice: " + e.getMessage());
            }
        }
    }

    public static boolean isDeviceResponsive(MorphoDevice device) {
        if (device == null) {
            return false;
        }
        synchronized (DEVICE_LOCK) {
            try {
                return device.ping() == ErrorCodes.MORPHO_OK;
            } catch (Exception e) {
                Log.w(TAG, "ping: " + e.getMessage());
                return false;
            }
        }
    }

    public static int captureOneTemplate(MorphoDevice device, TemplateList templateList, Observer observer) {
        synchronized (DEVICE_LOCK) {
            cancelAcquisition(device);

            int callbackCmd = CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue()
                    | CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue()
                    | CallbackMask.MORPHO_CALLBACK_CODEQUALITY.getValue()
                    | CallbackMask.MORPHO_CALLBACK_DETECTQUALITY.getValue();

            int detectMode = DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue()
                    | DetectionMode.MORPHO_FORCE_FINGER_ON_TOP_DETECT_MODE.getValue();

            return device.capture(
                    30,
                    0,
                    0,
                    1,
                    TemplateType.MORPHO_PK_ISO_FMR,
                    TemplateFVPType.MORPHO_NO_PK_FVP,
                    512,
                    EnrollmentType.ONE_ACQUISITIONS,
                    LatentDetection.LATENT_DETECT_ENABLE,
                    Coder.MORPHO_DEFAULT_CODER,
                    detectMode,
                    templateList,
                    callbackCmd,
                    observer);
        }
    }

    /**
     * Compare deux templates via le SDK Morpho (accès sérialisé au capteur).
     */
    public static int verifyMatchScore(MorphoDevice device, byte[] capturedTemplate, byte[] storedTemplate, int far) {
        if (device == null || capturedTemplate == null || storedTemplate == null) {
            return -1;
        }
        synchronized (DEVICE_LOCK) {
            try {
                TemplateList searchList = new TemplateList();
                Template searchTemplate = new Template();
                searchTemplate.setData(capturedTemplate);
                searchTemplate.setTemplateType(TemplateType.MORPHO_PK_ISO_FMR);
                searchList.putTemplate(searchTemplate);

                TemplateList referenceList = new TemplateList();
                Template referenceTemplate = new Template();
                referenceTemplate.setData(storedTemplate);
                referenceTemplate.setTemplateType(TemplateType.MORPHO_PK_ISO_FMR);
                referenceList.putTemplate(referenceTemplate);

                Integer matchingScore = new Integer(0);
                int ret = device.verifyMatch(far, searchList, referenceList, matchingScore);
                if (ret == ErrorCodes.MORPHO_OK) {
                    return matchingScore;
                }
            } catch (Exception e) {
                Log.e(TAG, "verifyMatch: " + e.getMessage(), e);
            }
            return -1;
        }
    }
}
