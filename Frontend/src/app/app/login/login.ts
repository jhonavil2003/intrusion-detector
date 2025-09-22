import { Component } from '@angular/core';
import {FormsModule} from '@angular/forms';
import {Router} from '@angular/router';
import {Auth} from '../auth';
import {AuthApi} from '../auth-api';
import {JsonPipe} from '@angular/common';
import {Store}  from '../../auth/store';
import {Services} from '../../auth/services';

@Component({
  selector: 'app-login',
  imports: [
    FormsModule,
    JsonPipe
  ],
  standalone: true,
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class Login {
  email = '';
  //password = '';
  loading = false;
  error = '';

  username = 'jhonavil2003@hotmail.com';
  password = 'EpSFiwMeW4CsxZ2@';
  deviceId = 'web-' + Math.random().toString(36).slice(2,8);
  country = 'CO';
  otp = '';
  lat = 4.710989;
  lon = -74.072090;
  success = false;
  ip = '0.0.0.0';

  challengeSession: string | null = null;

  lastResult: any = null;

  constructor(private auth: Auth, private api: AuthApi, private router: Router, private store: Store, private service: Services) {}

  async onSubmit(ev: Event) {
    ev.preventDefault();
    this.service.setDeviceId(this.deviceId);
    this.service.setCountry(this.country);
    const r = await this.api.login(this.username, this.password, { deviceId: this.deviceId, ip: this.ip, country: this.country, lat: this.lat, lon: this.lon , success: this.success});
    this.lastResult = r;
    if (r.status === 'CHALLENGE') {
      this.service.setUsername(this.username);
      this.service.setChallengeSession(r.session);
      this.challengeSession = r.session;
      this.router.navigateByUrl('/auth/otp');
    } else if (r.status === 'OK') {
      this.store.set({
        accessToken: r.tokens.AccessToken,
        idToken: r.tokens.IdToken,
        refreshToken: r.tokens.RefreshToken,
      });
      this.router.navigateByUrl('/auth/private');
    }
  }

  async answer() {
    if (!this.challengeSession) return;
    const r = await this.api.answer(this.username, this.otp, this.challengeSession, { deviceId: this.deviceId, country: this.country });
    this.lastResult = r;
    if (r.status === 'OK') {
      this.store.set({
        accessToken: r.tokens.AccessToken,
        idToken: r.tokens.IdToken,
        refreshToken: r.tokens.RefreshToken,
      });
      this.router.navigateByUrl('/auth/private');
      this.challengeSession = null;
    }
  }

  async submit() {
    this.loading = true;
    this.error = '';
    try {
      const res = await this.auth.login(this.email, this.password);
      if (res.done) {
        this.router.navigateByUrl('/auth/private');
      } else if ((res as any).challenge === 'CUSTOM_CHALLENGE') {
        this.router.navigateByUrl('/auth/otp');
      } else {
        this.error = `Paso no soportado: ${(res as any).step}`;
      }
    } catch (e:any) {
      this.error = e?.message ?? 'Error de autenticación';
    } finally {
      this.loading = false;
    }
  }
}
