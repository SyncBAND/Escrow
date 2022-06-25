import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { AuthService } from '../../shared/service/auth/auth.service';
import { Router } from '@angular/router';

import { NavController } from '@ionic/angular';

@Component({
    selector: 'app-login',
    templateUrl: './login.page.html',
    styleUrls: ['./login.page.scss'],
})

export class LoginPage implements OnInit {

    loginForm: FormGroup;
    isSubmitted = false;

    passwordType = 'password';
    passwordIcon = 'eye-off';

    logo = "../../../assets/logo.png";
    platform = "ios"

    constructor(
      public formBuilder: FormBuilder,
      public authService: AuthService,
      private nav: NavController,
      public route: Router) { }

    ngOnInit() {
        this.loginForm = this.formBuilder.group({
            email: ['', [Validators.required, Validators.pattern('[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$')]],
            password: [''],
            mode: (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'enduser').toUpperCase()
        })
    }

    get errorControl() {
        return this.loginForm.controls;
    }

    login() {
        this.isSubmitted = true;
        if (!this.loginForm.valid) {
          return false;
        } else {
          this.authService.signIn(this.loginForm.value)
          this.isSubmitted = false;
          this.loginForm.controls.password.reset()
        }
    }

    goRegister() {
        this.nav.navigateRoot('/register');
    }

    goForgot() {
        this.nav.navigateRoot('/forgot-password');
    }

    hideShowPassword() {
        this.passwordType = this.passwordType === 'text' ? 'password' : 'text';
        this.passwordIcon = this.passwordIcon === 'eye-off' ? 'eye' : 'eye-off';
    }

    moveFocus(nextElement) {
        nextElement.setFocus();
    }

}

