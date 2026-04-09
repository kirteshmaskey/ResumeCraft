import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, throwError, Subject } from 'rxjs';
import { tap, catchError, switchMap, map, take, filter, shareReplay, finalize } from 'rxjs/operators';
import { Router } from '@angular/router';
import { ApiService } from './api.service';

export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();

  private isRefreshing = false;

  constructor(
    private api: ApiService,
    private router: Router
  ) { }

  get isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  demoLogin(): void {
    const dummyUser: User = {
      id: 'demo-user-123',
      email: 'demo@resumecraft.ai',
      name: 'Demo User',
      is_active: true,
      created_at: new Date().toISOString()
    };

    this.storeTokens('fake-access-token', 'fake-refresh-token');
    this.userSubject.next(dummyUser);
    this.router.navigate(['/dashboard']);
  }

  /** Get the login URL from the backend */
  getLoginUrl(): Observable<{ url: string }> {
    return this.api.get<{ url: string }>('/auth/login-url');
  }

  /** Exchange OAuth code for JWT tokens */
  handleCallback(code: string): Observable<TokenResponse> {
    return this.api.get<TokenResponse>('/auth/callback', { code }).pipe(
      tap((res) => {
        this.storeTokens(res.access_token, res.refresh_token);
        this.userSubject.next(res.user);
      })
    );
  }

  private refreshObservable: Observable<{ access_token: string; expires_in: number }> | null =
    null;

  /** Refresh the access token using the refresh token */
  refreshToken(): Observable<{ access_token: string; expires_in: number }> {
    if (this.refreshObservable) {
      return this.refreshObservable;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token'));
    }

    console.log('[Auth] Starting token refresh...');
    this.isRefreshing = true;

    this.refreshObservable = this.api
      .post<{ access_token: string; expires_in: number }>('/auth/refresh', {
        refresh_token: refreshToken,
      })
      .pipe(
        tap((res) => {
          console.log('[Auth] Refresh successful');
          localStorage.setItem('access_token', res.access_token);
        }),
        shareReplay(1),
        catchError((err) => {
          console.error('[Auth] Refresh failed');
          this.forceLogout();
          return throwError(() => err);
        }),
        finalize(() => {
          this.isRefreshing = false;
          this.refreshObservable = null;
        })
      );

    return this.refreshObservable;
  }

  /** Logout — call backend + clear local state */
  logout(): void {
    this.api.post('/auth/logout').subscribe({
      complete: () => this.forceLogout(),
      error: () => this.forceLogout(),
    });
  }

  /** Force logout without backend call (e.g., on 401) */
  forceLogout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.userSubject.next(null);
    this.router.navigate(['/auth/login']);
  }

  /** Fetch current user profile from backend */
  getCurrentUser(): Observable<User> {
    return this.api.get<User>('/auth/me').pipe(
      tap((user) => this.userSubject.next(user))
    );
  }

  /** Initialize auth state on app startup */
  initAuth(): void {
    if (this.isLoggedIn) {
      this.getCurrentUser().subscribe({
        error: () => this.forceLogout(),
      });
    }
  }

  private storeTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }
}
