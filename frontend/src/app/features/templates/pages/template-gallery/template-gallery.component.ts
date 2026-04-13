import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { TemplateService, TemplateListItem } from '../../../../core/services/template.service';

@Component({
    selector: 'app-template-gallery',
    standalone: true,
    imports: [CommonModule, RouterModule],
    templateUrl: './template-gallery.component.html',
    styleUrls: ['./template-gallery.component.scss'],
})
export class TemplateGalleryComponent implements OnInit {
    templates = signal<TemplateListItem[]>([]);
    loading = signal(true);
    activeCategory = signal<string | null>(null);

    readonly categories = [
        { value: null, label: 'All Templates', icon: '📋' },
        { value: 'professional', label: 'Professional', icon: '💼' },
        { value: 'tech', label: 'Tech', icon: '💻' },
        { value: 'academic', label: 'Academic', icon: '🎓' },
        { value: 'creative', label: 'Creative', icon: '🎨' },
    ];

    constructor(private templateService: TemplateService) { }

    ngOnInit(): void {
        this.loadTemplates();
    }

    loadTemplates(category?: string | null): void {
        this.loading.set(true);
        this.activeCategory.set(category ?? null);

        this.templateService.list(category || undefined).subscribe({
            next: (templates) => {
                this.templates.set(templates);
                this.loading.set(false);
            },
            error: () => {
                this.loading.set(false);
            },
        });
    }

    getCategoryBadgeClass(category: string): string {
        const map: Record<string, string> = {
            professional: 'badge-primary',
            tech: 'badge-success',
            academic: 'badge-warning',
            creative: 'badge-purple',
        };
        return map[category] || 'badge-primary';
    }

    deleteTemplate(id: string, event: Event): void {
        event.stopPropagation();
        event.preventDefault();
        if (confirm('Are you sure you want to delete this template?')) {
            this.templateService.delete(id).subscribe({
                next: () => this.loadTemplates(this.activeCategory()),
            });
        }
    }
}
