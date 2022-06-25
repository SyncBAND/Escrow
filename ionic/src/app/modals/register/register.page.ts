import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { AuthService } from '../../shared/service/auth/auth.service';

import { Router } from '@angular/router';

import { NavController } from '@ionic/angular';
import { ToastService } from 'src/app/shared/service/toast/toast.service';

@Component({
    selector: 'app-register',
    templateUrl: './register.page.html',
    styleUrls: ['./register.page.scss'],
})
export class RegisterPage implements OnInit {

    registerForm: FormGroup;
    isSubmitted = false;

    passwordType = 'password';
    passwordIcon = 'eye-off';

    logo = "../../../assets/logo.png";
    platform = "ios"

    constructor(
        public formBuilder: FormBuilder,
        public authService: AuthService,
        private nav: NavController,
        public route: Router,
        public toast: ToastService,
    ) { }

    ngOnInit() {
        this.registerForm = this.formBuilder.group({
            first_name: ['', [Validators.required, Validators.minLength(2)]],
            email: ['', [Validators.required, Validators.pattern('[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$')]],
            cell: ['', [Validators.required, Validators.pattern('^[0-9]+$')]],
            password: ['', [Validators.required, Validators.minLength(8)]],
            password2: ['', [Validators.required, Validators.minLength(8)]],
            group: ['auto'],
            mode: (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'enduser').toUpperCase()
        })
    }

    get errorControl() {
        return this.registerForm.controls;
    }

    register() {
        this.isSubmitted = true;
        if (!this.registerForm.valid) {
            return false;
        } else {
            this.authService.signUp(this.registerForm.value).subscribe((res) => {
              this.isSubmitted = false;
              this.authService.signIn(this.registerForm.value)
              this.registerForm.controls.password.reset()
              this.registerForm.controls.password2.reset()
            }, err=>{
                //this.toast.presentToast(JSON.stringify(err))
            })
        }
    }

    goLogin() {
        this.nav.navigateRoot('/login');
    }

    hideShowPassword() {
        this.passwordType = this.passwordType === 'text' ? 'password' : 'text';
        this.passwordIcon = this.passwordIcon === 'eye-off' ? 'eye' : 'eye-off';
    }
    
    moveFocus(nextElement) {
        nextElement.setFocus();
    }

}

