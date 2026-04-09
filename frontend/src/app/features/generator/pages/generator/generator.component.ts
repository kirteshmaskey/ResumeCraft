import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-generator',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="page-container">
      <div class="header">
        <h1>AI Resume Generator</h1>
      </div>
      <div class="generator-form">
        <div class="step">
          <h3>1. Select Master Resume</h3>
          <select class="form-control">
            <option>Select a resume...</option>
          </select>
        </div>
        <div class="step">
          <h3>2. Paste Job Description</h3>
          <textarea class="form-control" rows="10" placeholder="Paste the JD here..."></textarea>
        </div>
        <button class="btn-primary mt-4">Generate Personalized Resume</button>
      </div>
    </div>
  `,
    styles: [`
    .page-container { padding: 2rem; max-width: 800px; margin: 0 auto; }
    .header { margin-bottom: 2rem; }
    .generator-form { display: flex; flex-direction: column; gap: 1.5rem; }
    .step { display: flex; flex-direction: column; gap: 0.5rem; }
    .form-control { border: 1px solid #e5e7eb; border-radius: 6px; padding: 0.75rem; font-family: inherit; }
    .btn-primary { background: #3b82f6; color: white; border: none; padding: 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; }
    .mt-4 { margin-top: 1rem; }
  `]
})
export class GeneratorComponent { }
