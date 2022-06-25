import { Component, ViewChild, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationExtras, Router } from '@angular/router';
import { IonContent } from '@ionic/angular';

import { AuthService } from 'src/app/shared/service/auth/auth.service';
import { UtilsService } from 'src/app/shared/service/utils/utils.service';

@Component({
  selector: 'app-wallet-transactions',
  templateUrl: './wallet-transactions.page.html',
  styleUrls: ['./wallet-transactions.page.scss'],
})
export class WalletTransactionsPage implements OnInit {

  @ViewChild(IonContent) ionContent: IonContent;
  @ViewChild('search') search : any;

  showSearchbar: boolean;

  page_number = 1
  num_pages = 1
  transactions = []
  backupTransactions = []

  constructor(public authService: AuthService, private route: ActivatedRoute, public router: Router, public utils: UtilsService) { 
    
    this.route.queryParams.subscribe(params => {
      let res = localStorage.getItem('withdrawal_reload')
      
      if(this.authService.isLoggedIn){
        if(res == null || res == undefined)
          this.refresh()
        else if(this.router.getCurrentNavigation().extras.state == undefined || this.router.getCurrentNavigation().extras.state == null)
          this.refresh()
      }
    });
  }

  ngOnInit() {
    
  }

  details(transaction_id) {
    let navigationExtras: NavigationExtras = { state: { data: 'reload_hack' } };
    localStorage.setItem('withdrawal_reload', 'set')
    localStorage.setItem('transaction_id', transaction_id)
    this.router.navigateByUrl('/withdrawal-details', navigationExtras);
  }

  withdraw(withdrawal_reference, withdrawal_amount) {
    let navigationExtras: NavigationExtras = { state: { data: 'reload_hack' } };
    localStorage.setItem('withdrawal_reload', 'set')
    localStorage.setItem('withdrawal_reference', withdrawal_reference)
    localStorage.setItem('withdrawal_amount', withdrawal_amount)
    localStorage.setItem('withdrawal_current_page', this.router.url)
    this.router.navigateByUrl('/withdrawal', navigationExtras);
  }

  scrollToBottom = () => {
    this.ionContent.scrollToBottom(300);
  }

  scrollToTop = () => {
    this.ionContent.scrollToTop(300);
  }

  doInfinite(event) {
    this.getWalletTransactions(true, event);
  }

  getWalletTransactions(isFirstLoad, event){

    let url = `wallet-transactions/received`

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

  refresh(){
    this.transactions = []
    this.backupTransactions = [];
    this.num_pages = 1
    this.page_number = 1
    
    this.getWalletTransactions(false, "");
  }
  
  back() {
      this.router.navigateByUrl(localStorage.getItem('current_page') ? localStorage.getItem('current_page'): '/tabs/profile');
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
        return item.wallet_reference.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1 || item.transaction.reference.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1 || item.transaction.amount.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1;
    });
  }

}
