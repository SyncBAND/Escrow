import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { Router, NavigationExtras } from '@angular/router';
import { NavController } from '@ionic/angular';

import { AuthService } from '../shared/service/auth/auth.service'
import { BadgeService } from '../shared/service/badge/badge.service';
import { UtilsService } from '../shared/service/utils/utils.service';

@Component({
  selector: 'app-tab2',
  templateUrl: 'tab2.page.html',
  styleUrls: ['tab2.page.scss']
})
export class Tab2Page {

  calculateForm: FormGroup;

  hideElement = true;
  isCalculatedError = false;
  isShowingPaymentOptions = false

  // DB variables - have a switch with cases of different amount brackets
  PERCENTAGE:number = 1.15/100;
  FLAT_FEE:number = 49.00;
  AMOUNT_NEEDED:any = 100.00;

  fee_charges: any = [];

  calculated_error:any = "The amount needs to be equal to or over R";

  data: any;
  fee_help = '';

  page_number = 1
  num_pages = 1
  
  constructor(
    private authService: AuthService,
    public formBuilder: FormBuilder,
    public utils: UtilsService,
    private nav: NavController,
    public router: Router, 
    public badgeService: BadgeService) {

  }

  //use guards - to check url
  ngOnInit() {
    this.fee_help = `Percentage fee = ${this.PERCENTAGE}$<br/>Flat fee = R${this.FLAT_FEE}`;
      
    this.calculateForm = this.formBuilder.group({
        amount: ['', [Validators.required, ]]
    }) 

    this.data = {
        amount: 0.00,
        calculated_charge: 0.00,
        calculated_amount: 0.00,
        percentage: 0.00,
        flat_fee: 0.00,
    }

    this.calculated_error = this.calculated_error + this.AMOUNT_NEEDED ;

    this.calculateForm.valueChanges.subscribe( obj => {
      
        // reflects how much user will be paying minus the percentage fee
        if (obj.amount >= this.AMOUNT_NEEDED) {
            this.hideElement = false;
            this.isCalculatedError = false;

            for(let fee in this.fee_charges){
              if('minimum' in this.fee_charges[fee]){
                if(obj.amount >= Number(this.fee_charges[fee]['minimum']) && obj.amount <= Number(this.fee_charges[fee]['maximum'])){
                  if('percentage' in this.fee_charges[fee])
                    this.PERCENTAGE = this.utils.round( Number(this.fee_charges[fee]['percentage'])/100, 4)
                  if('flat_fee' in this.fee_charges[fee])
                    this.FLAT_FEE = Number(this.fee_charges[fee]['flat_fee'])
                  break;
                }
              }
            }

            this.data.amount = (obj.amount * 1);
            this.data.calculated_charge = this.utils.round( (this.data.amount * this.PERCENTAGE) + this.FLAT_FEE, 2 );
            this.data.calculated_amount = this.utils.round( this.data.amount + this.data.calculated_charge, 2 );
            this.data.percentage = this.PERCENTAGE;
            this.data.flat_fee = this.FLAT_FEE;
            

        } else {
            this.clear();
            this.isCalculatedError = true;
        }

    });

  }

  clear() {
      this.hideElement = true;
      this.isCalculatedError = false;
      
      this.PERCENTAGE = 1.15/100;
      this.FLAT_FEE = 49.00;

      this.data.amount = 0.00;
      this.data.calculated_amount = 0.00;
      this.data.calculated_charge = 0.00;
  }

  ionViewWillEnter() {
    localStorage.removeItem('current_page')
    localStorage.removeItem('withdrawal_current_page')
    this.getFeeCharges(true)
  }

  help() {
    this.utils.showAlert('Enter amount to pay', 'Below is the fee break down<br/><br/>'+this.fee_help)
  }

  continue() {
      let navigationExtras: NavigationExtras = { state: { data: JSON.stringify(this.data) } };
      //this.nav.navigateRoot('/payment-options', navigationExtras);
      this.router.navigateByUrl('/payment-options', navigationExtras);
      this.calculateForm.controls.amount.reset();
      this.clear();
  }

  notifications() {
    let res = localStorage.getItem('profile_info'), count = 0;

    if(res != null && res != undefined){
      res = JSON.parse(localStorage.getItem('profile_info'))
      if(!res['verified_email']){
        count++;
        this.badgeService.updateProfileNotifications(count)
      }
      if(res['verified_details_status'] == 0){
        count++;
        this.badgeService.updateProfileNotifications(count)
      }
    }
  }

  getFeeCharges(isFirstLoad){

    let url = 'payment-charge-fee'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    this.authService.request(url, 'get', {}).then((results:any)=>{

      this.fee_help = ''
      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        this.fee_charges.push(res)
        this.fee_help = this.fee_help + `${res['id']}. Between R${res['minimum']} and R${res['maximum']},<br/>Percentage fee = ${res['percentage']}%<br/>Flat fee = R${res['flat_fee']}<br/><br/>`;
      })

      let amount = localStorage.getItem('pay_again_amount')
      if(amount != undefined && amount != null)
        this.calculateForm.controls.amount.setValue(amount)

      this.notifications()

    },(err)=>{

      this.authService.handleError(err)

      let amount = localStorage.getItem('pay_again_amount')
      if(amount != undefined && amount != null)
        this.calculateForm.controls.amount.setValue(amount)

    })

  }

}
