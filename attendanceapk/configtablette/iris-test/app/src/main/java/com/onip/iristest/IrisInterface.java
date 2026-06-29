package com.onip.iristest;

import android.graphics.Bitmap;
import android.util.Log;

/**
 * Interface native pour la reconnaissance d'iris
 * Basée sur le SDK MorphoTablet réel
 */
public class IrisInterface {

    private static final String TAG = "IrisInterface";

    // Méthodes JNI natives du SDK
    public native int initialize();
    public native Object[] capture(int i_timeout, int i_matchingScore);
    public native int cancel();
    public native int getExpectedIrisRadius();
    public native int[] getIrisLocations();
    public static native int setupResultListener(NativePreviewResultListener lsnr);
    public static native int getCapturedTpl();
    public static native int setRecordPath(String path);
    public static native String getMobIrisVersion();
    public static native String getDeviceId();
    public static native String getCameraModelId();
    public static native int getMatchScore();
    public static native int getMatchIndex();
    public static native int getAcquitisionQuality();
    public static native int getLeftTemplateQuality();
    public static native int getRightTemplateQuality();

    /*
    flush previously registered templates
     */
    public native int clearTemplates();
    /*
        @left:left iris template
        @right:right iris template
        @return: user id
     */
    public native int pushTemplate(byte []left,byte[] right);

    static {
        try {
            System.loadLibrary("irisInterfaceJNI");
            Log.d(TAG, "Bibliothèque native irisInterfaceJNI chargée avec succès");
        } catch (UnsatisfiedLinkError e) {
            Log.e(TAG, "ERREUR: Impossible de charger irisInterfaceJNI: " + e.getMessage());
            throw e;
        }
    }
}
