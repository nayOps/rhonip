package com.onip.enroll.widgets;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.View;
import androidx.core.content.ContextCompat;
import com.onip.enroll.R;
import com.onip.enroll.utils.FingerCatalog;
import java.util.HashSet;
import java.util.Set;

/**
 * Grille alignée des 10 doigts (2 rangées × 5 colonnes) — sans forme de main.
 */
public class HandDiagramView extends View {

    private static final String[] SHORT_LABELS = {
            "Aur.", "Ann.", "Maj.", "Idx", "Pou.",
            "Pou.", "Idx", "Maj.", "Ann.", "Aur."
    };

    private final Paint cellPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint strokePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint indexPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint labelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint sectionPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private int currentFingerIndex = 0;
    private final Set<String> completedCodes = new HashSet<>();

    public HandDiagramView(Context context) {
        super(context);
        init();
    }

    public HandDiagramView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        cellPaint.setStyle(Paint.Style.FILL);

        strokePaint.setStyle(Paint.Style.STROKE);
        strokePaint.setStrokeWidth(4f);

        indexPaint.setTextAlign(Paint.Align.CENTER);
        indexPaint.setFakeBoldText(true);

        labelPaint.setTextAlign(Paint.Align.CENTER);

        sectionPaint.setTextAlign(Paint.Align.CENTER);
        sectionPaint.setFakeBoldText(true);
        sectionPaint.setColor(ContextCompat.getColor(getContext(), R.color.rdc_blue));
    }

    public void updateState(int currentIndex, Set<String> completedRegisterCodes) {
        currentFingerIndex = currentIndex;
        completedCodes.clear();
        if (completedRegisterCodes != null) {
            completedCodes.addAll(completedRegisterCodes);
        }
        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        float w = getWidth();
        float h = getHeight();
        float padding = Math.min(w, h) * 0.04f;
        float sectionHeight = h * 0.10f;
        float rowHeight = (h - sectionHeight * 2f - padding * 3f) / 2f;
        float cellGap = padding * 0.5f;
        float cellWidth = (w - padding * 2f - cellGap * 4f) / 5f;

        float textScale = Math.min(cellWidth, rowHeight);
        indexPaint.setTextSize(textScale * 0.28f);
        labelPaint.setTextSize(textScale * 0.18f);
        sectionPaint.setTextSize(Math.min(w, h) * 0.045f);

        drawRow(canvas, padding, padding, cellWidth, rowHeight, cellGap, 0, 5, "MAIN GAUCHE");
        float row2Top = padding + sectionHeight + rowHeight + padding;
        drawRow(canvas, padding, row2Top, cellWidth, rowHeight, cellGap, 5, 10, "MAIN DROITE");
    }

    private void drawRow(Canvas canvas, float left, float top, float cellWidth, float rowHeight,
                         float cellGap, int startIndex, int endIndex, String sectionTitle) {
        float w = getWidth();
        canvas.drawText(sectionTitle, w / 2f, top + rowHeight * 0.08f, sectionPaint);

        float cellsTop = top + rowHeight * 0.14f;
        float cellBodyHeight = rowHeight * 0.86f;

        for (int i = startIndex; i < endIndex; i++) {
            int col = i - startIndex;
            float x = left + col * (cellWidth + cellGap);
            FingerCatalog.FingerDef def = FingerCatalog.ALL_TEN[i];

            int fillColor;
            if (completedCodes.contains(def.registerCode)) {
                fillColor = ContextCompat.getColor(getContext(), R.color.success);
            } else if (i == currentFingerIndex) {
                fillColor = ContextCompat.getColor(getContext(), R.color.rdc_yellow);
            } else {
                fillColor = ContextCompat.getColor(getContext(), R.color.border_medium);
            }

            RectF rect = new RectF(x, cellsTop, x + cellWidth, cellsTop + cellBodyHeight);
            float radius = Math.min(cellWidth, cellBodyHeight) * 0.12f;

            cellPaint.setColor(fillColor);
            canvas.drawRoundRect(rect, radius, radius, cellPaint);

            if (i == currentFingerIndex) {
                strokePaint.setColor(ContextCompat.getColor(getContext(), R.color.rdc_blue));
                canvas.drawRoundRect(rect, radius, radius, strokePaint);
            }

            int textColor = (i == currentFingerIndex)
                    ? ContextCompat.getColor(getContext(), R.color.text_primary)
                    : ContextCompat.getColor(getContext(), R.color.white);
            indexPaint.setColor(textColor);
            labelPaint.setColor(textColor);

            float centerX = rect.centerX();
            float centerY = rect.centerY();
            canvas.drawText(String.valueOf(i + 1), centerX, centerY - labelPaint.getTextSize() * 0.2f, indexPaint);
            canvas.drawText(SHORT_LABELS[i], centerX, centerY + indexPaint.getTextSize() * 0.55f, labelPaint);
        }
    }
}
