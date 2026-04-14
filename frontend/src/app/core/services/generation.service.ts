import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface GenerateResumeRequest {
    master_resume_id?: string;
    master_resume_text?: string;
    job_description: string;
    template_id: string;
}

export interface GenerateResumeResponse {
    id: string;
    latex_source: string;
    status: string;
    created_at: string;
}

@Injectable({ providedIn: 'root' })
export class GenerationService {
    private readonly endpoint = '/generation';

    constructor(private api: ApiService) { }

    /** Generate a tailored resume from master resume + JD + template */
    generate(payload: GenerateResumeRequest): Observable<GenerateResumeResponse> {
        return this.api.post<GenerateResumeResponse>(`${this.endpoint}/generate`, payload);
    }

    /** Compile raw LaTeX code into a PDF and download it */
    compileToPdf(latexCode: string, isTemplate: boolean = false): Observable<Blob> {
        // ApiService.post normally assumes JSON response, using HttpClient directly for Blob response
        // is actually easier here, or we can use the relative URL logic from ApiService
        return this.api.postBlob(`${this.endpoint}/compile`, { latex_code: latexCode, is_template: isTemplate });
    }

    /** Trigger download of a Blob as a file */
    downloadBlob(blob: Blob, filename: string = 'resume.pdf'): void {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}
