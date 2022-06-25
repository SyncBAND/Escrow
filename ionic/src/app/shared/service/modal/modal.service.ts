import { Injectable } from '@angular/core';

import { ModalController } from '@ionic/angular';
import { ModalPopupPage } from '../../../modals/modal-popup/modal-popup.page';

@Injectable({
  providedIn: 'root'
})
export class ModalService {

  constructor(public modalController: ModalController) { }

  async showModal(header: string, message: string, button_1_name: string, button_2_name: string) {
    /*
      header: header
      message: message
      button_1_name: 1st button name - returns 1
      button_2_name: 2nd button name - returns 2
      returns selected button value, e.g. 1 or 2
    */
    const modal = await this.modalController.create({
      component: ModalPopupPage,
      componentProps: {
        'header': header,
        'message': message,
        'button_1_name': button_1_name,
        'button_2_name': button_2_name,
      }
    });
    await modal.present();
    const { data } = await modal.onWillDismiss();
    return data
  }

}
