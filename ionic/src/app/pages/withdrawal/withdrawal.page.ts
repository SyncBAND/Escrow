import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { ActivatedRoute, NavigationExtras, Router } from '@angular/router';

import { AlertController, NavController } from '@ionic/angular';

import { AuthService } from 'src/app/shared/service/auth/auth.service';
import { ToastService } from 'src/app/shared/service/toast/toast.service';

@Component({
  selector: 'app-withdrawal',
  templateUrl: './withdrawal.page.html',
  styleUrls: ['./withdrawal.page.scss'],
})
export class WithdrawalPage implements OnInit {
 
  withdrawalForm: FormGroup;
  isSubmitted = false;

  isLoading:boolean;
  amount = '';
  withdrawal_reference = '';
  withdrawal_payment = '';
  withdrawal_payment_account = '';

  data: any;

  withdrawal_payment_options = []
  withdrawal_payment_account_type_options = []

  constructor(
    public authService: AuthService, public alertController: AlertController, public formBuilder: FormBuilder,
    public activatedRoute : ActivatedRoute, public router: Router, private nav: NavController, public toast: ToastService) {

      this.activatedRoute.queryParams.subscribe((res)=>{
        if (this.router.getCurrentNavigation().extras.state) {

        }
        else{
          localStorage.removeItem('withdrawal_reload')
        }
      });
  }
  //use guards - to check url
  ngOnInit() {
      
    let res = localStorage.getItem('profile_info')
    let withdrawal_cell_number = '', withdrawal_account_number = '';
    
    if(res){
      res = JSON.parse(res)
      // console.log(res)
      this.withdrawal_payment = res['withdrawal_payment']
      withdrawal_cell_number = res['withdrawal_cell_number']
      this.withdrawal_payment_account = res['withdrawal_payment_account']
      withdrawal_account_number = res['withdrawal_account_number']
      this.withdrawal_payment_options = res['withdrawal_payment_options']
      this.withdrawal_payment_account_type_options = res['withdrawal_payment_account_type_options']
      this.withdrawal_reference = localStorage.getItem('withdrawal_reference')
      this.amount = localStorage.getItem('withdrawal_amount')
    }
    else{
      this.back()
    }

    this.withdrawalForm = this.formBuilder.group({
      withdrawal_cell_number: [withdrawal_cell_number],
      withdrawal_payment_account: [this.withdrawal_payment_account],
      withdrawal_account_number: [withdrawal_account_number],
      reference: [this.withdrawal_reference],
      amount: [this.amount],
      withdrawal_payment: [this.withdrawal_payment, [Validators.required]],
      password: ['']
    })
    
    this.isLoading = false;

  }

  compareFn(e1, e2): boolean {
    return e1 && e2 ? e1.id == e2.id : e1 == e2;
  }
  
  back() {
      let navigationExtras: NavigationExtras = { state: { data: 'reload_hack' } };
      this.nav.navigateRoot(localStorage.getItem('withdrawal_current_page') ? localStorage.getItem('withdrawal_current_page'): '/wallet-transactions', navigationExtras);
  }
  onSelectChange(selectedValue: any) {
  }

  get getControl() {
      return this.withdrawalForm.controls;
  }
  
  moveFocus(nextElement) {
      nextElement.setFocus();
  }

  async continue() {
    
    this.isSubmitted = true;

    if (!this.withdrawalForm.valid) {
      return false;
    } else {

      if(this.withdrawalForm.controls.withdrawal_payment.value == 0){
        if(this.withdrawalForm.controls.withdrawal_cell_number.value == undefined)
          return this.withdrawalForm.controls.withdrawal_cell_number.setErrors({minlength: 10})
        else if(this.withdrawalForm.controls.withdrawal_cell_number.value.length < 10)
          return this.withdrawalForm.controls.withdrawal_cell_number.setErrors({minlength: 10})
      }
      else{
        console.log(this.withdrawalForm.controls.withdrawal_payment_account.value)
        console.log(typeof(this.withdrawalForm.controls.withdrawal_payment_account.value))
        if(this.withdrawalForm.controls.withdrawal_payment_account.value == undefined)
          return this.withdrawalForm.controls.withdrawal_payment_account.setErrors({required: true})
        else if(this.withdrawalForm.controls.withdrawal_account_number.value == undefined)
          return this.withdrawalForm.controls.withdrawal_account_number.setErrors({minlength: 5})
        else if(this.withdrawalForm.controls.withdrawal_account_number.value.length < 5)
          return this.withdrawalForm.controls.withdrawal_account_number.setErrors({minlength: 5})
      }

      this.isSubmitted = false;
    
      this.isLoading = true;

      const alert = await this.alertController.create({
        cssClass: 'my-custom-class',
        header: 'Password',
        inputs: [
          {
            name: 'password',
            type: 'password',
            placeholder: 'Your pin code'
          },
        ],
        buttons: [
          {
            text: 'Cancel',
            role: 'cancel',
            cssClass: 'secondary',
            handler: () => {
              this.isLoading = false;
            }
          }, {
            text: 'Ok',
            handler: (res) => {
              this.withdraw(res['password'])
            }
          }
        ]
      });

      await alert.present();

    }
  }

  withdraw(password) {
    
    if(password == undefined || password == null || password.length < 3){
      this.isLoading = false;
      return this.toast.presentToast('Valid password is required')
    }
    
    this.withdrawalForm.controls.password.setValue(password)
    
    this.authService.request_logged_in(`wallet-transactions/withdraw`, 'post', this.withdrawalForm.value).then((res) => {
      localStorage.removeItem('withdrawal_reload')
      this.toast.presentToast("Withdrawal is processing")
      this.isLoading = false;
      localStorage.setItem('profile_info', JSON.stringify(res))
      this.back()
    }, (err)=>{
      this.isLoading = false;
      this.authService.handleError(err)
    })

  }


}
