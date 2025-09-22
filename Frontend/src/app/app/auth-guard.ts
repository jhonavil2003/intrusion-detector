import {CanActivateFn, Router} from '@angular/router';
import {inject} from '@angular/core';
import {Auth} from './auth';

export const authGuard: CanActivateFn = async () => {
  const auth = inject(Auth);
  const router = inject(Router);
  const ok = await auth.check();
  if (!ok) {
    router.navigateByUrl('/auth/login');
    return false;
  }
  return true;
};
