import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Login } from './login/login';
import { Otp } from './otp/otp';
import { authGuard } from './auth-guard';

const routes: Routes = [
  { path: 'login', component: Login, title: 'Iniciar sesión' },
  { path: 'otp', component: Otp, title: 'Registro' },
  { path: 'private', loadComponent: () => import('./private/private').then(m => m.Private) },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AuthRoutingModule { }
