import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { TemplateService, TemplateListItem } from '../../../../core/services/template.service';
import { GenerationService, GenerateResumeResponse } from '../../../../core/services/generation.service';
import { ResumeService, MasterResume } from '../../../../core/services/resume.service';

type WizardStep = 'template' | 'input' | 'result';

@Component({
  selector: 'app-generator',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './generator.component.html',
  styleUrls: ['./generator.component.scss'],
})
export class GeneratorComponent implements OnInit {
  // Wizard state
  currentStep = signal<WizardStep>('template');
  templates = signal<TemplateListItem[]>([]);
  masterResumes = signal<MasterResume[]>([]);
  selectedTemplateId = signal<string | null>(null);
  selectedMasterResumeId = signal<string | 'manual'>('manual');
  loading = signal(false);
  generating = signal(false);
  compiling = signal(false);
  error = signal<string | null>(null);

  // Form inputs
  masterResumeText = '';
  jobDescription = '';

  // Result
  generatedResult = signal<GenerateResumeResponse | null>(null);
  editableLatex = '';
  pdfUrl = signal<SafeResourceUrl | null>(null);
  pdfBlob: Blob | null = null;

  constructor(
    private templateService: TemplateService,
    private generationService: GenerationService,
    private resumeService: ResumeService,
    private sanitizer: DomSanitizer
  ) { }

  ngOnInit(): void {
    this.loadTemplates();
    this.loadMasterResumes();
  }

  loadMasterResumes(): void {
    this.resumeService.list().subscribe({
      next: (resumes) => {
        this.masterResumes.set(resumes);
        if (resumes.length > 0) {
          this.selectedMasterResumeId.set(resumes[0].id);
        }
      }
    });
  }

  /** Step 1: Load templates */
  loadTemplates(): void {
    this.loading.set(true);
    this.templateService.list().subscribe({
      next: (templates) => {
        this.templates.set(templates);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  /** Step 1: Select template */
  selectTemplate(id: string): void {
    this.selectedTemplateId.set(id);
  }

  /** Navigate to step 2: Input */
  goToInput(): void {
    if (!this.selectedTemplateId()) {
      this.error.set('Please select a template first.');
      return;
    }
    this.error.set(null);
    this.currentStep.set('input');
  }

  /** Navigate back to step 1 */
  goToTemplateStep(): void {
    this.currentStep.set('template');
    this.error.set(null);
  }

  /** Step 2 → 3: Generate resume */
  generateResume(): void {
    const isManual = this.selectedMasterResumeId() === 'manual';

    if (isManual && !this.masterResumeText.trim()) {
      this.error.set('Please paste your master resume text.');
      return;
    }
    if (!this.jobDescription.trim()) {
      this.error.set('Please paste the job description.');
      return;
    }

    this.error.set(null);
    this.generating.set(true);

    const payload: any = {
      job_description: this.jobDescription,
      template_id: this.selectedTemplateId()!,
    };

    if (isManual) {
      payload.master_resume_text = this.masterResumeText;
    } else {
      payload.master_resume_id = this.selectedMasterResumeId();
    }

    this.generationService.generate(payload).subscribe({
      next: (result) => {
        this.generatedResult.set(result);
        this.editableLatex = result.latex_source;
        this.generating.set(false);
        this.currentStep.set('result');
      },
      error: (err: any) => {
        this.generating.set(false);
        this.error.set(err?.error?.detail || 'Resume generation failed. Please try again.');
      },
    });
  }

  /** Step 3: Compile current LaTeX and show PREVIEW */
  previewPdf(): void {
    if (!this.editableLatex.trim()) return;

    this.compiling.set(true);
    this.error.set(null);

    this.generationService.compileToPdf(this.editableLatex).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        this.pdfUrl.set(this.sanitizer.bypassSecurityTrustResourceUrl(url));
        this.pdfBlob = blob;
        this.compiling.set(false);
      },
      error: (err: any) => {
        this.compiling.set(false);
        this.pdfUrl.set(null);
        this.pdfBlob = null;
        if (err?.error instanceof Blob) {
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const errData = JSON.parse(reader.result as string);
              this.error.set(errData?.detail?.message || 'LaTeX compilation failed');
            } catch {
              this.error.set('LaTeX compilation failed');
            }
          };
          reader.readAsText(err.error);
        } else {
          this.error.set('LaTeX compilation failed. Check your LaTeX syntax.');
        }
      },
    });
  }

  /** Step 3: Download the already compiled PDF */
  downloadPdf(): void {
    if (this.pdfBlob) {
      this.generationService.downloadBlob(this.pdfBlob, 'tailored_resume.pdf');
    }
  }

  /** Start over from step 1 */
  startOver(): void {
    this.currentStep.set('template');
    this.selectedTemplateId.set(null);
    this.masterResumeText = '';
    this.jobDescription = '';
    this.generatedResult.set(null);
    this.editableLatex = '';
    this.pdfUrl.set(null);
    this.pdfBlob = null;
    this.error.set(null);
  }

  /** Go back to input step to regenerate */
  goBackToInput(): void {
    this.currentStep.set('input');
    this.error.set(null);
  }

  getSelectedTemplateName(): string {
    const tpl = this.templates().find(t => t.id === this.selectedTemplateId());
    return tpl?.name || 'Unknown Template';
  }

  getSelectedMasterResume(): MasterResume | undefined {
    return this.masterResumes().find(r => r.id === this.selectedMasterResumeId());
  }
}
