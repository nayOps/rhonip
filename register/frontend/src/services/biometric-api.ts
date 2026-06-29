// Service API pour les opérations biométriques
const BIOMETRIC_API_URL = process.env.NEXT_PUBLIC_BIOMETRIC_URL || 'http://localhost:8003';

export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
}

export interface IrisCaptureSession {
  id: string;
  enrollment_session_id: string;
  status: string;
  created_at: string;
}

export interface IrisCaptureData {
  id: string;
  session_id: string;
  eye: 'LEFT' | 'RIGHT';
  eye_region?: string;
  quality_percentage?: number;
  status: string;
}

class BiometricApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = BIOMETRIC_API_URL;
  }

  // Iris Capture API
  async startIrisSession(enrollmentSessionId: string): Promise<ApiResponse<IrisCaptureSession>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/biometrics/iris/sessions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enrollment_session_id: enrollmentSessionId,
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Erreur lors du démarrage de la session');
      }

      return {
        success: true,
        data: data,
        message: 'Session démarrée avec succès',
      };
    } catch (error: any) {
      console.error('Erreur startIrisSession:', error);
      return {
        success: false,
        data: null,
        message: error.message || 'Erreur réseau',
      };
    }
  }

  async captureEye(
    sessionId: string,
    eye: 'LEFT' | 'RIGHT',
    timeout: number = 30
  ): Promise<ApiResponse<IrisCaptureData>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/biometrics/iris/sessions/${sessionId}/capture/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eye_position: eye,
          timeout: timeout,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Erreur lors de la capture');
      }

      return {
        success: true,
        data: data,
        message: 'Capture réussie',
      };
    } catch (error: any) {
      console.error('Erreur captureEye:', error);
      return {
        success: false,
        data: null,
        message: error.message || 'Erreur lors de la capture',
      };
    }
  }

  async markEyeHandicap(
    sessionId: string,
    eye: 'LEFT' | 'RIGHT',
    handicapType: 'BLIND' | 'MISSING' | 'DAMAGED' | 'OTHER',
    reason: string
  ): Promise<ApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/biometrics/iris/sessions/${sessionId}/handicap/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eye_position: eye,
          handicap_type: handicapType,
          reason: reason,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Erreur lors du marquage handicap');
      }

      return {
        success: true,
        data: data,
        message: 'Handicap enregistré',
      };
    } catch (error: any) {
      console.error('Erreur markEyeHandicap:', error);
      return {
        success: false,
        data: null,
        message: error.message || 'Erreur réseau',
      };
    }
  }

  async completeSession(sessionId: string): Promise<ApiResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/biometrics/iris/sessions/${sessionId}/complete/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Erreur lors de la finalisation');
      }

      return {
        success: true,
        data: data,
        message: 'Session finalisée',
      };
    } catch (error: any) {
      console.error('Erreur completeSession:', error);
      return {
        success: false,
        data: null,
        message: error.message || 'Erreur réseau',
      };
    }
  }

  async getSessionStatus(sessionId: string): Promise<ApiResponse<IrisCaptureSession>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/biometrics/iris/sessions/${sessionId}/`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de la récupération du statut');
      }

      return {
        success: true,
        data: data,
        message: 'Statut récupéré',
      };
    } catch (error: any) {
      console.error('Erreur getSessionStatus:', error);
      return {
        success: false,
        data: null,
        message: error.message || 'Erreur réseau',
      };
    }
  }
}

export const biometricApi = new BiometricApiService();