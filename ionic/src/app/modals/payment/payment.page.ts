import { Component, OnInit } from '@angular/core';
import { ModalController, NavParams} from '@ionic/angular';

import { Browser } from '@capacitor/browser';

@Component({
  selector: 'app-payment',
  templateUrl: './payment.page.html',
  styleUrls: ['./payment.page.scss'],
})
export class PaymentPage implements OnInit {

  constructor(private modalController: ModalController, private navParams: NavParams) { 

  }

  ngOnInit() {
    Browser.addListener('browserFinished', () => {
      
    })
    let url = ''
    if('url' in this.navParams.data)
      url = this.navParams.get('url')
      
    this.openPaymentOption(url)
  }

  async openPaymentOption(url) {
    if( url != '')
      await Browser.open({ url: url });
    else
      setTimeout(()=>{
        this.closeModal("Invalid", true)
      }, 500)
  };

  async closeModal(msg, invalid=false) {
    if(!invalid)
      msg = 'Done'
    await this.modalController.dismiss(msg);
  }

}
