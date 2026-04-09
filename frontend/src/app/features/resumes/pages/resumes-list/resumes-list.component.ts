import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-resumes-list',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="page-container">
      <div class="header">
        <h1>Master Resumes</h1>
        <button class="btn-primary">Add New Resume</button>
      </div>
      <div class="empty-state">
        <p>You haven't added any master resumes yet.</p>
      </div>
    </div>
  `,
    styles: [`
    .page-container { padding: 2rem; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
    .empty-state { text-align: center; padding: 4rem; background: #f9fafb; border-radius: 8px; border: 2px dashed #e5e7eb; }
    .btn-primary { background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
  `]
})
export class ResumesListComponent { }
