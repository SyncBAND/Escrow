import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../../../shared/service/auth/auth.service';

import { NavController } from '@ionic/angular';

@Injectable({
    providedIn: 'root'
})
export class LoggedinGuard implements CanActivate {
  
    constructor(
        public authService: AuthService,
        public nav: NavController
    ) { }

    canActivate(
        next: ActivatedRouteSnapshot,
        state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
        if (this.authService.isLoggedIn === true) {
            this.nav.navigateRoot('/home');
        }
        return true;
    }
  
}
