import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { ConfigService } from '../../../core/services/config.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-container">
      <div class="login-card">
        <div class="logo-section">
          <div class="logo-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="url(#gradient)" />
              <path d="M14 24H34M14 16H34M14 32H24" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#3b82f6"/>
                  <stop offset="1" stop-color="#2563eb"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1>{{ configService.appName }}</h1>
          <p class="tagline">AI-Powered Resume Optimization</p>
        </div>

        <div class="tabs">
          <button [class.active]="isLogin" (click)="toggleMode()">Sign In</button>
          <button [class.active]="!isLogin" (click)="toggleMode()">Sign Up</button>
        </div>

        <div class="form-section">
          <div class="form-group" *ngIf="!isLogin">
            <input type="text" class="form-control" placeholder="Full Name" [(ngModel)]="fullName" />
          </div>
          <div class="form-group">
            <input type="email" class="form-control" placeholder="Email Address" [(ngModel)]="email" />
          </div>
          <div class="form-group">
            <input type="password" class="form-control" placeholder="Password" [(ngModel)]="password" />
          </div>
        </div>

        <div *ngIf="errorMessage" class="error-msg">{{ errorMessage }}</div>

        <button class="login-btn" (click)="submit()" [disabled]="isLoading">
          <span *ngIf="!isLoading" class="btn-content">
            {{ isLogin ? 'Sign In' : 'Sign Up' }}
          </span>
          <span *ngIf="isLoading" class="btn-content">
            <span class="spinner"></span>
            Processing...
          </span>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f8fafc;
      padding: 1rem;
    }

    .login-card {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 24px;
      padding: 3rem;
      width: 100%;
      max-width: 420px;
      text-align: center;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .logo-section { margin-bottom: 2rem; }

    .logo-icon {
      display: inline-block;
      margin-bottom: 1rem;
    }

    h1 {
      font-size: 1.75rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 0.5rem 0;
    }

    .tagline {
      color: #64748b;
      font-size: 0.875rem;
      margin: 0;
    }

    .tabs {
      display: flex;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid #e2e8f0;
    }

    .tabs button {
      flex: 1;
      padding: 0.75rem;
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      transition: all 0.2s;
    }

    .tabs button.active {
      color: #3b82f6;
      border-bottom-color: #3b82f6;
    }

    .form-section {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .form-control {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      font-family: inherit;
      font-size: 0.875rem;
      transition: border-color 0.2s;
      box-sizing: border-box;
    }

    .form-control:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .error-msg {
      color: #ef4444;
      font-size: 0.875rem;
      margin-bottom: 1rem;
      text-align: left;
    }

    .login-btn {
      width: 100%;
      padding: 0.875rem 1.5rem;
      font-size: 1rem;
      font-weight: 600;
      color: white;
      background: #3b82f6;
      border: none;
      border-radius: 14px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .login-btn:hover:not(:disabled) {
      background: #2563eb;
    }

    .login-btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }

    .btn-content {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }

    .spinner {
      width: 18px;
      height: 18px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `],
})
export class LoginComponent {
  isLoading = false;
  isLogin = true;
  email = '';
  password = '';
  fullName = '';
  errorMessage = '';

  configService = inject(ConfigService);
  private router = inject(Router);

  constructor(private authService: AuthService) { }

  toggleMode(): void {
    this.isLogin = !this.isLogin;
    this.errorMessage = '';
  }

  submit(): void {
    this.errorMessage = '';

    if (!this.email || !this.password || (!this.isLogin && !this.fullName)) {
      this.errorMessage = 'Please fill out all fields.';
      return;
    }

    this.isLoading = true;

    if (this.isLogin) {
      this.authService.login({ email: this.email, password: this.password }).subscribe({
        next: () => {
          this.isLoading = false;
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = err?.error?.detail || 'Invalid email or password.';
        }
      });
    } else {
      this.authService.signup({ email: this.email, password: this.password, full_name: this.fullName }).subscribe({
        next: () => {
          // Log user in automatically after sign up
          this.authService.login({ email: this.email, password: this.password }).subscribe({
            next: () => {
              this.isLoading = false;
              this.router.navigate(['/dashboard']);
            },
            error: () => {
              this.isLoading = false;
              this.router.navigate(['/auth/login']); // fallback
            }
          })
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = err?.error?.detail || 'Sign up failed.';
        }
      });
    }
  }
}
