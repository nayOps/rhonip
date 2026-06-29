export type UserRole = 'admin' | 'ops';

export interface AuthUser {
  id: string;
  displayName: string;
  role: UserRole;
  /** Ops : poste guichet */
  stationId?: string;
}

export interface AuthSession {
  user: AuthUser;
  loggedInAt: string;
}
