import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ResumeService, MasterResume } from '../../../../core/services/resume.service';
import { AddResumeDialogComponent } from '../../components/add-resume-dialog/add-resume-dialog.component';

@Component({
  selector: 'app-resumes-list',
  standalone: true,
  imports: [CommonModule, AddResumeDialogComponent],
  templateUrl: './resumes-list.component.html',
  styleUrls: ['./resumes-list.component.scss']
})
export class ResumesListComponent implements OnInit {
  resumes = signal<MasterResume[]>([]);
  loading = signal(true);
  showAddDialog = signal(false);

  constructor(private resumeService: ResumeService) { }

  ngOnInit(): void {
    this.loadResumes();
  }

  loadResumes(): void {
    this.loading.set(true);
    this.resumeService.list().subscribe({
      next: (resumes) => {
        this.resumes.set(resumes);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  deleteResume(id: string): void {
    if (confirm('Are you sure you want to delete this resume?')) {
      this.resumeService.delete(id).subscribe({
        next: () => this.loadResumes()
      });
    }
  }
}
