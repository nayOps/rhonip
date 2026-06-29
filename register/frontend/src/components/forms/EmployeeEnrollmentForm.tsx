'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  ENROLLMENT_FIELD_GRID_CLASS,
  ENROLLMENT_FORM_BODY_CLASS,
  ENROLLMENT_FORM_SCROLL_CLASS,
  ENROLLMENT_INPUT_CLASS,
  ENROLLMENT_LABEL_CLASS,
  ENROLLMENT_SECTION_CLASS,
  ENROLLMENT_SECTION_TITLE_CLASS,
  ENROLLMENT_SHELL_CLASS,
} from '@/lib/enrollment-ui';
import GeographyCascadeFields from '@/components/forms/GeographyCascadeFields';
import EnrollmentFormCard from '@/components/enrollment/EnrollmentFormCard';
import EnrollmentFooter from '@/components/enrollment/EnrollmentFooter';
import { fetchGuichetRefs, fetchEmployeeByMatricule, type GuichetRefs } from '@/services/rh-api';
import {
  EMPLOYEE_FIELD_LABELS,
  EMPLOYEE_GENDER_OPTIONS,
  EMPLOYEE_MARITAL_OPTIONS,
  EMPLOYEE_PAYMENT_OPTIONS,
  ID_CARD_TYPE_OPTIONS,
  isRhFormValid,
} from '@/lib/employee-form-config';
import { COUNTRY_OPTIONS, DEFAULT_COUNTRY } from '@/lib/countries';
import {
  DEFAULT_EMPLOYEE_FORM,
  type EmployeeChildRow,
  type EmployeeDocumentRow,
  type EmployeeEducationRow,
  type EmployeeExperienceRow,
  type EmployeeFormData,
} from '@/types/employee';

export type { EmployeeFormData } from '@/types/employee';

interface EmployeeEnrollmentFormProps {
  onNext: (data: EmployeeFormData) => void;
  onCancel?: () => void;
  initialData?: Partial<EmployeeFormData> | null;
}

type FormTab = 'employe' | 'enfants' | 'educations' | 'experiences' | 'documents';

const TAB_LABELS: Record<FormTab, string> = {
  employe: 'Employé',
  enfants: 'Enfants',
  educations: 'Educations',
  experiences: 'Experiences',
  documents: 'Documents',
};

