import { Component, ViewChild, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { IonContent, ModalController } from '@ionic/angular';

import { DeliveredPage } from 'src/app/modals/delivered/delivered.page';

import { AuthService } from '../../shared/service/auth/auth.service';
import { UtilsService } from 'src/app/shared/service/utils/utils.service';
import { ToastService } from 'src/app/shared/service/toast/toast.service';

@Component({
  selector: 'app-view-all-history',
  templateUrl: './view-all-history.page.html',
  styleUrls: ['./view-all-history.page.scss'],
})
export class ViewAllHistoryPage implements OnInit {

  @ViewChild(IonContent) ionContent: IonContent;
  @ViewChild('search') search : any;

  showSearchbar: boolean;

  page_number = 1
  num_pages = 1
  
  transactions = []
  backupTransactions = []

  title = 'Transaction'
  type = ''

  scrollToBottom = () => {
    this.ionContent.scrollToBottom(300);
  }

  scrollToTop = () => {
    this.ionContent.scrollToTop(300);
  }

  doInfinite(event) {
    this.getTransactions(true, event);
  }
  
  constructor(public authService: AuthService, private modalController: ModalController, public router: Router, public toast: ToastService, public utils: UtilsService) { }

  ngOnInit() {
  }

  ionViewWillEnter() {
    if(this.authService.isLoggedIn)
      this.refresh(this.num_pages, this.page_number)
  }

  getTransactions(isFirstLoad, event){

    let url = `transactions/${this.type}`

    let get_data: any = {'pk': this.authService.getUserId()}
    if(isFirstLoad)
      get_data = {'pk': this.authService.getUserId(), 'page': this.page_number, '_limit':this.num_pages}

    this.authService.request_logged_in(url, 'get', get_data).then((results:any)=>{

      this.num_pages = results.paginator.num_pages
      if(isFirstLoad)
        event.target.complete();
        
      this.page_number++;

      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        this.transactions.push(res)
        this.backupTransactions = this.transactions;
      })

    },(err)=>{

      this.authService.handleError(err)

    })

  }

  refresh(num_pages, page_number){
    this.type = localStorage.getItem('type')
    
    if(this.type == null || this.type == undefined)
      this.back()

    this.transactions = []
    this.num_pages = num_pages
    this.page_number = page_number
    this.getTransactions(false, "");
  }

  view_history(transaction) {
    localStorage.setItem('current_page', this.router.url)
    localStorage.setItem('transaction', JSON.stringify(transaction))
    //this.nav.navigateRoot('/payment-options', navigationExtras);
    this.router.navigateByUrl('/view-history');
  }
  
  back() {
      this.router.navigateByUrl('tabs/history');
  }
  
  showSearch() {
    this.showSearchbar = true
    setTimeout(() => this.search.setFocus() , 500);
  }
  
  onChange(event) {
    const filteration = event.target.value;
    this.transactions = this.filterItems(filteration);
    if (filteration.length === 0) {
        this.transactions = this.backupTransactions;
    }
  }

  onCancel(){
    this.showSearchbar = false;
    this.transactions = this.backupTransactions;
  }

  filterItems(searchTerm) {
    return this.backupTransactions.filter(item => {
        return item.payer.get_full_name.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1 || item.recipient.get_full_name.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1 || item.amount.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1 || item.reference.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1;
    });
  }

  ionViewWillLeave(){
    this.onCancel()
    this.transactions = []
    this.backupTransactions = []
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
                        this.refresh(this.num_pages, this.page_number)
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
