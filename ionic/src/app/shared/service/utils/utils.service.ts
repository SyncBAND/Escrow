import { AlertController, ModalController, Platform } from '@ionic/angular';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { ModalPopupPage } from '../../../modals/modal-popup/modal-popup.page';

import { Dialog } from '@capacitor/dialog';

@Injectable({
  providedIn: 'root'
})
export class UtilsService {

   /**
    * @name platformIs
    * @type String
    * @public
    * @description               Property that stores the environment reference and is 
    *                            used as a flag for determining which features to 
    *                            'switch on' inside the component template
    */
   public platformIs 				: string 		=	'';


   constructor(
      public alertController: AlertController,
      public http : HttpClient,
      public modalController: ModalController, 
      private _PLAT : Platform,
   ) {  

    // Are we on mobile?
    if(this._PLAT.is('ios') || this._PLAT.is('android'))
    {
       this.platformIs = 'mobile';
    }
    // Or web?
    else
    {
       this.platformIs = 'browser';
    }
   }


   format_date = function( value ) {

      if (value){
          var date_time  = new Date(value);
          value = date_time.toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' });
      }
      else
          value = '-';
  
      return `${value}`
  
   };

   async openModal(id, type, info={}) {
     // type can be "Cancel" or "Rate"
     let init = {
         "id": id,
         "rating": 0,
         "title": type
      }
      let componentProps = Object.assign({}, init, info)
      const modal = await this.modalController.create({
            component: ModalPopupPage,
            componentProps: componentProps
      });
 
      await modal.present();
      const { data } = await modal.onWillDismiss();
      return data
   }

   async showAlert(title, message) {
      const alert = await this.alertController.create({
         header: title,
         message: message,
         buttons: ['OK'],
      });

      return await alert.present();
   }

   showConfirm = async (title, message) => {
      const { value } = await Dialog.confirm({
         title: title,
         message: message
      });
      
      console.log('Confirmed:', value);
   };
   
   showPrompt = async (title, message) => {
      const { value, cancelled } = await Dialog.prompt({
         title: title,
         message: message
      });
      
      console.log('Name:', value);
      console.log('Cancelled:', cancelled);
   };

   round = function(num, decimal_places) {
      try{
         return +(Math.round( +(num + ("e+"+decimal_places)) ) + "e-"+decimal_places);
      }
      catch {
         return 0.00
      }
   }

}
