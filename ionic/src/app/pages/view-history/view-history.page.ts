import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

import { FormGroup, FormBuilder } from "@angular/forms";
import { AuthService } from '../../shared/service/auth/auth.service';
import { Router, ActivatedRoute } from '@angular/router';
import { NavController, AlertController, ModalController } from '@ionic/angular';

import { PaymentPage } from '../../modals/payment/payment.page';
import { UtilsService } from 'src/app/shared/service/utils/utils.service';
import { ToastService } from 'src/app/shared/service/toast/toast.service';
import { DeliveredPage } from 'src/app/modals/delivered/delivered.page';

@Component({
  selector: 'app-view-history',
  templateUrl: './view-history.page.html',
  styleUrls: ['./view-history.page.scss'],
})
export class ViewHistoryPage implements OnInit {

  paymentForm: FormGroup;

  hideElement:boolean;
  isLoading:boolean;
  isFindingRecipient:boolean;

  transaction = {}
  title = 'Transaction'
  type = ''
  
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
      
      this.transaction = JSON.parse(localStorage.getItem('transaction'))
      this.type = localStorage.getItem('type')
      if('reference' in this.transaction)
        this.title = this.transaction['reference']
      else{
        this.back()
      }
      
      this.hideElement = true;
      this.isLoading = false;
      this.isFindingRecipient = true;
  }

  ngOnInit() {
    
  }
  
  back() {
      this.nav.navigateRoot(localStorage.getItem('current_page') ? localStorage.getItem('current_page'): '/view-all-history');
  }

  async pay_again(){

    let header = 'Pay this user?';
    if(this.transaction['status'] == 0)
      header = 'Finish off payment?'

    const alert = await this.alertController.create({
      cssClass: 'my-custom-class',
      header: header,
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
            if( this.type == 'paid' )
              localStorage.setItem('pay_again_share_code', this.transaction['recipient']['share_code'])
            else
              localStorage.setItem('pay_again_share_code', this.transaction['payer']['share_code'])
            
            localStorage.setItem('pay_again_amount', this.transaction['original_amount'])
            localStorage.setItem('pay_again_details', this.transaction['details'])
            this.nav.navigateRoot('/tabs/pay');
          }
        }
      ]
    });

    await alert.present();

  }
  
  async rate() {
    const modal = await this.modalController.create({
      component: DeliveredPage,
      componentProps: {
        "rating": 0,
      }
    });

    await modal.present();
    const { data } = await modal.onWillDismiss();
    return data
  }

  delivered(id, reference){

    this.rate().then((data) => {
      if (data != null && data != undefined) {
        
          if(data.success){
              if(data.rating){
                  let rate = localStorage.getItem('rating') 
                  if(rate == null || rate == undefined)
                    return this.toast.presentToast("Rating was not set")
                  
                  let rating = parseInt(rate)
                  
                  if( rating == 0 )
                      this.toast.presentToast("Rating was not set")
                  else{
                    data['rating'] = rating;
                    let formData = new FormData();

                    formData.append('id', id)
                    formData.append('rating', rating.toString())
                    formData.append('details', data.details)
                    formData.append('reference', reference)
                    
                    this.authService.request_logged_in(`transactions/delivered`, "patch", formData).then((res)=>{
                        this.transaction = res
                        this.toast.presentToast('Rating was successful')
                    },(err)=>{
                        this.authService.handleError(err);
                    });
                  }
              }
              else
                this.toast.presentToast("Dismissed")
          }
          else
              this.toast.presentToast('Dismissed')
      }
      else
          this.toast.presentToast('Dismissed')
    });
  }

  withdraw(withdrawal_reference, withdrawal_amount){
    localStorage.setItem('withdrawal_reload', 'set')
    localStorage.setItem('withdrawal_reference', withdrawal_reference)
    localStorage.setItem('withdrawal_amount', withdrawal_amount)
    localStorage.setItem('withdrawal_current_page', this.router.url)
    this.router.navigateByUrl('/withdrawal');
  }

}

