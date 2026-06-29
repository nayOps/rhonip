/** Règles d'affichage et de validation — formulaire biographique (étape base) */

export type BaseFormStrata =
  | 'ENFANT'
  | 'ELEVES'
  | 'ELECTEUR'
  | 'PNC'
  | 'FARDC'
  | 'PRISON'
  | 'REFUGIE'
  | 'DEPLACE'
  | 'ETRANGER'
  | 'DIASPORA';

export const MINOR_STRATA: BaseFormStrata[] = ['ENFANT', 'ELEVES'];

export const FILIATION_REQUIRED_STRATA: BaseFormStrata[] = ['ENFANT', 'ELEVES'];

/** Filiation affichée (optionnelle ou obligatoire) */
export const FILIATION_VISIBLE_STRATA: BaseFormStrata[] = [
  'ENFANT',
  'ELEVES',
  'REFUGIE',
  'DEPLACE',
];

export const ETUDES_REQUIRED_STRATA: BaseFormStrata[] = ['ELEVES'];

export const TUTEUR_VISIBLE_STRATA: BaseFormStrata[] = ['ENFANT', 'ELEVES', 'REFUGIE'];

export const PROFESSION_PRESET_STRATA: Partial<Record<BaseFormStrata, string>> = {
  ENFANT: 'Enfant / mineur',
  ELEVES: 'Élève',
  PNC: 'Policier',
  FARDC: 'Militaire',
  PRISON: 'Détenu',
};

export interface PieceTypeOption {
  value: string;
  label: string;
}

const ALL_PIECES: PieceTypeOption[] = [
  { value: 'Acte de naissance', label: 'Acte de naissance' },
  { value: 'Jugement supplétif', label: 'Jugement supplétif' },
  { value: "Carte d'électeur", label: "Carte d'électeur" },
  { value: 'Certificat de nationalité', label: 'Certificat de nationalité' },
  { value: 'Passeport', label: 'Passeport' },
  { value: "Carte d'élève", label: "Carte d'élève / étudiant" },
  { value: 'Carte réfugié / document HCR', label: 'Carte réfugié / document HCR' },
  { value: 'Autre', label: 'Autre' },
];

const PIECES_BY_STRATA: Partial<Record<BaseFormStrata, string[]>> = {
  ENFANT: ['Acte de naissance', 'Jugement supplétif', 'Autre'],
  ELEVES: ['Acte de naissance', "Carte d'élève", 'Jugement supplétif', 'Autre'],
  ELECTEUR: ['Acte de naissance', "Carte d'électeur", 'Certificat de nationalité', 'Passeport', 'Autre'],
  ETRANGER: ['Passeport', 'Certificat de nationalité', 'Jugement supplétif', 'Autre'],
  REFUGIE: ['Carte réfugié / document HCR', 'Passeport', 'Jugement supplétif', 'Acte de naissance', 'Autre'],
  DEPLACE: ['Acte de naissance', 'Jugement supplétif', 'Certificat de nationalité', 'Autre'],
  DIASPORA: ['Passeport', 'Certificat de nationalité', 'Acte de naissance', 'Autre'],
  PNC: ['Acte de naissance', 'Certificat de nationalité', 'Autre'],
  FARDC: ['Acte de naissance', 'Certificat de nationalité', 'Autre'],
  PRISON: ['Acte de naissance', 'Jugement supplétif', 'Autre'],
};

export function isSituationFamilialeActive(strata: BaseFormStrata | null): boolean {
  return Boolean(strata && !MINOR_STRATA.includes(strata));
}

export function isFiliationRequired(strata: BaseFormStrata | null): boolean {
  return Boolean(strata && FILIATION_REQUIRED_STRATA.includes(strata));
}

export function isFiliationSectionVisible(strata: BaseFormStrata | null): boolean {
  return Boolean(strata && FILIATION_VISIBLE_STRATA.includes(strata));
}

