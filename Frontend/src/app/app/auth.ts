import { Injectable } from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {
  signIn,
  confirmSignIn,
  signOut,
  fetchAuthSession,
  getCurrentUser,
} from 'aws-amplify/auth';

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private _isAuth$ = new BehaviorSubject<boolean>(false);
  isAuth$ = this._isAuth$.asObservable();

  async login(email: string, password: string) {
    const res = await signIn({
      username: email,
      password: password,
    });

    const step = res.nextStep?.signInStep;
    if (step === 'DONE') {
      this._isAuth$.next(true);
      return { done: true };
    }
    if (step === 'CONFIRM_SIGN_IN_WITH_CUSTOM_CHALLENGE') {
      return { challenge: 'CUSTOM_CHALLENGE' };
    }
    return { step };
  }

  async confirmOtp(code: string) {
    const res = await confirmSignIn({ challengeResponse: code });
    const step = res.nextStep?.signInStep;
    if (step === 'DONE') {
      this._isAuth$.next(true);
      return { done: true };
    }
    return { step };
  }

  async token(): Promise<string | null> {
    const s = await fetchAuthSession();
    return s.tokens?.idToken?.toString() ?? null;
  }

  async logout() {
    await signOut();
    this._isAuth$.next(false);
  }

  async check() {
    try {
      await getCurrentUser();
      this._isAuth$.next(true);
      return true;
    } catch {
      this._isAuth$.next(false);
      return false;
    }
  }
}
