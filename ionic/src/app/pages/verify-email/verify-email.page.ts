import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { Router } from '@angular/router';

import { ToastService } from '../../shared/service/toast/toast.service';
import { AuthService } from '../../shared/service/auth/auth.service';

@Component({
  selector: 'app-verify-email',
  templateUrl: './verify-email.page.html',
  styleUrls: ['./verify-email.page.scss'],
})
export class VerifyEmailPage implements OnInit {

  verifyForm: FormGroup;
  isSubmitted = false;
  email_verified = 'None';

  constructor(public authService: AuthService, public formBuilder: FormBuilder, public router: Router, public toast: ToastService) { }

  ngOnInit() {
    this.verifyForm = this.formBuilder.group({
      email: [(localStorage.getItem('email') != null ? localStorage.getItem('email') : ''), [Validators.required, Validators.pattern('[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$')]],
    })
  }

  back(){
    this.router.navigateByUrl( localStorage.getItem('current_page') != null ? `/`+localStorage.getItem('current_page') : '/tabs/profile' );
  }

  ionViewWillEnter(){
    this.email_verified = (localStorage.getItem('email_verified') != null ? localStorage.getItem('email_verified') : 'None')
  }

  verify() {

    this.isSubmitted = true;

    if (!this.verifyForm.valid) {
      return false;
    } else {
      this.isSubmitted = false;
      let id = this.authService.getUserId()

      this.authService.request_logged_in(`update-profile-email/${id}`, 'patch', this.verifyForm.value).then((res)=>{
        this.toast.presentToast(res.detail)
        this.back()
      }, (err)=>{
        this.authService.handleError(err)
      })
    }
    
  }

  refresh(){
    let id = this.authService.getUserId()

    localStorage.removeItem('profile_loaded')

    this.authService.request_logged_in(`user-profiles/${id}`, 'get', {}).then((res: any) => {
      localStorage.setItem('profile_info', JSON.stringify(res))
      setTimeout(()=>{
        this.toast.presentToast("Details refreshed.")
        this.back()
      }, 500)
    },
    (err: any)=>{
      this.authService.handleError(err)
      localStorage.removeItem('profile_info')
      this.back()
    })
  }

  get errorControl() {
      return this.verifyForm.controls;
  }
  
  moveFocus(nextElement) {
      nextElement.setFocus();
  }

}
