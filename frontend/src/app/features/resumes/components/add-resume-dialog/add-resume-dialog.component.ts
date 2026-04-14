import { Component, EventEmitter, Output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ResumeService } from '../../../../core/services/resume.service';

@Component({
  selector: 'app-add-resume-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './add-resume-dialog.component.html',
  styleUrls: ['./add-resume-dialog.component.scss']
})
export class AddResumeDialogComponent {
  @Output() close = new EventEmitter<void>();
  @Output() saved = new EventEmitter<void>();

  name = '';
  textContent = '';
  uploadType: 'text' | 'file' = 'text';
  selectedFile: File | null = null;
  loading = false;
  error: string | null = null;

  constructor(private resumeService: ResumeService) { }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        this.error = 'Please select a PDF file.';
        return;
      }
      this.selectedFile = file;
      this.error = null;
    }
  }

  isValid(): boolean {
    if (!this.name.trim()) return false;
    if (this.uploadType === 'text') return !!this.textContent.trim();
    if (this.uploadType === 'file') return !!this.selectedFile;
    return false;
  }

  onSubmit(event: Event): void {
    event.preventDefault();
    if (!this.isValid()) return;

    this.loading = true;
    this.error = null;

    this.resumeService.create(
      this.name,
      this.uploadType === 'text' ? this.textContent : undefined,
      this.uploadType === 'file' ? this.selectedFile! : undefined
    ).subscribe({
      next: () => {
        this.loading = false;
        this.saved.emit();
        this.close.emit();
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || 'Failed to add resume. Please try again.';
      }
    });
  }
}
