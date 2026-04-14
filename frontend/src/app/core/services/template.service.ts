import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

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
    private readonly endpoint = '/templates';

    constructor(private api: ApiService) { }

    /** List all active templates */
    list(category?: string): Observable<TemplateListItem[]> {
        const params: any = {};
        if (category) params.category = category;
        return this.api.get<TemplateListItem[]>(this.endpoint, params);
    }

    /** Get a single template by ID (includes full latex_code) */
    get(id: string): Observable<ResumeTemplate> {
        return this.api.get<ResumeTemplate>(`${this.endpoint}/${id}`);
    }

    /** Create a new template */
    create(payload: TemplateCreatePayload): Observable<ResumeTemplate> {
        return this.api.post<ResumeTemplate>(this.endpoint, payload);
    }

    /** Update an existing template */
    update(id: string, payload: TemplateUpdatePayload): Observable<ResumeTemplate> {
        return this.api.put<ResumeTemplate>(`${this.endpoint}/${id}`, payload);
    }

    /** Soft-delete a template */
    delete(id: string): Observable<void> {
        return this.api.delete<void>(`${this.endpoint}/${id}`);
    }
}
