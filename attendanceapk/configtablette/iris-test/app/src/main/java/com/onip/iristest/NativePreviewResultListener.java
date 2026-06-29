package com.onip.iristest;

import android.graphics.Bitmap;

/**
 * Interface native pour les callbacks de preview d'iris
 * Basée sur le SDK MorphoTablet réel
 */
public interface NativePreviewResultListener {
    
    class IrisPosition {
        public int x, y, radius;
    }

    void postResult(Bitmap frame);
    Bitmap provideNextBitmap();
}