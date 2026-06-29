'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ENROLLMENT_FIELD_GRID_CLASS,
  ENROLLMENT_INPUT_CLASS,
  ENROLLMENT_LABEL_CLASS,
} from '@/lib/enrollment-ui';
import { EMPLOYEE_FIELD_LABELS } from '@/lib/employee-form-config';
import {
  fetchGeographyOptions,
  type GeographyOption,
  type GeographyVillageOption,
} from '@/services/rh-api';

export interface GeographyFormValues {
  home_province?: string;
  home_territory?: string;
  home_sector?: string;
  home_groupement?: string;
  home_village?: string;
}

interface GeographyCascadeFieldsProps {
  values: GeographyFormValues;
  provinces: GeographyOption[];
  onChange: (field: keyof GeographyFormValues, value: string) => void;
  onBulkChange: (patch: Partial<GeographyFormValues>) => void;
}

function GeoSelect({
  label,
  value,
  options,
  disabled,
  onChange,
}: {
  label: string;
  value?: string;
  options: GeographyOption[];
  disabled?: boolean;
  onChange: (v: string) => void;
}) {
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

export default function GeographyCascadeFields({
  values,
  provinces,
  onChange,
  onBulkChange,
}: GeographyCascadeFieldsProps) {
  const [territories, setTerritories] = useState<GeographyOption[]>([]);
  const [sectors, setSectors] = useState<GeographyOption[]>([]);
  const [groupements, setGroupements] = useState<GeographyOption[]>([]);
  const [villages, setVillages] = useState<GeographyVillageOption[]>([]);
  const [villageQuery, setVillageQuery] = useState('');
  const [searchResults, setSearchResults] = useState<GeographyVillageOption[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  const provinceId = values.home_province || '';
  const territoryId = values.home_territory || '';
  const sectorId = values.home_sector || '';
  const groupementId = values.home_groupement || '';

  useEffect(() => {
    if (!provinceId) {
      setTerritories([]);
      return;
    }
    let cancelled = false;
    void fetchGeographyOptions('territory', { province_id: provinceId }).then((rows) => {
      if (!cancelled) setTerritories(rows);
    });
    return () => {
      cancelled = true;
    };
  }, [provinceId]);

  useEffect(() => {
    if (!territoryId) {
      setSectors([]);
      return;
    }
    let cancelled = false;
    void fetchGeographyOptions('sector', { territory_id: territoryId }).then((rows) => {
      if (!cancelled) setSectors(rows);
    });
    return () => {
      cancelled = true;
    };
  }, [territoryId]);

  useEffect(() => {
    if (!sectorId) {
      setGroupements([]);
      return;
    }
    let cancelled = false;
    void fetchGeographyOptions('groupement', { sector_id: sectorId }).then((rows) => {
      if (!cancelled) setGroupements(rows);
    });
    return () => {
      cancelled = true;
    };
  }, [sectorId]);

  useEffect(() => {
    if (!groupementId) {
      setVillages([]);
      return;
    }
    let cancelled = false;
    void fetchGeographyOptions('village', { groupement_id: groupementId }).then((rows) => {
      if (!cancelled) setVillages(rows as GeographyVillageOption[]);
    });
    return () => {
      cancelled = true;
    };
  }, [groupementId]);

  useEffect(() => {
    const q = villageQuery.trim();
    if (q.length < 2) {
      setSearchResults([]);
      return;
    }
    let cancelled = false;
    const timer = setTimeout(() => {
      void fetchGeographyOptions('village', {
        q,
        province_id: provinceId || undefined,
        territory_id: territoryId || undefined,
        sector_id: sectorId || undefined,
      }).then((rows) => {
        if (!cancelled) {
          setSearchResults(rows as GeographyVillageOption[]);
          setSearchOpen(true);
        }
      });
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [villageQuery, provinceId, territoryId, sectorId]);

  useEffect(() => {
    const onDocClick = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const clearBelowProvince = useCallback(() => {
    onBulkChange({
      home_territory: '',
      home_sector: '',
      home_groupement: '',
      home_village: '',
    });
    setVillageQuery('');
  }, [onBulkChange]);

  const clearBelowTerritory = useCallback(() => {
    onBulkChange({
      home_sector: '',
      home_groupement: '',
      home_village: '',
    });
    setVillageQuery('');
  }, [onBulkChange]);

  const clearBelowSector = useCallback(() => {
    onBulkChange({
      home_groupement: '',
      home_village: '',
    });
    setVillageQuery('');
  }, [onBulkChange]);

  const clearBelowGroupement = useCallback(() => {
    onBulkChange({ home_village: '' });
    setVillageQuery('');
  }, [onBulkChange]);

  const applyVillageSelection = (item: GeographyVillageOption) => {
    onBulkChange({
      home_province: String(item.province_id),
      home_territory: String(item.territory_id),
      home_sector: String(item.sector_id),
      home_groupement: String(item.groupement_id),
      home_village: String(item.id),
    });
    setVillageQuery(item.label || item.name);
    setSearchOpen(false);
  };

  const selectedVillageLabel =
    villages.find((v) => String(v.id) === values.home_village)?.name ||
    searchResults.find((v) => String(v.id) === values.home_village)?.label ||
    '';

  return (
    <>
      <div className={ENROLLMENT_FIELD_GRID_CLASS}>
        <GeoSelect
          label={EMPLOYEE_FIELD_LABELS.home_province}
          value={values.home_province}
          options={provinces}
          onChange={(v) => {
            onChange('home_province', v);
            clearBelowProvince();
          }}
        />
        <GeoSelect
          label={EMPLOYEE_FIELD_LABELS.home_territory}
          value={values.home_territory}
          options={territories}
          disabled={!provinceId}
          onChange={(v) => {
            onChange('home_territory', v);
            clearBelowTerritory();
          }}
        />
        <GeoSelect
          label={EMPLOYEE_FIELD_LABELS.home_sector}
          value={values.home_sector}
          options={sectors}
          disabled={!territoryId}
          onChange={(v) => {
            onChange('home_sector', v);
            clearBelowSector();
          }}
        />
        <GeoSelect
          label={EMPLOYEE_FIELD_LABELS.home_groupement}
          value={values.home_groupement}
          options={groupements}
          disabled={!sectorId}
          onChange={(v) => {
            onChange('home_groupement', v);
            clearBelowGroupement();
          }}
        />
      </div>

      <div className="mt-3" ref={searchRef}>
        <label className={ENROLLMENT_LABEL_CLASS}>
          {EMPLOYEE_FIELD_LABELS.home_village}
          <span className="ml-1 text-xs font-normal text-gray-500">
            (recherche rapide, min. 2 lettres)
          </span>
          <input
            type="text"
            className={ENROLLMENT_INPUT_CLASS}
            value={villageQuery || selectedVillageLabel}
            placeholder="Tapez le nom du village…"
            onChange={(e) => {
              setVillageQuery(e.target.value);
              if (!e.target.value.trim()) {
                onChange('home_village', '');
              }
            }}
            onFocus={() => {
              if (searchResults.length) setSearchOpen(true);
            }}
          />
        </label>
        {searchOpen && searchResults.length > 0 && (
          <ul className="mt-1 max-h-48 overflow-y-auto rounded border border-gray-200 bg-white shadow-sm">
            {searchResults.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className="w-full px-3 py-2 text-left text-sm hover:bg-blue-50"
                  onClick={() => applyVillageSelection(item)}
                >
                  {item.label || item.name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {groupementId && villages.length > 0 && (
        <div className="mt-3">
          <GeoSelect
            label={`${EMPLOYEE_FIELD_LABELS.home_village} (liste du groupement)`}
            value={values.home_village}
            options={villages}
            onChange={(v) => {
              onChange('home_village', v);
              const picked = villages.find((row) => String(row.id) === v);
              setVillageQuery(picked?.name || '');
            }}
          />
        </div>
      )}
    </>
  );
}
