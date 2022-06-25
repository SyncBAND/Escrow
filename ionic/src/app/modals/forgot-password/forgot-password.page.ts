import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { AuthService } from '../../shared/service/auth/auth.service';
import { Router } from '@angular/router';

import { NavController } from '@ionic/angular';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.page.html',
  styleUrls: ['./forgot-password.page.scss'],
})
export class ForgotPasswordPage implements OnInit {

    forgotForm: FormGroup;
    isSubmitted = false;

    logo = "../../../assets/logo.png";
    platform = "ios"

    constructor(
        public formBuilder: FormBuilder,
        public authService: AuthService,
        private nav: NavController,
        public route: Router) { }

    ngOnInit() {
        this.forgotForm = this.formBuilder.group({
            email: ['', [Validators.required, Validators.pattern('[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$')]],
            mode: (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'enduser').toUpperCase()
        })
    }

    get errorControl() {
        return this.forgotForm.controls;
    }

    reset() {
        this.isSubmitted = true;
        if (!this.forgotForm.valid) {
            return false;
        } else {

            this.authService.resetPassword(this.forgotForm.value).subscribe((res) => {
                this.authService.toast.presentToast(res.detail)
                this.isSubmitted = false;
                this.forgotForm.controls.email.reset()
                this.route.navigateByUrl('/login');
            })

        }
    }

    goLogin() {
        this.nav.navigateRoot('/login');
    }

}

