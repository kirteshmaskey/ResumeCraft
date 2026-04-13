import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface GenerateResumeRequest {
    master_resume_text: string;
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
    private readonly baseUrl = `${environment.apiUrl}/generation`;

    constructor(private http: HttpClient) { }

    /** Generate a tailored resume from master resume + JD + template */
    generate(payload: GenerateResumeRequest): Observable<GenerateResumeResponse> {
        return this.http.post<GenerateResumeResponse>(`${this.baseUrl}/generate`, payload);
    }

    /** Compile raw LaTeX code into a PDF and download it */
    compileToPdf(latexCode: string, isTemplate: boolean = false): Observable<Blob> {
        return this.http.post(`${this.baseUrl}/compile`, { latex_code: latexCode, is_template: isTemplate }, {
            responseType: 'blob',
        });
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
