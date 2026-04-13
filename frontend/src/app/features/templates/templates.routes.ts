import { Routes } from '@angular/router';

export const TEMPLATE_ROUTES: Routes = [
    {
        path: '',
        loadComponent: () =>
            import('./pages/template-gallery/template-gallery.component').then(
                (m) => m.TemplateGalleryComponent
            ),
    },
    {
        path: 'new',
        loadComponent: () =>
            import('./pages/template-editor/template-editor.component').then(
                (m) => m.TemplateEditorComponent
            ),
    },
    {
        path: ':id/edit',
        loadComponent: () =>
            import('./pages/template-editor/template-editor.component').then(
                (m) => m.TemplateEditorComponent
            ),
    },
];
