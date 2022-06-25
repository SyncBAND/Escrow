import { Component, ViewChild } from '@angular/core';
import { NavigationExtras, Router } from '@angular/router';
import { IonSlides, ModalController } from '@ionic/angular';
import { DeliveredPage } from '../modals/delivered/delivered.page';

import { AuthService } from '../shared/service/auth/auth.service';
import { ToastService } from '../shared/service/toast/toast.service';
import { UtilsService } from '../shared/service/utils/utils.service';

@Component({
  selector: 'app-tab3',
  templateUrl: 'tab3.page.html',
  styleUrls: ['tab3.page.scss']
})
export class Tab3Page {

  /*
    1 - Pending
    2 - Cancelled
    3 - Complete
  */
  
  @ViewChild('slideWithNav1', { static: false }) slideWithNav1: IonSlides;
  @ViewChild('slideWithNav2', { static: false }) slideWithNav2: IonSlides;

  sliderOne: any = {'slidesItems': []};
  sliderTwo: any = {'slidesItems': []};

  slideOptsOne = {
    initialSlide: 0,
    slidesPerView: 1,
    loop: false,
    centeredSlides: true,
    spaceBetween: 20
  };

  slideOptsTwo = {
    initialSlide: 0,
    slidesPerView: 1,
    loop: false,
    centeredSlides: true,
    spaceBetween: 20
  };

  page_number = 1
  num_pages = 5
  
  constructor(public authService: AuthService, private modalController: ModalController, public router: Router, public toast: ToastService, public utils: UtilsService) {
    //Item object for Food
    
  }
  ionViewWillEnter(){
    if(this.authService.isLoggedIn){
      localStorage.removeItem('current_page')
      localStorage.removeItem('withdrawal_current_page')
      this.getRecievedTransactions()
      this.getPaidTransactions()
    }
  }

  // slider 
  
  //Move to Next slide
  slideNext(object, slideView) {
    slideView.slideNext(500).then(() => {
      this.checkIfNavDisabled(object, slideView);
    });
  }

  //Move to previous slide
  slidePrev(object, slideView) {
    slideView.slidePrev(500).then(() => {
      this.checkIfNavDisabled(object, slideView);
    });;
  }

  //Method called when slide is changed by drag or navigation
  SlideDidChange(object, slideView) {
    this.checkIfNavDisabled(object, slideView);
  }

  //Call methods to check if slide is first or last to enable disbale navigation  
  checkIfNavDisabled(object, slideView) {
    this.checkisBeginning(object, slideView);
    this.checkisEnd(object, slideView);
  }

  checkisBeginning(object, slideView) {
    slideView.isBeginning().then((istrue) => {
      object.isBeginningSlide = istrue;
    });
  }
  checkisEnd(object, slideView) {
    slideView.isEnd().then((istrue) => {
      object.isEndSlide = istrue;
    });
  }

  openLogin() {
    //this.authService.openLoginModal();
  }

  view_all(type) {
    localStorage.setItem('type', type)
    this.router.navigateByUrl('/view-all-history');
  }

  getRecievedTransactions(){

    let url = `transactions/recieved`

    this.authService.request_logged_in(url, 'get', {'pk': this.authService.getUserId(), 'page': this.page_number, '_limit':this.num_pages}).then((results:any)=>{
      
      let transactions = []
      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        transactions.push(res)
      })

      this.sliderOne =
      {
        isBeginningSlide: true,
        isEndSlide: false,
        slidesItems: transactions
      };

    },(err)=>{
      this.authService.handleError(err)
    })

  }

  getPaidTransactions(){

    let url = `transactions/paid`

    this.authService.request_logged_in(url, 'get', {'pk': this.authService.getUserId(), 'page': this.page_number, '_limit':this.num_pages}).then((results:any)=>{
      
      let transactions = []
      
      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        transactions.push(res)
      })
      
      this.sliderTwo =
      {
        isBeginningSlide: true,
        isEndSlide: false,
        slidesItems: transactions
      };

    },(err)=>{
      this.authService.handleError(err)
    })

  }
  refresh(){
    this.sliderTwo.slidesItems = []
    this.getPaidTransactions();
  }

  view_history(transaction, type) {
    localStorage.setItem('current_page', this.router.url)
    localStorage.setItem('type', type)
    localStorage.setItem('transaction', JSON.stringify(transaction))
    //this.nav.navigateRoot('/payment-options', navigationExtras);
    this.router.navigateByUrl('/view-history');
  }

  wallet() {
    localStorage.removeItem('withdrawal_reload')
    localStorage.setItem('current_page', this.router.url)
    this.router.navigateByUrl('/wallet-transactions');
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
                    
                    this.authService.request_logged_in(`transactions/delivered`, "patch", formData).then(()=>{
                        this.refresh()
                        this.toast.presentToast('Rating was successful')
                    },(err)=>{
                        this.authService.handleError(err);
                    });
                  }
              }
              else{
                this.toast.presentToast("Dismissed")
              }
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
    localStorage.setItem('current_page', this.router.url)
    localStorage.setItem('withdrawal_current_page', this.router.url)
    this.router.navigateByUrl('/withdrawal');
  }

}
