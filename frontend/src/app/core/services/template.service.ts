import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ResumeTemplate {
    id: string;
    name: string;
    description: string | null;
    latex_code: string;
    category: string;
    preview_image_url: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface TemplateListItem {
    id: string;
    name: string;
    description: string | null;
    category: string;
    preview_image_url: string | null;
    is_active: boolean;
    created_at: string;
}

export interface TemplateCreatePayload {
    name: string;
    description?: string;
    latex_code: string;
    category: string;
}

export interface TemplateUpdatePayload {
    name?: string;
    description?: string;
    latex_code?: string;
    category?: string;
    is_active?: boolean;
}

@Injectable({ providedIn: 'root' })
export class TemplateService {
    private readonly baseUrl = `${environment.apiUrl}/templates`;

    constructor(private http: HttpClient) { }

    /** List all active templates */
    list(category?: string): Observable<TemplateListItem[]> {
        const params: any = {};
        if (category) params.category = category;
        return this.http.get<TemplateListItem[]>(this.baseUrl, { params });
    }

    /** Get a single template by ID (includes full latex_code) */
    get(id: string): Observable<ResumeTemplate> {
        return this.http.get<ResumeTemplate>(`${this.baseUrl}/${id}`);
    }

    /** Create a new template */
    create(payload: TemplateCreatePayload): Observable<ResumeTemplate> {
        return this.http.post<ResumeTemplate>(this.baseUrl, payload);
    }

    /** Update an existing template */
    update(id: string, payload: TemplateUpdatePayload): Observable<ResumeTemplate> {
        return this.http.put<ResumeTemplate>(`${this.baseUrl}/${id}`, payload);
    }

    /** Soft-delete a template */
    delete(id: string): Observable<void> {
        return this.http.delete<void>(`${this.baseUrl}/${id}`);
    }
}
