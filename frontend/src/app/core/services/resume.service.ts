import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface MasterResume {
    id: string;
    user_id: string;
    name: string;
    content: any;
    raw_text: string;
    created_at: string;
    updated_at: string;
}

@Injectable({
    providedIn: 'root'
})
export class ResumeService {
    private endpoint = '/resumes';

    constructor(private api: ApiService) { }

    list(): Observable<MasterResume[]> {
        return this.api.get<MasterResume[]>(this.endpoint);
    }

    create(name: string, textContent?: string, file?: File): Observable<MasterResume> {
        const formData = new FormData();
        formData.append('name', name);
        if (textContent) {
            formData.append('text_content', textContent);
        }
        if (file) {
            formData.append('file', file);
        }
        return this.api.post<MasterResume>(this.endpoint, formData);
    }

    delete(id: string): Observable<any> {
        return this.api.delete(`${this.endpoint}/${id}`);
    }
}
