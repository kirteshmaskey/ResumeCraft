import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import {
    TemplateService,
    ResumeTemplate,
    TemplateCreatePayload,
} from '../../../../core/services/template.service';
import { GenerationService } from '../../../../core/services/generation.service';

@Component({
    selector: 'app-template-editor',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './template-editor.component.html',
    styleUrls: ['./template-editor.component.scss'],
})
export class TemplateEditorComponent implements OnInit {
    isEditMode = signal(false);
    templateId = signal<string | null>(null);
    loading = signal(false);
    saving = signal(false);
    compiling = signal(false);
    error = signal<string | null>(null);
    success = signal<string | null>(null);

    // Form fields
    name = '';
    description = '';
    latexCode = '';
    category = 'professional';

    readonly categories = [
        { value: 'professional', label: 'Professional' },
        { value: 'tech', label: 'Tech' },
        { value: 'academic', label: 'Academic' },
        { value: 'creative', label: 'Creative' },
        { value: 'general', label: 'General' },
    ];

    constructor(
        private templateService: TemplateService,
        private generationService: GenerationService,
        private router: Router,
        private route: ActivatedRoute
    ) { }

    ngOnInit(): void {
        const id = this.route.snapshot.paramMap.get('id');
        if (id) {
            this.isEditMode.set(true);
            this.templateId.set(id);
            this.loadTemplate(id);
        }
    }

    /** Load existing template for editing */
    private loadTemplate(id: string): void {
        this.loading.set(true);
        this.templateService.get(id).subscribe({
            next: (template) => {
                this.name = template.name;
                this.description = template.description || '';
                this.latexCode = template.latex_code;
                this.category = template.category;
                this.loading.set(false);
            },
            error: (err) => {
                this.error.set('Failed to load template');
                this.loading.set(false);
            },
        });
    }

    /** Save (create or update) */
    save(): void {
        if (!this.name.trim() || !this.latexCode.trim()) {
            this.error.set('Name and LaTeX code are required.');
            return;
        }

        this.saving.set(true);
        this.error.set(null);
        this.success.set(null);

        const payload: TemplateCreatePayload = {
            name: this.name.trim(),
            description: this.description.trim() || undefined,
            latex_code: this.latexCode,
            category: this.category,
        };

        const request$ = this.isEditMode()
            ? this.templateService.update(this.templateId()!, payload)
            : this.templateService.create(payload);

        request$.subscribe({
            next: (template) => {
                this.saving.set(false);
                this.success.set(this.isEditMode() ? 'Template updated!' : 'Template created!');
                if (!this.isEditMode()) {
                    // Navigate to edit mode after creation
                    this.router.navigate(['/templates', template.id, 'edit']);
                }
                setTimeout(() => this.success.set(null), 3000);
            },
            error: (err) => {
                this.saving.set(false);
                const detail = err?.error?.detail || 'Failed to save template';
                this.error.set(typeof detail === 'string' ? detail : JSON.stringify(detail));
            },
        });
    }

    /** Compile LaTeX to PDF and download */
    compileAndDownload(): void {
        if (!this.latexCode.trim()) {
            this.error.set('Enter LaTeX code before compiling.');
            return;
        }

        this.compiling.set(true);
        this.error.set(null);

        this.generationService.compileToPdf(this.latexCode, true).subscribe({
            next: (blob) => {
                this.generationService.downloadBlob(blob, `${this.name || 'template'}.pdf`);
                this.compiling.set(false);
                this.success.set('PDF compiled successfully!');
                setTimeout(() => this.success.set(null), 3000);
            },
            error: (err) => {
                this.compiling.set(false);
                let errorMsg = 'LaTeX compilation failed';
                if (err?.error instanceof Blob) {
                    // Error response is a blob, need to read it
                    const reader = new FileReader();
                    reader.onload = () => {
                        try {
                            const errData = JSON.parse(reader.result as string);
                            this.error.set(errData?.detail?.message || errorMsg);
                        } catch {
                            this.error.set(errorMsg);
                        }
                    };
                    reader.readAsText(err.error);
                } else {
                    const detail = err?.error?.detail;
                    this.error.set(detail?.message || errorMsg);
                }
            },
        });
    }

    goBack(): void {
        this.router.navigate(['/templates']);
    }
}
