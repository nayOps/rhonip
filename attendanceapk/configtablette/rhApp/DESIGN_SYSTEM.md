# Design System - Ministère de la Jeunesse RDC
## Basé sur la Charte Graphique Officielle du Gouvernement RDC (Février 2022)

---

## 🎨 COULEURS OFFICIELLES

### Couleurs Tricolores du Drapeau RDC

#### Bleu (Couleur Principale)
- **Web** : `#0095c9`
- **Pantone** : 801C
- **RGB** : R:0, G:149, B:201
- **Usage** : Couleur principale, éléments de navigation, liens

#### Jaune (Couleur Secondaire)
- **Web** : `#fff24b`
- **Pantone** : 803C
- **RGB** : R:255, G:242, B:75
- **Usage** : Accents, badges, highlights, éléments importants

#### Rouge (Couleur Accent)
- **Web** : `#db3832`
- **Pantone** : 485C
- **RGB** : R:219, G:56, B:50
- **Usage** : Alertes, urgences, éléments d'attention

### Couleurs Complémentaires

#### Bleu Foncé (Navigation, Headers)
- **Web** : `#17418a`
- **Usage** : Headers, navigation principale, fonds sombres

#### Bleu Ciel (Variante)
- **Web** : `#0f89cb`
- **Usage** : Liens hover, éléments interactifs

#### Gris Neutres
- **Gris Foncé** : `#323230` - Textes principaux
- **Gris Moyen** : `#405D64` - Textes secondaires
- **Gris Clair** : `#E0E0E0` - Bordures, séparateurs
- **Gris Très Clair** : `#F5F5F5` - Fond de sections

#### Autres Couleurs (si nécessaire)
- **Vert** : `#65b32e` - Succès, validations
- **Orange** : `#ed7016` - Warnings, notifications
- **Violet** : `#9C0055` - Éléments spéciaux

---

## 📝 TYPOGRAPHIE

### Police Principale : Cooper Hewitt
**Source** : Google Fonts ou système local

#### Variantes Utilisées
- **Cooper Hewitt Bold** : Titres principaux, Headers
- **Cooper Hewitt Medium** : Sous-titres, textes importants
- **Cooper Hewitt Regular** : Corps de texte (si disponible)

#### Hiérarchie Typographique

##### Titres
- **H1** : Cooper Hewitt Bold, 48px (3rem) / 64px (4rem) desktop
- **H2** : Cooper Hewitt Bold, 36px (2.25rem) / 48px (3rem) desktop
- **H3** : Cooper Hewitt Bold, 28px (1.75rem) / 32px (2rem) desktop
- **H4** : Cooper Hewitt Bold, 24px (1.5rem)
- **H5** : Cooper Hewitt Medium, 20px (1.25rem)
- **H6** : Cooper Hewitt Medium, 18px (1.125rem)

##### Corps de Texte
- **Body Large** : 18px (1.125rem), line-height: 1.6
- **Body** : 16px (1rem), line-height: 1.5
- **Body Small** : 14px (0.875rem), line-height: 1.4
- **Caption** : 12px (0.75rem), line-height: 1.3

### Police de Fallback
- **Sans-serif** : Inter, Roboto, -apple-system, system-ui, sans-serif
- Pour les cas où Cooper Hewitt n'est pas disponible

---

## 🏗️ ARCHITECTURE DE LA MARQUE

### Éléments de Base

#### 1. Bloc-Armoirie
- **Position** : Toujours à gauche
- **Usage** : Logo officiel du ministère
- **Caractéristiques** : Ne change pas, représente l'autorité de l'État

#### 2. Ligne d'État
- **Forme** : Barre verticale tricolore
- **Ordre** : Bleu (haut), Jaune (milieu), Rouge (bas)
- **Proportions** : 3 couleurs à parts égales
- **Usage** : Séparateur vertical, élément identitaire
- **Largeur** : X (unité de base)
- **Zone de sécurité** : 4X de chaque côté

#### 3. Intitulé Officiel
- **Typographie** : Cooper Hewitt (Bold)
- **Taille** : Homogène pour tous les ministères
- **Usage** : Nom de la structure émettrice

---

## 📐 ESPACEMENTS

### Système 8px
- **4px** : Espacements très serrés (icônes, badges)
- **8px** : Espacements serrés
- **16px** : Espacements moyens (espacement entre éléments)
- **24px** : Espacements larges (espacement entre sections)
- **32px** : Espacements très larges
- **48px** : Espacements extra larges
- **64px** : Espacements entre grandes sections
- **96px** : Espacements maximum (hero sections)

---

## 🎯 BORDURES & RAYONS

### Bordures
- **1px** : Bordures fines (séparateurs, inputs)
- **2px** : Bordures standards (cards, boutons)
- **4px** : Bordures épaisses (éléments importants)

### Rayons (Border Radius)
- **0px** : Pas d'arrondi (design plat strict)
- **4px** : Arrondi minimal (cards, inputs)
- **8px** : Arrondi standard (boutons, badges)
- **12px** : Arrondi large (éléments spéciaux)

**Note** : Design flat = pas de rounded-xl excessifs

---

## 🌑 OMBRES

