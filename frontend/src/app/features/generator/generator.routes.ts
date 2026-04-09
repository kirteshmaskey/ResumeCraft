import { Routes } from '@angular/router';

export const GENERATOR_ROUTES: Routes = [
    {
        path: '',
        loadComponent: () =>
            import('./pages/generator/generator.component').then(
                (m) => m.GeneratorComponent
            ),
    },
];
