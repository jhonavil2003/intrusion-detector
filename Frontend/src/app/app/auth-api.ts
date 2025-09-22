import { Injectable } from '@angular/core';
import {environment} from '../../environments/environment';

export interface LoginResponseChallenge {
  status: 'CHALLENGE';
  session: string;
  username: string;
}
export interface LoginResponseOK {
  status: 'OK';
  tokens: {
    AccessToken: string;
    IdToken: string;
    RefreshToken?: string;
    ExpiresIn?: number;
    TokenType?: string;
  };
}
export interface LoginResponseError { status: 'ERROR' | 'UNEXPECTED'; message?: string; }

@Injectable({
  providedIn: 'root'
})
export class AuthApi {
  private base = environment.apiBase;

  async login(username: string, password: string, ctx: { ip?:string, deviceId: string; lat?: number; lon?: number; country?: string; success?: boolean }) {
    const r = await fetch(`${this.base}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, ...ctx }),
    });
    return r.json() as Promise<LoginResponseChallenge | LoginResponseOK | LoginResponseError>;
  }

  async answer(username: string, code: string, session: string, ctx: any) {
    const r = await fetch(`${this.base}/auth/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, code, session, ...ctx }),
    });
    return r.json() as Promise<LoginResponseOK | LoginResponseError>;
  }
}
