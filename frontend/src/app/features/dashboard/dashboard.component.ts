import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, RouterModule],
    template: `
    <div class="page-container">
      <div class="welcome-section">
        <h1>Welcome to ResumeCraft</h1>
        <p>Your AI-powered assistant for perfect job applications.</p>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">0</span>
          <span class="stat-label">Master Resumes</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">0</span>
          <span class="stat-label">Generated Resumes</span>
        </div>
      </div>

      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="actions-grid">
          <a routerLink="/generator" class="action-card">
            <span class="action-icon">✨</span>
            <div class="action-info">
              <h3>Generate New Resume</h3>
              <p>Optimize your resume for a specific job description</p>
            </div>
          </a>
          <a routerLink="/resumes" class="action-card">
            <span class="action-icon">📄</span>
            <div class="action-info">
              <h3>Manage Master Resumes</h3>
              <p>Update your core experience and skills</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .page-container { padding: 2rem; }
    .welcome-section { margin-bottom: 3rem; }
    .welcome-section h1 { font-size: 2.5rem; margin-bottom: 0.5rem; color: #111827; }
    .welcome-section p { font-size: 1.125rem; color: #4b5563; }
    
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 3rem; }
    .stat-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; }
    .stat-value { font-size: 2rem; font-weight: 700; color: #3b82f6; }
    .stat-label { color: #6b7280; font-weight: 500; }

    .quick-actions h2 { margin-bottom: 1.5rem; font-size: 1.5rem; }
    .actions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
    .action-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-decoration: none; color: inherit; display: flex; align-items: flex-start; gap: 1rem; transition: transform 0.2s, box-shadow 0.2s; }
    .action-card:hover { transform: translateY(-4px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .action-icon { font-size: 2rem; }
    .action-info h3 { margin: 0; font-size: 1.125rem; color: #111827; }
    .action-info p { margin: 0.25rem 0 0; color: #6b7280; font-size: 0.875rem; }
  `]
})
export class DashboardComponent { }
