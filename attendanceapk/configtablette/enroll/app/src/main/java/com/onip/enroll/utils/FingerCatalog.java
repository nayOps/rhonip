package com.onip.enroll.utils;

/**
 * Catalogue des 10 doigts — codes register + noms tablette Morpho.
 */
public final class FingerCatalog {

    public static final class FingerDef {
        public final String registerCode;
        public final String tabletName;
        public final String label;

        FingerDef(String registerCode, String tabletName, String label) {
            this.registerCode = registerCode;
            this.tabletName = tabletName;
            this.label = label;
        }
    }

    public static final FingerDef[] ALL_TEN = new FingerDef[]{
            new FingerDef("LEFT_LITTLE", "Auriculaire_Gauche", "Auriculaire gauche"),
            new FingerDef("LEFT_RING", "Annulaire_Gauche", "Annulaire gauche"),
            new FingerDef("LEFT_MIDDLE", "Majeur_Gauche", "Majeur gauche"),
            new FingerDef("LEFT_INDEX", "Index_Gauche", "Index gauche"),
            new FingerDef("LEFT_THUMB", "Pouce_Gauche", "Pouce gauche"),
            new FingerDef("RIGHT_THUMB", "Pouce_Droit", "Pouce droit"),
            new FingerDef("RIGHT_INDEX", "Index_Droit", "Index droit"),
            new FingerDef("RIGHT_MIDDLE", "Majeur_Droit", "Majeur droit"),
            new FingerDef("RIGHT_RING", "Annulaire_Droit", "Annulaire droit"),
            new FingerDef("RIGHT_LITTLE", "Auriculaire_Droit", "Auriculaire droit"),
    };

    private FingerCatalog() {
    }
}
