import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';
import { ConfigService } from '../../../core/services/config.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule],
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

        <div class="features">
          <div class="feature-item">
            <span class="feature-icon">📁</span>
            <span>Manage Master Resumes</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✨</span>
            <span>AI-tailored job applications</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📊</span>
            <span>Track application history</span>
          </div>
        </div>

        <button class="login-btn" (click)="login()" [disabled]="isLoading">
          <span *ngIf="!isLoading" class="btn-content">
            Enter ResumeCraft
          </span>
          <span *ngIf="isLoading" class="btn-content">
            <span class="spinner"></span>
            Starting...
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

    .features {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      margin-bottom: 2rem;
    }

    .feature-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      color: #475569;
      font-size: 0.875rem;
      text-align: left;
      padding: 0.5rem 1rem;
      background: #f1f5f9;
      border-radius: 12px;
    }

    .feature-icon { font-size: 1.25rem; }

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
  configService = inject(ConfigService);

  constructor(private authService: AuthService) { }

  login(): void {
    this.isLoading = true;
    // For now, just demo login
    setTimeout(() => {
      this.authService.demoLogin();
      this.isLoading = false;
    }, 500);
  }
}
