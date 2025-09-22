import {Injectable, signal} from '@angular/core';

export type CognitoTokens = {
  accessToken: string;
  idToken: string;
  refreshToken?: string;
  expiresAt?: number;
};

const KEY = 'cognito_tokens';

@Injectable({
  providedIn: 'root'
})
export class Store {
  tokens = signal<CognitoTokens | null>(null);

  constructor() {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      try { this.tokens.set(JSON.parse(raw)); } catch {}
    }
  }

  set(tokens: CognitoTokens) {
    this.tokens.set(tokens);
    localStorage.setItem(KEY, JSON.stringify(tokens));
  }

  clear() {
    this.tokens.set(null);
    localStorage.removeItem(KEY);
  }

  get idToken(): string | null {
    return this.tokens()?.idToken ?? null;
  }

  get accessToken(): string | null {
    return this.tokens()?.accessToken ?? null;
  }
}