### Niveaux d'Ombres (Subtiles)
- **Shadow Sm** : `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- **Shadow Md** : `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)`
- **Shadow Lg** : `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)`

**Principe** : Ombres très subtiles pour profondeur, pas de blur

---

## 🎨 COMPOSANTS UI

### Buttons
- **Style** : Flat, bordures nettes
- **Couleurs** : Bleu (#0095c9), Jaune (#fff24b), Rouge (#db3832), Gris
- **Padding** : 12px 24px (md), 16px 32px (lg)
- **Border Radius** : 4px ou 8px
- **Hover** : Légère élévation (shadow-md)
- **Pas d'animations excessives**

### Cards
- **Background** : Blanc (#ffffff)
- **Border** : 1px #E0E0E0
- **Border Radius** : 4px
- **Shadow** : Shadow-sm (hover: shadow-md)
- **Padding** : 16px, 24px, ou 32px selon contexte

### Badges
- **Style** : Minimaliste, plat
- **Couleurs** : Bleu, Jaune, Rouge avec fond clair (10% opacity)
- **Border Radius** : 12px (pill shape)
- **Padding** : 4px 12px

### Inputs
- **Border** : 1px #E0E0E0
- **Border Radius** : 4px
- **Focus** : Border 2px #0095c9, shadow-sm
- **Padding** : 12px 16px

### Separators
- **Ligne d'État** : Barre verticale tricolore (Bleu, Jaune, Rouge)
- **Ligne simple** : 1px #E0E0E0
- **Ligne épaisse** : 2px #0095c9

---

## 📱 RESPONSIVE BREAKPOINTS

- **Mobile** : < 640px
- **Tablet** : 640px - 1024px
- **Desktop** : > 1024px
- **Large Desktop** : > 1280px

---

## 🎭 ÉTATS & INTERACTIONS

### Hover States
- **Transitions** : 200ms ease-in-out (max)
- **Élévation** : Légère ombre
- **Couleur** : Légèrement plus foncée ou claire

### Focus States
- **Outline** : 2px solid #0095c9
- **Outline Offset** : 2px
- **Accessibilité** : Toujours visible

### Active States
- **Échelle** : 0.98 (légère compression)
- **Transition** : 100ms

### Disabled States
- **Opacity** : 0.5
- **Cursor** : not-allowed
- **Pas d'interaction**

---

## 🏛️ ÉLÉMENTS INSTITUTIONNELS

### Header
- **Barre supérieure** : Ligne d'État (tricolore) horizontale
- **Logo** : Bloc-armoirie à gauche
- **Navigation** : Horizontal, épurée
- **Background** : Blanc ou #F5F5F5
- **Shadow** : Subtile au scroll

### Footer
- **Background** : #323230 (gris foncé) ou #17418a (bleu foncé)
- **Couleur texte** : Blanc ou #F5F5F5
- **Ligne d'État** : Barre horizontale tricolore en bas
- **Structure** : 4 colonnes (Accès Rapides, Sites Institutionnels, Contact, Réseaux)

### Hero Section
- **Background** : Couleur unie (#0095c9) ou image officielle
- **Typographie** : Cooper Hewitt Bold, grande taille
- **Ligne d'État** : Élément décoratif

---

## ✅ RÈGLES D'USAGE

### Do's ✅
- Utiliser les 3 couleurs tricolores (Bleu, Jaune, Rouge)
- Respecter la Ligne d'État (tricolore verticale/horizontale)
- Utiliser Cooper Hewitt pour les titres
- Design flat, épuré, professionnel
- Espacements généreux
- Contraste élevé (WCAG AA)

### Don'ts ❌
- Pas de gradients complexes
- Pas de blur effects
- Pas d'animations excessives
- Pas de couleurs non-officielles
- Pas de typographie non-approuvée
- Pas d'arrondis excessifs

---

## 📋 VARIABLES CSS

```css
:root {
  /* Couleurs Tricolores Officielles */
  --color-blue-rdc: #0095c9;
  --color-yellow-rdc: #fff24b;
  --color-red-rdc: #db3832;
  
  /* Couleurs Complémentaires */
  --color-blue-dark: #17418a;
  --color-blue-sky: #0f89cb;
  --color-green: #65b32e;
  --color-orange: #ed7016;
  
  /* Gris */
  --color-gray-dark: #323230;
  --color-gray-medium: #405D64;
  --color-gray-light: #E0E0E0;
  --color-gray-very-light: #F5F5F5;
  
  /* Fond et Texte */
  --color-background: #ffffff;
  --color-text: #323230;
  --color-text-secondary: #405D64;
  
  /* Typographie */
  --font-primary: 'Cooper Hewitt', -apple-system, system-ui, sans-serif;
  --font-display: 'Cooper Hewitt', var(--font-primary);
  
  /* Espacements */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;
  --spacing-4xl: 96px;
  
  /* Ombres */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  
  /* Bordures */
  --border-width-thin: 1px;
  --border-width-medium: 2px;
  --border-width-thick: 4px;
  --border-color: #E0E0E0;
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
}
```

---

**Ce design system est basé sur la Charte Graphique Officielle du Gouvernement de la RDC (Février 2022)**

