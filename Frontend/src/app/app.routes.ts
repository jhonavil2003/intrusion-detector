import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'auth', pathMatch: 'full' },

  // Lazy load del módulo 'auth'
  {
    path: 'auth',
    loadChildren: () =>
      import('./app/auth-module').then(m => m.AuthModule),
  },

  // Wildcard
  { path: '**', redirectTo: 'auth' },
];
