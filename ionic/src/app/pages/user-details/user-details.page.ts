import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { Router } from '@angular/router';

import { NavController } from '@ionic/angular';

import { AuthService } from 'src/app/shared/service/auth/auth.service';
import { ToastService } from 'src/app/shared/service/toast/toast.service';

@Component({
  selector: 'app-user-details',
  templateUrl: './user-details.page.html',
  styleUrls: ['./user-details.page.scss'],
})
export class UserDetailsPage implements OnInit {

  userForm: FormGroup;
  isSubmitted = false;

  data: any;

  constructor(
    public authService: AuthService,
    public formBuilder: FormBuilder,
    private nav: NavController,
    public router: Router,
    public toast: ToastService) {

  }

  //use guards - to check url
  ngOnInit() {
      
    let res = localStorage.getItem('profile_info')
    let name = '', last = '', cell = ''

    if(res){
      res = JSON.parse(res)
      name = res['user_details']['first_name']
      last = res['user_details']['last_name']
      cell = res['user_details']['cell']
    }

    this.userForm = this.formBuilder.group({
      first_name: [name, [Validators.required, Validators.minLength(2)]],
      last_name: [last, [Validators.required, Validators.minLength(2)]],
      cell: [cell, [Validators.required, Validators.minLength(10), Validators.pattern('^[0-9]+$')]],
    })

  }

  back() {
      this.nav.navigateRoot('/tabs/profile');
  }

  get errorControl() {
      return this.userForm.controls;
  }
  
  moveFocus(nextElement) {
      nextElement.setFocus();
  }

  edit() {

    this.isSubmitted = true;
    if (!this.userForm.valid) {
      return false;
    } else {
      this.isSubmitted = false;

      let id = this.authService.getUserId()
      
      this.authService.request_logged_in(`update-profile/${id}`, 'patch', this.userForm.value).then((res) => {
        localStorage.removeItem('profile_loaded')
        this.toast.presentToast("Details updated.")
        this.back()
      }, (err)=>{
        
        this.authService.handleError(err)

      })

    }
  }

}
