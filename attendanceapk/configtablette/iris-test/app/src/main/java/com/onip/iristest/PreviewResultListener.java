package com.onip.iristest;

import android.graphics.Bitmap;

/**
 * Interface pour les callbacks de prévisualisation
 */
public interface PreviewResultListener {
    void onPreviewResult(Bitmap leftImage, Bitmap rightImage);
}
