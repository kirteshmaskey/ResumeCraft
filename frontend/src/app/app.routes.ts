import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadChildren: () =>
      import('./features/auth/auth.routes').then((m) => m.AUTH_ROUTES),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () =>
      import(
        './core/components/authenticated-layout/authenticated-layout.component'
      ).then((m) => m.AuthenticatedLayoutComponent),
    children: [
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then(
            (m) => m.DashboardComponent
          ),
      },
      {
        path: 'resumes',
        loadChildren: () =>
          import('./features/resumes/resumes.routes').then(
            (m) => m.RESUME_ROUTES
          ),
      },
      {
        path: 'generator',
        loadChildren: () =>
          import('./features/generator/generator.routes').then(
            (m) => m.GENERATOR_ROUTES
          ),
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];
