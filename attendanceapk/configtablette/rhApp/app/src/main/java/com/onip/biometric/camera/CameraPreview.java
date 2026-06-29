package com.onip.biometric.camera;

import android.content.Context;
import android.graphics.Rect;
import android.hardware.Camera;
import android.util.Log;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Classe de prévisualisation de caméra avec auto-focus tactile
 * Basée sur l'exemple SDK officiel
 */
public class CameraPreview extends SurfaceView implements SurfaceHolder.Callback {
    private static final String TAG = "CameraPreview";
    
    private SurfaceHolder mHolder;
    private Camera mCamera;
    private Camera.AutoFocusCallback autoFocusCallback;

    public CameraPreview(Context context, Camera camera) {
        super(context);
        mCamera = camera;

        mHolder = getHolder();
        mHolder.addCallback(this);
        mHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);

        autoFocusCallback = new Camera.AutoFocusCallback() {
            @Override
            public void onAutoFocus(boolean success, Camera camera) {
                if (success) {
                    mCamera.cancelAutoFocus();
                    Log.d(TAG, "Auto-focus réussi");
                } else {
                    Log.d(TAG, "Auto-focus échoué");
                }
            }
        };
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        if (event.getAction() == MotionEvent.ACTION_DOWN) {
            float x = event.getX();
            float y = event.getY();

            int border = 100;
            int max_x = getWidth();
            int max_y = getHeight();
            float left_point_x = 100;
            float left_point_y = 100;
            float right_point_x = 100;
            float right_point_y = 100;

            if (x < border)
                left_point_x = x;
            if (y < border)
                left_point_y = y;
            if (x > max_x - border)
                right_point_x = max_x - x;
            if (y > max_y - border)
                right_point_y = max_y - y;

            Rect touchRect = new Rect(
                    (int) (x - left_point_x),
                    (int) (y - left_point_y),
                    (int) (x + right_point_x),
                    (int) (y + right_point_y));

            final Rect targetFocusRect = new Rect(
                    touchRect.left * 2000 / this.getWidth() - 1000,
                    touchRect.top * 2000 / this.getHeight() - 1000,
                    touchRect.right * 2000 / this.getWidth() - 1000,
                    touchRect.bottom * 2000 / this.getHeight() - 1000);

            doTouchFocus(targetFocusRect);
        }

        return super.onTouchEvent(event);
    }

    public void doTouchFocus(final Rect focusRect) {
        try {
            List<Camera.Area> focusList = new ArrayList<Camera.Area>();
            Camera.Area focusArea = new Camera.Area(focusRect, 1000);
            focusList.add(focusArea);

            Camera.Parameters param = mCamera.getParameters();
            param.setFocusAreas(focusList);
            param.setMeteringAreas(focusList);
            mCamera.setParameters(param);

            mCamera.autoFocus(autoFocusCallback);
            Log.d(TAG, "Auto-focus déclenché");
        } catch (Exception e) {
            Log.e(TAG, "Erreur auto-focus: " + e.getMessage());
        }
    }

    public void setCamera(Camera cam) {
        mCamera = cam;
        if (mCamera != null) {
            requestLayout();
        }
    }

    public void surfaceCreated(SurfaceHolder holder) {
        try {
            mCamera.setPreviewDisplay(holder);
            mCamera.startPreview();
            Log.d(TAG, "Preview démarré");
        } catch (IOException e) {
            Log.d(TAG, "Erreur preview: " + e.getMessage());
        }
    }

    public void surfaceDestroyed(SurfaceHolder holder) {
        // Libération gérée dans l'activité
    }

    public void surfaceChanged(SurfaceHolder holder, int format, int w, int h) {
        if (mHolder.getSurface() == null) {
            return;
        }

        try {
            mCamera.stopPreview();
        } catch (Exception e) {
            // Ignorer
        }

        try {
            mCamera.setPreviewDisplay(mHolder);
            mCamera.startPreview();
            Log.d(TAG, "Preview redémarré - " + w + "x" + h);
        } catch (Exception e) {
            Log.d(TAG, "Erreur redémarrage preview: " + e.getMessage());
        }
    }
}