export function isEtudesRequired(strata: BaseFormStrata | null): boolean {
  return Boolean(strata && ETUDES_REQUIRED_STRATA.includes(strata));
}

export function isEtudesSectionVisible(strata: BaseFormStrata | null): boolean {
  return isEtudesRequired(strata);
}

export function isTuteurVisible(strata: BaseFormStrata | null): boolean {
  return Boolean(strata && TUTEUR_VISIBLE_STRATA.includes(strata));
}

export function isProfessionSectionPreset(strata: BaseFormStrata | null): boolean {
  return Boolean(strata && strata in PROFESSION_PRESET_STRATA);
}

export function getPresetProfession(strata: BaseFormStrata | null): string {
  if (!strata) return '';
  return PROFESSION_PRESET_STRATA[strata] ?? '';
}

export function getPieceTypeOptions(strata: BaseFormStrata | null): PieceTypeOption[] {
  if (!strata) return ALL_PIECES;
  const allowed = PIECES_BY_STRATA[strata];
  if (!allowed) return ALL_PIECES;
  return ALL_PIECES.filter((p) => allowed.includes(p.value));
}

export function getDefaultPieceType(strata: BaseFormStrata | null): string {
  const options = getPieceTypeOptions(strata);
  if (strata === 'ELEVES') return "Carte d'élève";
  if (strata === 'ELECTEUR') return "Carte d'électeur";
  if (strata === 'REFUGIE') return 'Carte réfugié / document HCR';
  if (strata === 'ETRANGER' || strata === 'DIASPORA') return 'Passeport';
  return options[0]?.value ?? 'Acte de naissance';
}

export interface StrataRuleLine {
  label: string;
  required: boolean;
}

export function getStrataRuleLines(strata: BaseFormStrata): StrataRuleLine[] {
  const lines: StrataRuleLine[] = [
    { label: 'Identité et origine / résidence', required: true },
  ];

  if (isSituationFamilialeActive(strata)) {
    lines.push({ label: 'Situation familiale (adultes / majeurs)', required: false });
  } else {
    lines.push({ label: 'Situation familiale — non requise (mineur / élève)', required: false });
  }

  if (isFiliationSectionVisible(strata)) {
    lines.push({
      label: isFiliationRequired(strata)
        ? 'Filiation (parents) — obligatoire'
        : 'Filiation — recommandée (réfugié / déplacé)',
      required: isFiliationRequired(strata),
    });
  } else {
    lines.push({ label: 'Filiation — non applicable', required: false });
  }

  if (isEtudesSectionVisible(strata)) {
    lines.push({ label: 'Études faites — obligatoire', required: true });
  } else {
    lines.push({ label: 'Études faites — non applicable', required: false });
  }

  if (isProfessionSectionPreset(strata)) {
    lines.push({ label: `Profession — préremplie (${getPresetProfession(strata)})`, required: false });
  } else {
    lines.push({ label: 'Profession / occupation', required: false });
  }

  lines.push({ label: `Pièce d'identité — ${getDefaultPieceType(strata)} suggéré`, required: true });
  lines.push({ label: 'Éléments signalétiques (handicap)', required: false });

  return lines;
}

export function validateBaseForm(
  strata: BaseFormStrata | null,
  formData: Record<string, unknown>
): boolean {
  if (!strata) return false;

  const str = (k: string) => String(formData[k] ?? '').trim();

  if (!str('prenom') || !str('nom') || !str('dateNaissance') || !str('lieuNaissance')) {
    return false;
  }

  if (isFiliationRequired(strata)) {
    if (!str('pereNom') || !str('mereNom')) return false;
  }

  if (isEtudesRequired(strata)) {
    if (!str('niveauEtude')) return false;
  }

  if (isSituationFamilialeActive(strata) && formData.etatMatrimonial === 'Marié(e)') {
    if (!str('conjointNom')) return false;
  }

  if (!str('typePiece')) return false;

  return true;
}
