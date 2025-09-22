import { Component } from '@angular/core';
import {Router} from '@angular/router';
import {Auth} from '../auth';
import {FormsModule} from '@angular/forms';
import {Store} from '../../auth/store';
import {AuthApi} from '../auth-api';
import {Services} from '../../auth/services';

@Component({
  selector: 'app-otp',
  imports: [
    FormsModule
  ],
  standalone: true,
  templateUrl: './otp.html',
  styleUrl: './otp.scss'
})
export class Otp {
  code = '';
  error = '';
  loading = false;

  constructor(private auth: Auth, private api: AuthApi, private router: Router, private store: Store, private service: Services) {}

  async confirm() {
    const r = await this.api.answer(this.service.username(), this.code, this.service.challengeSession(), { deviceId: this.service.deviceId, country: this.service.country });
    if (r.status === 'OK') {
      this.store.set({
        accessToken: r.tokens.AccessToken,
        idToken: r.tokens.IdToken,
        refreshToken: r.tokens.RefreshToken,
      });
      this.router.navigateByUrl('/auth/private');
    }
    this.loading = true;
    this.error = '';
    try {
      const res = await this.auth.confirmOtp(this.code);
      if ((res as any).done) {
        this.router.navigateByUrl('/auth/private');
      } else {
        this.error = `Paso no soportado: ${(res as any).step}`;
      }
    } catch (e:any) {
      this.error = e?.message ?? 'Código inválido';
    } finally {
      this.loading = false;
    }
  }
}
