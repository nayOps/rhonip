package com.onip.enroll.fingerprint;

import android.app.Activity;
import android.graphics.Bitmap;
import android.util.Log;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import com.morpho.morphosmart.sdk.CallbackMessage;
import com.morpho.morphosmart.sdk.MorphoImage;
import java.nio.ByteBuffer;
import java.util.Observable;
import java.util.Observer;

/**
 * Observer pour gérer les callbacks du SDK MorphoSmart
 * Basé sur l'exemple CBM du SDK
 */
public class FingerprintProcessObserver implements Observer {
    
    private static final String TAG = "FingerprintObserver";
    
    private Activity activity;
    private TextView statusTextView;
    private ImageView fingerprintImageView;
    private ProgressBar qualityProgressBar;
    
    public FingerprintProcessObserver(Activity activity, TextView statusTextView, 
                                     ImageView fingerprintImageView, ProgressBar qualityProgressBar) {
        this.activity = activity;
        this.statusTextView = statusTextView;
        this.fingerprintImageView = fingerprintImageView;
        this.qualityProgressBar = qualityProgressBar;
    }
    
    @Override
    public void update(Observable o, Object arg) {
        if (arg instanceof CallbackMessage) {
            CallbackMessage callbackMessage = (CallbackMessage) arg;
            
            Log.d(TAG, "Process message: " + callbackMessage.getMessageType() + " - " + callbackMessage.getMessage());
            
            // Traiter les différents types de messages
            int messageType = callbackMessage.getMessageType();
            if (messageType == 1) { // COMMAND_CMD
                handleCommandMessage(callbackMessage);
            } else if (messageType == 2) { // IMAGE_CMD
                handleImageMessage(callbackMessage);
            } else if (messageType == 4) { // CODEQUALITY
                handleQualityMessage(callbackMessage);
            } else if (messageType == 8) { // DETECTQUALITY
                handleDetectQualityMessage(callbackMessage);
            } else {
                Log.d(TAG, "Unknown callback type: " + messageType);
            }
        }
    }
    
    private void handleCommandMessage(CallbackMessage message) {
        Object command = message.getMessage();
        Log.d(TAG, "Command: " + command);

        activity.runOnUiThread(() -> {
            if (statusTextView != null) {
                String commandText = "Lecture en cours...";
                if (command instanceof Integer) {
                    commandText = getCommandText((Integer) command);
                }
                statusTextView.setText(commandText);
            }
        });
    }
    
    private String getCommandText(Integer command) {
        switch (command) {
            case 0: return "Retirez votre doigt";
            case 1: return "Déplacez le doigt vers le haut";
            case 2: return "Déplacez le doigt vers le bas";
            case 3: return "Déplacez le doigt vers la gauche";
            case 4: return "Déplacez le doigt vers la droite";
            case 5: return "Appuyez plus fort";
            case 6: return "Retirez votre doigt";
            case 7: return "Retirez votre doigt";
            case 8: return "Doigt détecté ✓";
            default: return "Commande: " + command;
        }
    }
    
    private void handleImageMessage(CallbackMessage message) {
        Log.d(TAG, "Image callback received");
        
        try {
            // Convertir l'image en Bitmap pour l'affichage
            byte[] imageData = (byte[]) message.getMessage();
            MorphoImage morphoImage = MorphoImage.getMorphoImageFromLive(imageData);
            
            int imageRowNumber = morphoImage.getMorphoImageHeader().getNbRow();
            int imageColumnNumber = morphoImage.getMorphoImageHeader().getNbColumn();
            
            final Bitmap imageBitmap = Bitmap.createBitmap(imageColumnNumber, imageRowNumber, Bitmap.Config.ALPHA_8);
            imageBitmap.copyPixelsFromBuffer(ByteBuffer.wrap(morphoImage.getImage(), 0, morphoImage.getImage().length));
            
            activity.runOnUiThread(() -> {
                if (fingerprintImageView != null) {
                    fingerprintImageView.setImageBitmap(imageBitmap);
                }
                if (statusTextView != null) {
                    statusTextView.setText("Image en temps réel...");
                }
            });
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur traitement image: " + e.getMessage());
        }
    }
    
    private void handleQualityMessage(CallbackMessage message) {
        Object quality = message.getMessage();
        Log.d(TAG, "Quality: " + quality);
        
        activity.runOnUiThread(() -> {
            if (qualityProgressBar != null && quality instanceof Integer) {
                qualityProgressBar.setProgress((Integer) quality);
            }
            if (statusTextView != null) {
                statusTextView.setText("Qualité: " + quality + "%");
            }
        });
    }
    
    private void handleDetectQualityMessage(CallbackMessage message) {
        Object detectQuality = message.getMessage();
        Log.d(TAG, "Detect Quality: " + detectQuality);
        
        activity.runOnUiThread(() -> {
            if (statusTextView != null) {
                statusTextView.setText("Détection: " + detectQuality + "%");
            }
        });
    }
}

