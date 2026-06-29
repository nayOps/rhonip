// Service API pour le système FGP

import { 
  EnrollmentRequest, 
  EnrollmentResponse, 
  SearchFilters, 
  SearchResult, 
  DashboardStats,
  ApiResponse,
  PaginatedResponse,
  PersonCore,
  AuditTrail
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Erreur inconnue' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // ===== ENROLLMENT SERVICES =====

  async submitEnrollment(enrollment: EnrollmentRequest): Promise<EnrollmentResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/enrolments/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(enrollment),
    });

    return this.handleResponse<EnrollmentResponse>(response);
  }

  async getEnrollmentStatus(nin: string): Promise<EnrollmentResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/enrolments/${nin}/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<EnrollmentResponse>(response);
  }

  // ===== SEARCH SERVICES =====

  async searchPersons(filters: SearchFilters, page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<SearchResult>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== undefined && value !== '')
      ),
    });

    const response = await fetch(`${this.baseUrl}/api/v1/search/?${params}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<PaginatedResponse<SearchResult>>(response);
  }

  async getPersonByNin(nin: string): Promise<PersonCore> {
    const response = await fetch(`${this.baseUrl}/api/v1/persons/${nin}/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<PersonCore>(response);
  }

  // ===== DASHBOARD SERVICES =====

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await fetch(`${this.baseUrl}/api/v1/dashboard/stats/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<DashboardStats>(response);
  }

  // ===== BIOMETRIC SERVICES =====

  async uploadBiometric(data: FormData): Promise<{ uri: string; quality: number }> {
    const headers = this.getHeaders();
    delete headers['Content-Type']; // Let browser set boundary for FormData

    const response = await fetch(`${this.baseUrl}/api/v1/biometric/upload/`, {
      method: 'POST',
      headers,
      body: data,
    });

    return this.handleResponse<{ uri: string; quality: number }>(response);
  }

  async verifyBiometric(nin: string, biometricData: FormData): Promise<{ match: boolean; score: number }> {
    const headers = this.getHeaders();
    delete headers['Content-Type'];

    const response = await fetch(`${this.baseUrl}/api/v1/biometric/verify/${nin}/`, {
      method: 'POST',
      headers,
      body: biometricData,
    });

    return this.handleResponse<{ match: boolean; score: number }>(response);
  }

  // ===== DOCUMENT SERVICES =====

  async uploadDocument(file: File, type: string): Promise<{ uri: string; hash: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const headers = this.getHeaders();
    delete headers['Content-Type'];

    const response = await fetch(`${this.baseUrl}/api/v1/documents/upload/`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return this.handleResponse<{ uri: string; hash: string }>(response);
  }

  // ===== EXTENSION SERVICES =====

  async getExtensions(nin: string): Promise<Record<string, any>> {
    const response = await fetch(`${this.baseUrl}/api/v1/extensions/${nin}/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<Record<string, any>>(response);
  }

  async updateExtension(nin: string, strata: string, data: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/extensions/${nin}/${strata}/`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse<any>(response);
  }

  // ===== AUDIT SERVICES =====

  async getAuditTrail(nin: string): Promise<AuditTrail[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/audit/${nin}/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<AuditTrail[]>(response);
  }

  // ===== AUTHENTICATION SERVICES =====

  async login(username: string, password: string): Promise<{ token: string; user: any }> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ username, password }),
    });

    const data = await this.handleResponse<{ token: string; user: any }>(response);
    this.token = data.token;
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', data.token);
    }

    return data;
  }

  async logout(): Promise<void> {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // ===== UTILITY METHODS =====

  setAuthToken(token: string): void {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }
}

export const apiService = new ApiService();
export default apiService;
