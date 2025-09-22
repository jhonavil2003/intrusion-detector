import {Injectable, signal} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class Services {

  challengeSession   = signal<string>('');
  username           = signal<string>('');
  deviceId           = signal<string>('');
  country            = signal<string>('CO');

  setChallengeSession(session: string) {
    this.challengeSession.set(session);
  }

  setUsername(username: string) {
    this.username.set(username);
  }

  setDeviceId(deviceId: string) {
    this.deviceId.set(deviceId);
  }

  setCountry(country: string) {
    this.country.set(country);
  }

}
