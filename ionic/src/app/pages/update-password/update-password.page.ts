import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { Router } from '@angular/router';

import { ToastService } from '../../shared/service/toast/toast.service';
import { AuthService } from '../../shared/service/auth/auth.service';

@Component({
  selector: 'app-update-password',
  templateUrl: './update-password.page.html',
  styleUrls: ['./update-password.page.scss'],
})
export class UpdatePasswordPage implements OnInit {

  updatePasswordForm: FormGroup;
  isSubmitted = false;

  passwordType = 'password';
  passwordIcon = 'eye-off';

  constructor(public authService: AuthService, public formBuilder: FormBuilder, public router: Router, public toast: ToastService) { }

  ngOnInit() {
    this.updatePasswordForm = this.formBuilder.group({
      password: ['', [Validators.required, Validators.minLength(8)]],
      password2: ['', [Validators.required, Validators.minLength(8)]],
    })
  }

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_page') != null ? `/`+localStorage.getItem('current_page') : '/tabs/profile' );
  }

  hideShowPassword() {
      this.passwordType = this.passwordType === 'text' ? 'password' : 'text';
      this.passwordIcon = this.passwordIcon === 'eye-off' ? 'eye' : 'eye-off';
  }
  
  moveFocus(nextElement) {
      nextElement.setFocus();
  }

  update() {

    this.isSubmitted = true;
    if (!this.updatePasswordForm.valid) {
      return false;
    } else {
      this.isSubmitted = false;

      let id = this.authService.getUserId()

      this.authService.request_logged_in(`update-user-password/${id}`, 'patch', this.updatePasswordForm.value).then((res) => {
        this.updatePasswordForm.controls.password.reset()
        this.updatePasswordForm.controls.password2.reset()
        this.toast.presentToast(res.detail)
        this.back()
      }, (err)=>{

        this.authService.handleError(err)

      })

    }
    
  }

  get errorControl() {
      return this.updatePasswordForm.controls;
  }

}
