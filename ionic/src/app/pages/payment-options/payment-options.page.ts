import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { AuthService } from '../../shared/service/auth/auth.service';
import { Router, ActivatedRoute } from '@angular/router';
import { NavController, AlertController, ModalController } from '@ionic/angular';

import { PaymentPage } from '../../modals/payment/payment.page';
import { UtilsService } from 'src/app/shared/service/utils/utils.service';
import { ToastService } from 'src/app/shared/service/toast/toast.service';

@Component({
  selector: 'app-payment-options',
  templateUrl: './payment-options.page.html',
  styleUrls: ['./payment-options.page.scss'],
})
export class PaymentOptionsPage implements OnInit {

    paymentForm: FormGroup;

    hideElement:boolean;
    isLoading:boolean;
    isFindingRecipient:boolean;

    payment_options: any = [];
    share_code = '';
    amount = '';
    original_amount = 0;
    calculated_charge = 0;
    percentage_charge = 0;
    flat_fee = 0;

    user_data: any = {};
    
    constructor(
        public activatedRoute : ActivatedRoute,
        public alertController: AlertController,
        public authService: AuthService,
        public cdRef:ChangeDetectorRef,
        public formBuilder: FormBuilder,
        public modalController: ModalController,
        private nav: NavController,
        public router: Router,
        public toast: ToastService,
        public utils: UtilsService) {

        this.activatedRoute.queryParams.subscribe((res)=>{
          if (this.router.getCurrentNavigation().extras.state) {
            let data = JSON.parse(this.router.getCurrentNavigation().extras.state.data)

            this.amount = data['calculated_amount']
            this.original_amount = data['amount']
            this.calculated_charge = data['calculated_charge']
            this.percentage_charge = data['percentage'] * 100
            this.flat_fee = data['flat_fee']
          }
          else{
            this.back()
          }
        });

        this.hideElement = true;
        this.isLoading = false;
        this.isFindingRecipient = true;
    }

    ngOnInit() {

        this.paymentForm = this.formBuilder.group({
            recipient_code: ['', [Validators.required]],
            details: ['']
        })

        let details = localStorage.getItem('pay_again_details')
        if(details == undefined || details == null)
            details = ''
            
        let share_code = localStorage.getItem('pay_again_share_code')
        if(share_code == undefined || share_code == null)
            share_code = ''
        
        this.paymentForm.controls.recipient_code.setValue(share_code)
        this.paymentForm.controls.details.setValue(details)

    }
    
    back() {
        localStorage.removeItem('pay_again_amount');
        localStorage.removeItem('pay_again_details');
        localStorage.removeItem('pay_again_share_code');
        this.nav.navigateRoot(['tabs/pay']);
    }

    clear() {
        this.paymentForm.controls.recipient_code.reset();
        this.paymentForm.controls.details.reset();
        
        this.isFindingRecipient = true;
        this.isLoading = false;
        this.hideElement = true;

        this.cdRef.detectChanges();
    }

    find_recipient() {
        this.getUser(this.paymentForm.controls.recipient_code.value)
    }

    async passwordAlertPrompt(id) {

        this.hideElement = true;
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
                this.hideElement = false;
              }
            }, {
              text: 'Ok',
              handler: (res) => {
                this.checkPassword(res['password'], id)
              }
            }
          ]
        });

        await alert.present();
    }

    async make_payment(url, redirect) {
      if(redirect){
        const modal = await this.modalController.create({
          component: PaymentPage,
          componentProps: {
            "url": url,
          }
        });

        modal.onDidDismiss().then((dataReturned) => {
          
          if (dataReturned.data == undefined || dataReturned.data == null || dataReturned.data == 'Done') {
            localStorage.removeItem('profile_loaded')
            this.nav.navigateRoot(['tabs/history']);
            this.isLoading = false;
          }
          else{
            this.presentAlert()
            this.isLoading = false;
            this.isFindingRecipient = false;
            this.hideElement = false;
          }
          
        });

        await modal.present();
        const { data } = await modal.onWillDismiss();
        return data
      }
    }

    moveFocus(nextElement) {
        nextElement.setFocus();
    }

    async presentAlert() {
      
      const alert = await this.alertController.create({
        cssClass: 'my-custom-class',
        header: 'Error',
        subHeader: '',
        message: 'Something went wrong',
        buttons: ['OK']
      });

      await alert.present();

      const { role } = await alert.onDidDismiss();
        
    }

    checkPassword(password, id){

      if(password == undefined || password == null || password.length == 0){
        this.isLoading = false;
        this.isFindingRecipient = false;
        this.hideElement = false;
        return this.toast.presentToast('Password is required')
      }

      // this.isLoading = false;
      // this.isFindingRecipient = false;

      let url = `transactions/initiate`

      this.authService.request_logged_in(url, 'post', {'password': password, 'share_code': this.share_code, 'payment_gateway': id, 'amount': this.amount, 'details': this.paymentForm.controls.details.value, 'original_amount': this.original_amount, 'calculated_charge': this.calculated_charge, 'percentage_charge': this.percentage_charge, 'flat_fee': this.flat_fee }).then((results:any)=>{
        // console.log(results)
        // this.isLoading = false;
        // this.isFindingRecipient = false;
        // this.hideElement = false;
        let response = results['response']
        
        if(response['redirect'] == false){
            localStorage.removeItem('profile_loaded')
            this.nav.navigateRoot(['tabs/history']);
            this.isLoading = false;
            return
        }
          
        this.make_payment(response['url'], response['redirect'])

      },(err)=>{
        // console.log(err)
        this.hideElement = false;
        this.isLoading = false;
        this.authService.handleError(err)

      })

    }

    getUser(code){

      if(code == undefined || code == null || code.length == 0)
        return this.toast.presentToast('Code is required')

      this.isLoading = true;
      this.isFindingRecipient = false;

      let url = `user-profiles/find_recipient`

      this.authService.request_logged_in(url, 'get', {'share_code':code}).then((results:any)=>{

        this.share_code = code

        this.hideElement = false;
        this.isLoading = false;
        this.payment_options = results['payment_gateway']
        this.user_data = results

        localStorage.removeItem('pay_again_amount');
        localStorage.removeItem('pay_again_details');
        localStorage.removeItem('pay_again_share_code');

      },(err)=>{
        this.isFindingRecipient = true;
        this.isLoading = false;
        this.authService.handleError(err)
      })

    }

    info() {
        this.utils.showAlert('Recipent code', 'Insert the unique code belonging to the user you are paying below')
    }

}
