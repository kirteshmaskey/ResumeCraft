import { Routes } from '@angular/router';

export const RESUME_ROUTES: Routes = [
    {
        path: '',
        loadComponent: () =>
            import('./pages/resumes-list/resumes-list.component').then(
                (m) => m.ResumesListComponent
            ),
    },
];