function CountrySelect({
  field,
  value,
  onChange,
}: {
  field: 'citizenship' | 'home_country';
  value?: string;
  onChange: (v: string) => void;
}) {
  const label = EMPLOYEE_FIELD_LABELS[field];
  const options = COUNTRY_OPTIONS;
  const current = value || DEFAULT_COUNTRY;
  const hasCurrent = options.some((o) => o.value === current);

  return (
    <label className={ENROLLMENT_LABEL_CLASS}>
      {label}
      <select
        className={ENROLLMENT_INPUT_CLASS}
        value={current}
        onChange={(e) => onChange(e.target.value)}
      >
        {!hasCurrent && current ? (
          <option value={current}>{current}</option>
        ) : null}
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function RefSelect({
  field,
  value,
  options,
  onChange,
  disabled,
}: {
  field: keyof typeof EMPLOYEE_FIELD_LABELS;
  value?: string;
  options: { id: number; name: string }[];
  onChange: (v: string) => void;
  disabled?: boolean;
}) {
  const label = EMPLOYEE_FIELD_LABELS[field];
  return (
    <label className={ENROLLMENT_LABEL_CLASS}>
      {label}
      <select
        className={ENROLLMENT_INPUT_CLASS}
        value={value || ''}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">---------</option>
        {options.map((o) => (
          <option key={o.id} value={String(o.id)}>
            {o.name}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function EmployeeEnrollmentForm({
  onNext,
  onCancel,
  initialData,
}: EmployeeEnrollmentFormProps) {
  const [activeTab, setActiveTab] = useState<FormTab>('employe');
  const [refs, setRefs] = useState<GuichetRefs | null>(null);
  const [refsError, setRefsError] = useState(false);
  const [matriculeHint, setMatriculeHint] = useState<string | null>(null);
  const [formData, setFormData] = useState<EmployeeFormData>({
    ...DEFAULT_EMPLOYEE_FORM,
    ...(initialData || {}),
  });

  useEffect(() => {
    if (!initialData?.registration_number) return;
    setFormData({ ...DEFAULT_EMPLOYEE_FORM, ...initialData });
  }, [initialData]);

  useEffect(() => {
    fetchGuichetRefs().then((data) => {
      const empty =
        !data.directions.length &&
        !data.grades.length &&
        !data.agreements.length;
      setRefsError(empty);
      setRefs(data);
    });
  }, []);

  useEffect(() => {
    const matricule = String(formData.registration_number ?? '').trim();
    if (matricule.length < 6) {
      setMatriculeHint(null);
      return;
    }
    let cancelled = false;
    const timer = setTimeout(() => {
      void fetchEmployeeByMatricule(matricule).then((data) => {
        if (cancelled) return;
        if (!data) {
          setMatriculeHint(null);
          return;
        }
        setMatriculeHint(
          data.nom_postnom ||
            [data.last_name, data.middle_name, data.first_name].filter(Boolean).join(' ')
        );
        setFormData((prev) => {
          if (String(prev.registration_number ?? '').trim() !== matricule) return prev;
          return {
            ...prev,
            first_name: prev.first_name || data.first_name || '',
            middle_name: prev.middle_name || data.middle_name || '',
            last_name: prev.last_name || data.last_name || '',
            gender: (prev.gender || data.gender || 'male') as EmployeeFormData['gender'],
            marital_status:
              prev.marital_status ||
              (data.marital_status as EmployeeFormData['marital_status']) ||
              'single',
            payment_method:
              prev.payment_method ||
              (data.payment_method as EmployeeFormData['payment_method']) ||
              'bank',
            payer_name: prev.payer_name || data.payer_name || '',
            payment_account: prev.payment_account || data.payment_account || '',
            branch: prev.branch || (data.branch != null ? String(data.branch) : ''),
            direction: prev.direction || (data.direction != null ? String(data.direction) : ''),
            sub_direction:
              prev.sub_direction || (data.sub_direction != null ? String(data.sub_direction) : ''),
            service: prev.service || (data.service != null ? String(data.service) : ''),
            grade: prev.grade || (data.grade != null ? String(data.grade) : ''),
            designation:
              prev.designation || (data.designation != null ? String(data.designation) : ''),
            home_province:
              prev.home_province || (data.home_province != null ? String(data.home_province) : ''),
            home_territory:
              prev.home_territory ||
              (data.home_territory != null ? String(data.home_territory) : ''),
            home_sector:
              prev.home_sector || (data.home_sector != null ? String(data.home_sector) : ''),
            home_groupement:
              prev.home_groupement ||
              (data.home_groupement != null ? String(data.home_groupement) : ''),
            home_village:
              prev.home_village || (data.home_village != null ? String(data.home_village) : ''),
          };
        });
      });
    }, 450);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [formData.registration_number]);

  const handleChange = (field: keyof EmployeeFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleBulkChange = (patch: Partial<EmployeeFormData>) => {
    setFormData((prev) => ({ ...prev, ...patch }));
  };

  const readFileAsBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ''));
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  const handlePhoto = async (file: File | undefined) => {
    if (!file) {
      setFormData((prev) => ({ ...prev, photo_name: '', photo_base64: '' }));
      return;
    }
    const b64 = await readFileAsBase64(file);
    setFormData((prev) => ({ ...prev, photo_name: file.name, photo_base64: b64 }));
  };

  const handleAppointmentLetter = async (file: File | undefined) => {
    if (!file) {
      setFormData((prev) => ({
        ...prev,
        appointment_letter_name: '',
        appointment_letter_base64: '',
      }));
      return;
    }
    const b64 = await readFileAsBase64(file);
    setFormData((prev) => ({
      ...prev,
      appointment_letter_name: file.name,
      appointment_letter_base64: b64,
    }));
  };

  const updateInlineRow = <T,>(
    key: 'children' | 'educations' | 'experiences' | 'employee_documents',
    index: number,
    patch: Partial<T>
  ) => {
    setFormData((prev) => {
      const rows = [...(prev[key] || [])] as T[];
      rows[index] = { ...rows[index], ...patch };
      return { ...prev, [key]: rows };
    });
  };

  const addInlineRow = (
    key: 'children' | 'educations' | 'experiences' | 'employee_documents',
    empty: EmployeeChildRow | EmployeeEducationRow | EmployeeExperienceRow | EmployeeDocumentRow
  ) => {
    setFormData((prev) => ({
      ...prev,
      [key]: [...(prev[key] || []), empty],
    }));
  };

  const removeInlineRow = (
    key: 'children' | 'educations' | 'experiences' | 'employee_documents',
    index: number
  ) => {
    setFormData((prev) => ({
      ...prev,
      [key]: (prev[key] || []).filter((_, i) => i !== index),
    }));
  };

  const filteredSubDirections = useMemo(() => {
    if (!refs || !formData.direction) return refs?.sub_directions || [];
    const dirId = Number(formData.direction);
    return refs.sub_directions.filter((s) => s.direction_id === dirId);
  }, [refs, formData.direction]);

  const filteredServices = useMemo(() => {
    if (!refs || !formData.sub_direction) return refs?.services || [];
    const subId = Number(formData.sub_direction);
    return refs.services.filter((s) => s.sub_direction_id === subId);
  }, [refs, formData.sub_direction]);

  const isValid = isRhFormValid(formData);

  const renderEmploye = () => (
    <>
      <section className={ENROLLMENT_SECTION_CLASS}>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <label className={`${ENROLLMENT_LABEL_CLASS} md:col-span-2`}>
            {EMPLOYEE_FIELD_LABELS.photo}
            <input
              type="file"
              accept="image/*"
              className={ENROLLMENT_INPUT_CLASS}
              onChange={(e) => void handlePhoto(e.target.files?.[0])}
            />
            {formData.photo_name ? (
              <span className="text-xs text-gray-500 mt-1">{formData.photo_name}</span>
            ) : (
              <span className="text-xs text-gray-400 mt-1">No file chosen</span>
            )}
            <span className="text-xs text-gray-500 mt-1 block">
              Une photo peut aussi être capturée à l&apos;étape biométrique (prioritaire).
            </span>
          </label>
        </div>
      </section>

      <section className={ENROLLMENT_SECTION_CLASS}>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.registration_number}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.registration_number}
              onChange={(e) => handleChange('registration_number', e.target.value)}
            />
            {matriculeHint && (
              <span className="text-xs text-emerald-700 mt-1 block">
                Agent trouvé RH : {matriculeHint}
              </span>
            )}
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.social_security_number}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.social_security_number || ''}
              onChange={(e) => handleChange('social_security_number', e.target.value)}
            />
          </label>
        </div>
      </section>

      <section className={ENROLLMENT_SECTION_CLASS}>
        {refsError && (
          <p className="mb-3 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
            Référentiels RH indisponibles — vérifiez que le service RH (port 8100) est démarré.
          </p>
        )}
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <RefSelect
            field="branch"
            value={formData.branch}
            options={refs?.branches || []}
            onChange={(v) => handleChange('branch', v)}
          />
          <RefSelect
            field="agreement"
            value={formData.agreement}
            options={refs?.agreements || []}
            onChange={(v) => handleChange('agreement', v)}
          />
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.date_of_join}
            <input
              type="date"
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.date_of_join || ''}
              onChange={(e) => handleChange('date_of_join', e.target.value)}
            />
          </label>
          <RefSelect
            field="direction"
            value={formData.direction}
            options={refs?.directions || []}
            onChange={(v) => {
              handleChange('direction', v);
              handleChange('sub_direction', '');
              handleChange('service', '');
            }}
          />
          <RefSelect
            field="sub_direction"
            value={formData.sub_direction}
            options={filteredSubDirections}
            disabled={!formData.direction}
            onChange={(v) => {
              handleChange('sub_direction', v);
              handleChange('service', '');
            }}
          />
          <RefSelect
            field="service"
            value={formData.service}
            options={filteredServices}
            disabled={!formData.sub_direction}
            onChange={(v) => handleChange('service', v)}
          />
          <RefSelect
            field="grade"
            value={formData.grade}
            options={refs?.grades || []}
            onChange={(v) => handleChange('grade', v)}
          />
          <RefSelect
            field="designation"
            value={formData.designation}
            options={refs?.designations || []}
            onChange={(v) => handleChange('designation', v)}
          />
        </div>
      </section>

      <section className={ENROLLMENT_SECTION_CLASS}>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.first_name}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.first_name}
              onChange={(e) => handleChange('first_name', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.middle_name}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.middle_name || ''}
              onChange={(e) => handleChange('middle_name', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.last_name}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.last_name}
              onChange={(e) => handleChange('last_name', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.gender}
            <select
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.gender || ''}
              onChange={(e) => handleChange('gender', e.target.value)}
            >
              <option value="">---------</option>
              {EMPLOYEE_GENDER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.date_of_birth}
            <input
              type="date"
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.date_of_birth || ''}
              onChange={(e) => handleChange('date_of_birth', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.place_of_birth}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.place_of_birth || ''}
              onChange={(e) => handleChange('place_of_birth', e.target.value)}
            />
          </label>
        </div>
      </section>

      <section className={ENROLLMENT_SECTION_CLASS}>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <CountrySelect
            field="citizenship"
            value={formData.citizenship}
            onChange={(v) => handleChange('citizenship', v)}
          />
          <CountrySelect
            field="home_country"
            value={formData.home_country}
            onChange={(v) => handleChange('home_country', v)}
          />
        </div>
        <GeographyCascadeFields
          values={{
            home_province: formData.home_province,
            home_territory: formData.home_territory,
            home_sector: formData.home_sector,
            home_groupement: formData.home_groupement,
            home_village: formData.home_village,
          }}
          provinces={refs?.provinces || []}
          onChange={handleChange}
          onBulkChange={handleBulkChange}
        />
      </section>

      <section className={ENROLLMENT_SECTION_CLASS}>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.type_of_identity}
            <select
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.type_of_identity || ''}
              onChange={(e) => handleChange('type_of_identity', e.target.value)}
            >
              <option value="">---------</option>
              {ID_CARD_TYPE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.identity_number}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.identity_number || ''}
              onChange={(e) => handleChange('identity_number', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.date_of_issue}
            <input
              type="date"
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.date_of_issue || ''}
              onChange={(e) => handleChange('date_of_issue', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.date_of_expiry}
            <input
              type="date"
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.date_of_expiry || ''}
              onChange={(e) => handleChange('date_of_expiry', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.place_of_issue}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.place_of_issue || ''}
              onChange={(e) => handleChange('place_of_issue', e.target.value)}
            />
          </label>
        </div>
      </section>

      <section className={ENROLLMENT_SECTION_CLASS}>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.appointment_letter}
            <input
              type="file"
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              className={ENROLLMENT_INPUT_CLASS}
              onChange={(e) => void handleAppointmentLetter(e.target.files?.[0])}
            />
            {formData.appointment_letter_name ? (
              <span className="text-xs text-gray-500 mt-1">{formData.appointment_letter_name}</span>
            ) : (
              <span className="text-xs text-gray-400 mt-1">No file chosen</span>
            )}
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.appointment_number}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.appointment_number || ''}
              onChange={(e) => handleChange('appointment_number', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.marital_status}
            <select
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.marital_status || ''}
              onChange={(e) => handleChange('marital_status', e.target.value)}
            >
              <option value="">---------</option>
              {EMPLOYEE_MARITAL_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.spouse}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.spouse || ''}
              onChange={(e) => handleChange('spouse', e.target.value)}
              disabled={formData.marital_status !== 'maried'}
            />
          </label>
        </div>
      </section>

      <section className={`${ENROLLMENT_SECTION_CLASS} bg-gray-50 border border-gray-200 p-5`}>
        <h3 className={ENROLLMENT_SECTION_TITLE_CLASS}>Contact</h3>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.telephone_number}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              placeholder="+243..."
              value={formData.telephone_number || ''}
              onChange={(e) => handleChange('telephone_number', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.mobile_number}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              placeholder="+243..."
              value={formData.mobile_number || ''}
              onChange={(e) => handleChange('mobile_number', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.email_professional}
            <input
              type="email"
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.email_professional || ''}
              onChange={(e) => handleChange('email_professional', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.email}
            <input
              type="email"
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.email || ''}
              onChange={(e) => handleChange('email', e.target.value)}
            />
          </label>
          <label className={`${ENROLLMENT_LABEL_CLASS} md:col-span-2`}>
            {EMPLOYEE_FIELD_LABELS.physical_address}
            <textarea
              className={ENROLLMENT_INPUT_CLASS}
              rows={2}
              value={formData.physical_address || ''}
              onChange={(e) => handleChange('physical_address', e.target.value)}
            />
          </label>
          <label className={`${ENROLLMENT_LABEL_CLASS} md:col-span-2`}>
            {EMPLOYEE_FIELD_LABELS.emergency_information}
            <textarea
              className={ENROLLMENT_INPUT_CLASS}
              rows={2}
              value={formData.emergency_information || ''}
              onChange={(e) => handleChange('emergency_information', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.emergency_contact}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.emergency_contact || ''}
              onChange={(e) => handleChange('emergency_contact', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.emergency_phone}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              placeholder="+243..."
              value={formData.emergency_phone || ''}
              onChange={(e) => handleChange('emergency_phone', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.relationship}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.relationship || ''}
              onChange={(e) => handleChange('relationship', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.refering_doctor}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.refering_doctor || ''}
              onChange={(e) => handleChange('refering_doctor', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.refering_doctor_phone}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.refering_doctor_phone || ''}
              onChange={(e) => handleChange('refering_doctor_phone', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.refering_doctor_email}
            <input
              type="email"
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.refering_doctor_email || ''}
              onChange={(e) => handleChange('refering_doctor_email', e.target.value)}
            />
          </label>
        </div>
      </section>

      <section className={ENROLLMENT_SECTION_CLASS}>
        <div className={ENROLLMENT_FIELD_GRID_CLASS}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.payment_method}
            <select
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.payment_method || ''}
              onChange={(e) => handleChange('payment_method', e.target.value)}
            >
              <option value="">---------</option>
              {EMPLOYEE_PAYMENT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.payer_name}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.payer_name || ''}
              onChange={(e) => handleChange('payer_name', e.target.value)}
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.payment_account}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={formData.payment_account || ''}
              onChange={(e) => handleChange('payment_account', e.target.value)}
            />
          </label>
          <label className={`${ENROLLMENT_LABEL_CLASS} md:col-span-2`}>
            {EMPLOYEE_FIELD_LABELS.comment}
            <textarea
              className={ENROLLMENT_INPUT_CLASS}
              rows={2}
              value={formData.comment || ''}
              onChange={(e) => handleChange('comment', e.target.value)}
            />
          </label>
        </div>
      </section>
    </>
  );

  const renderEnfants = () => (
    <section className={ENROLLMENT_SECTION_CLASS}>
      <div className="flex items-center justify-between mb-2">
        <h3 className={ENROLLMENT_SECTION_TITLE_CLASS}>{TAB_LABELS.enfants}</h3>
        <button
          type="button"
          className="text-sm text-blue-700 hover:underline"
          onClick={() => addInlineRow('children', { full_name: '' })}
        >
          + Ajouter
        </button>
      </div>
      {(formData.children || []).length === 0 && (
        <p className="text-sm text-gray-500">Aucun enfant — cliquez sur Ajouter.</p>
      )}
      {(formData.children || []).map((row, i) => (
          <div key={`child-${i}`} className={`${ENROLLMENT_FIELD_GRID_CLASS} mb-4 border-b border-gray-100 pb-4`}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.child_full_name}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={row.full_name}
              onChange={(e) =>
                updateInlineRow<EmployeeChildRow>('children', i, { full_name: e.target.value })
              }
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.child_date_of_birth}
            <input
              type="date"
              className={ENROLLMENT_INPUT_CLASS}
              value={row.date_of_birth || ''}
              onChange={(e) =>
                updateInlineRow<EmployeeChildRow>('children', i, { date_of_birth: e.target.value })
              }
            />
          </label>
          <button
            type="button"
            className="text-sm text-red-600 self-end"
            onClick={() => removeInlineRow('children', i)}
          >
            Supprimer
          </button>
        </div>
      ))}
    </section>
  );

  const renderEducations = () => (
    <section className={ENROLLMENT_SECTION_CLASS}>
      <div className="flex items-center justify-between mb-2">
        <h3 className={ENROLLMENT_SECTION_TITLE_CLASS}>{TAB_LABELS.educations}</h3>
        <button
          type="button"
          className="text-sm text-blue-700 hover:underline"
          onClick={() => addInlineRow('educations', { institution: '', degree: '' })}
        >
          + Ajouter
        </button>
      </div>
      {(formData.educations || []).length === 0 && (
        <p className="text-sm text-gray-500">Aucune formation — cliquez sur Ajouter.</p>
      )}
      {(formData.educations || []).map((row, i) => (
          <div key={`edu-${i}`} className={`${ENROLLMENT_FIELD_GRID_CLASS} mb-4 border-b border-gray-100 pb-4`}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.education_institution}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={row.institution || ''}
              onChange={(e) =>
                updateInlineRow<EmployeeEducationRow>('educations', i, { institution: e.target.value })
              }
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.education_degree}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={row.degree || ''}
              onChange={(e) =>
                updateInlineRow<EmployeeEducationRow>('educations', i, { degree: e.target.value })
              }
            />
          </label>
          <button
            type="button"
            className="text-sm text-red-600 self-end"
            onClick={() => removeInlineRow('educations', i)}
          >
            Supprimer
          </button>
        </div>
      ))}
    </section>
  );

  const renderExperiences = () => (
    <section className={ENROLLMENT_SECTION_CLASS}>
      <div className="flex items-center justify-between mb-2">
        <h3 className={ENROLLMENT_SECTION_TITLE_CLASS}>{TAB_LABELS.experiences}</h3>
        <button
          type="button"
          className="text-sm text-blue-700 hover:underline"
          onClick={() => addInlineRow('experiences', { organization: '', position: '' })}
        >
          + Ajouter
        </button>
      </div>
      {(formData.experiences || []).length === 0 && (
        <p className="text-sm text-gray-500">Aucune expérience — cliquez sur Ajouter.</p>
      )}
      {(formData.experiences || []).map((row, i) => (
          <div key={`exp-${i}`} className={`${ENROLLMENT_FIELD_GRID_CLASS} mb-4 border-b border-gray-100 pb-4`}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.experience_organization}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={row.organization || ''}
              onChange={(e) =>
                updateInlineRow<EmployeeExperienceRow>('experiences', i, { organization: e.target.value })
              }
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.experience_position}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={row.position || ''}
              onChange={(e) =>
                updateInlineRow<EmployeeExperienceRow>('experiences', i, { position: e.target.value })
              }
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.experience_start_date}
            <input
              type="date"
              className={ENROLLMENT_INPUT_CLASS}
              value={row.start_date || ''}
              onChange={(e) =>
                updateInlineRow<EmployeeExperienceRow>('experiences', i, { start_date: e.target.value })
              }
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.experience_end_date}
            <input
              type="date"
              className={ENROLLMENT_INPUT_CLASS}
              value={row.end_date || ''}
              onChange={(e) =>
                updateInlineRow<EmployeeExperienceRow>('experiences', i, { end_date: e.target.value })
              }
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.experience_photo}
            <input
              type="file"
              accept="image/*"
              className={ENROLLMENT_INPUT_CLASS}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                void readFileAsBase64(file).then((b64) =>
                  updateInlineRow<EmployeeExperienceRow>('experiences', i, {
                    photo_name: file.name,
                    photo_base64: b64,
                  })
                );
              }}
            />
            {row.photo_name && (
              <span className="text-xs text-gray-500 mt-1">{row.photo_name}</span>
            )}
          </label>
          <button
            type="button"
            className="text-sm text-red-600 self-end"
            onClick={() => removeInlineRow('experiences', i)}
          >
            Supprimer
          </button>
        </div>
      ))}
    </section>
  );

  const renderDocuments = () => (
    <section className={ENROLLMENT_SECTION_CLASS}>
      <div className="flex items-center justify-between mb-2">
        <h3 className={ENROLLMENT_SECTION_TITLE_CLASS}>{TAB_LABELS.documents}</h3>
        <button
          type="button"
          className="text-sm text-blue-700 hover:underline"
          onClick={() => addInlineRow('employee_documents', { name: '' })}
        >
          + Ajouter
        </button>
      </div>
      {(formData.employee_documents || []).length === 0 && (
        <p className="text-sm text-gray-500">Aucun document — cliquez sur Ajouter.</p>
      )}
      {(formData.employee_documents || []).map((row, i) => (
          <div key={`doc-${i}`} className={`${ENROLLMENT_FIELD_GRID_CLASS} mb-4 border-b border-gray-100 pb-4`}>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.document_name}
            <input
              className={ENROLLMENT_INPUT_CLASS}
              value={row.name}
              onChange={(e) =>
                updateInlineRow<EmployeeDocumentRow>('employee_documents', i, { name: e.target.value })
              }
            />
          </label>
          <label className={ENROLLMENT_LABEL_CLASS}>
            {EMPLOYEE_FIELD_LABELS.document_file}
            <input
              type="file"
              className={ENROLLMENT_INPUT_CLASS}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                void readFileAsBase64(file).then((b64) =>
                  updateInlineRow<EmployeeDocumentRow>('employee_documents', i, {
                    file_name: file.name,
                    file_base64: b64,
                  })
                );
              }}
            />
            {row.file_name && (
              <span className="text-xs text-gray-500 mt-1">{row.file_name}</span>
            )}
          </label>
          <button
            type="button"
            className="text-sm text-red-600 self-end"
            onClick={() => removeInlineRow('employee_documents', i)}
          >
            Supprimer
          </button>
        </div>
      ))}
    </section>
  );

  const tabContent: Record<FormTab, () => React.ReactNode> = {
    employe: renderEmploye,
    enfants: renderEnfants,
    educations: renderEducations,
    experiences: renderExperiences,
    documents: renderDocuments,
  };

  return (
    <EnrollmentFormCard
      title="Fiche employé ONIP"
      subtitle="Alignée sur le formulaire RH Payday — tous les champs sont optionnels"
      className="flex-1 min-h-0"
    >
      <div className={`${ENROLLMENT_SHELL_CLASS} h-full min-h-0 flex flex-col`}>
        <nav className="flex flex-wrap gap-1 px-4 pt-3 border-b border-gray-200 bg-white">
          {(Object.keys(TAB_LABELS) as FormTab[]).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-2 text-sm font-medium rounded-t transition ${
                activeTab === tab
                  ? 'bg-blue-50 text-blue-800 border border-b-white border-gray-200 -mb-px'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </nav>

        <div className={ENROLLMENT_FORM_BODY_CLASS}>
          <div className={ENROLLMENT_FORM_SCROLL_CLASS}>{tabContent[activeTab]()}</div>
        </div>

        <EnrollmentFooter
          onCancel={onCancel}
          onNext={() => isValid && onNext(formData)}
          nextDisabled={!isValid}
          nextLabel="Continuer vers biométrie"
        />
      </div>
    </EnrollmentFormCard>
  );
}
