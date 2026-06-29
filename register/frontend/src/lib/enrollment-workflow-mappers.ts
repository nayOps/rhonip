import type { WorkflowStep } from '@/components/forms/EnrollmentWorkflow.types';
import { visitedRhActiveStepsUpTo } from '@/lib/rh-guichet-workflow';

function pick(data: Record<string, unknown>, camel: string, snake?: string): string {
  const v = data[camel] ?? data[snake ?? camel];
  if (v == null) return '';
  return String(v);
}

export function visitedStepsUpTo(step: WorkflowStep): WorkflowStep[] {
  return visitedRhActiveStepsUpTo(step);
}

export function defaultBaseFormState() {
  return {
    prenom: '',
    nom: '',
    postnom: '',
    autresNoms: '',
    sexe: 'M',
    dateNaissance: '',
    lieuNaissance: '',
    nationalite: 'Congolaise',
    taille: '',
    couleurYeux: '',
    groupeSanguin: '',
    telephone: '',
    email: '',
    boitePostale: '',
    origineProvince: '',
    origineVille: '',
    origineCommune: '',
    origineQuartier: '',
    residenceProvince: '',
    residenceVille: '',
    residenceCommune: '',
    residenceQuartier: '',
    residenceRue: '',
    etatMatrimonial: 'Célibataire',
    nombreEnfants: '',
    conjointNom: '',
    conjointNationalite: '',
    conjointLieuNaissance: '',
    pereStatut: 'En vie',
    pereNom: '',
    pereNationalite: '',
    pereNIN: '',
    pereLieuNaissance: '',
    mereStatut: 'En vie',
    mereNom: '',
    mereNationalite: '',
    mereNIN: '',
    mereLieuNaissance: '',
    tuteurNom: '',
    tuteurNationalite: '',
    tuteurLien: '',
    niveauEtude: '',
    etablissement: '',
    anneeObtention: '',
    domaine: '',
    profession: '',
    employeur: '',
    fonction: '',
    typePiece: 'Acte de naissance',
    numeroPiece: '',
    datePiece: '',
    handicap: 'Aucun',
    handicapDetails: '',
  };
}

export function mapWorkflowToBaseFormState(data: Record<string, unknown> | null | undefined) {
  if (!data) return defaultBaseFormState();
  return {
    ...defaultBaseFormState(),
    prenom: pick(data, 'prenom'),
    nom: pick(data, 'nom'),
    postnom: pick(data, 'postnom'),
    autresNoms: pick(data, 'autresNoms', 'autres_noms'),
    sexe: pick(data, 'sexe') || 'M',
    dateNaissance: pick(data, 'dateNaissance', 'date_naissance'),
    lieuNaissance: pick(data, 'lieuNaissance', 'lieu_naissance'),
    nationalite: pick(data, 'nationalite') || 'Congolaise',
    taille: pick(data, 'taille'),
    couleurYeux: pick(data, 'couleurYeux', 'couleur_yeux'),
    groupeSanguin: pick(data, 'groupeSanguin', 'groupe_sanguin'),
    telephone: pick(data, 'telephone'),
    email: pick(data, 'email'),
    boitePostale: pick(data, 'boitePostale', 'boite_postale'),
    origineProvince: pick(data, 'origineProvince', 'origine_province'),
    origineVille: pick(data, 'origineVille', 'origine_ville'),
    origineCommune: pick(data, 'origineCommune', 'origine_commune'),
    origineQuartier: pick(data, 'origineQuartier', 'origine_quartier'),
    residenceProvince: pick(data, 'residenceProvince', 'residence_province'),
    residenceVille: pick(data, 'residenceVille', 'residence_ville'),
    residenceCommune: pick(data, 'residenceCommune', 'residence_commune'),
    residenceQuartier: pick(data, 'residenceQuartier', 'residence_quartier'),
    residenceRue: pick(data, 'residenceRue', 'residence_rue'),
    etatMatrimonial: pick(data, 'etatMatrimonial', 'etat_matrimonial') || 'Célibataire',
    nombreEnfants: pick(data, 'nombreEnfants', 'nombre_enfants'),
    conjointNom: pick(data, 'conjointNom', 'conjoint_nom'),
    conjointNationalite: pick(data, 'conjointNationalite', 'conjoint_nationalite'),
    conjointLieuNaissance: pick(data, 'conjointLieuNaissance', 'conjoint_lieu_naissance'),
    pereStatut: pick(data, 'pereStatut', 'pere_statut') || 'En vie',
    pereNom: pick(data, 'pereNom', 'pere_nom'),
    pereNationalite: pick(data, 'pereNationalite', 'pere_nationalite'),
    pereNIN: pick(data, 'pereNIN', 'pere_nin'),
    pereLieuNaissance: pick(data, 'pereLieuNaissance', 'pere_lieu_naissance'),
    mereStatut: pick(data, 'mereStatut', 'mere_statut') || 'En vie',
    mereNom: pick(data, 'mereNom', 'mere_nom'),
    mereNationalite: pick(data, 'mereNationalite', 'mere_nationalite'),
    mereNIN: pick(data, 'mereNIN', 'mere_nin'),
    mereLieuNaissance: pick(data, 'mereLieuNaissance', 'mere_lieu_naissance'),
    tuteurNom: pick(data, 'tuteurNom', 'tuteur_nom'),
    tuteurNationalite: pick(data, 'tuteurNationalite', 'tuteur_nationalite'),
    tuteurLien: pick(data, 'tuteurLien', 'tuteur_lien'),
    niveauEtude: pick(data, 'niveauEtude', 'niveau_etude'),
    etablissement: pick(data, 'etablissement'),
    anneeObtention: pick(data, 'anneeObtention', 'annee_obtention'),
    domaine: pick(data, 'domaine'),
    profession: pick(data, 'profession'),
    employeur: pick(data, 'employeur'),
    fonction: pick(data, 'fonction'),
    typePiece: pick(data, 'typePiece', 'type_piece') || 'Acte de naissance',
    numeroPiece: pick(data, 'numeroPiece', 'numero_piece'),
    datePiece: pick(data, 'datePiece', 'date_piece'),
    handicap: pick(data, 'handicap') || 'Aucun',
    handicapDetails: pick(data, 'handicapDetails', 'handicap_details'),
  };
}

export function strataFromWorkflowData(data: Record<string, unknown> | null | undefined): string | null {
  if (!data?.strata) return null;
  const s = data.strata;
  if (Array.isArray(s)) return s[0] ? String(s[0]) : null;
  return String(s);
}
