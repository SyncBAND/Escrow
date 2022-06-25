import { Component, ViewChild, OnInit } from '@angular/core';
import { IonContent, NavController } from '@ionic/angular';
import { ActivatedRoute, NavigationExtras, Router } from '@angular/router';

import { AuthService } from 'src/app/shared/service/auth/auth.service';

@Component({
  selector: 'app-withdrawal-details',
  templateUrl: './withdrawal-details.page.html',
  styleUrls: ['./withdrawal-details.page.scss'],
})
export class WithdrawalDetailsPage implements OnInit {

  @ViewChild(IonContent) ionContent: IonContent;
  @ViewChild('search') search : any;

  showSearchbar: boolean;

  page_number = 1
  num_pages = 1
  transactions = []
  backupTransactions = []

  constructor(
    public authService: AuthService,
    public activatedRoute : ActivatedRoute, public router: Router, private nav: NavController) {

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
  }

  back() {
    let navigationExtras: NavigationExtras = { state: { data: 'reload_hack' } };
    this.nav.navigateRoot('/wallet-transactions', navigationExtras);
  }

  ionViewWillEnter() {
    if(this.authService.isLoggedIn)
        this.refresh()
  }

  scrollToBottom = () => {
    this.ionContent.scrollToBottom(300);
  }

  scrollToTop = () => {
    this.ionContent.scrollToTop(300);
  }

  doInfinite(event) {
    this.getWithdrawalDetails(true, event);
  }

  getWithdrawalDetails(isFirstLoad, event){

    let url = `withdrawal-transactions/details`

    let get_data: any = {'transaction_id': localStorage.getItem('transaction_id')}
    if(isFirstLoad)
      get_data = {'transaction_id': localStorage.getItem('transaction_id'), 'page': this.page_number, '_limit':this.num_pages}

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
    this.num_pages = 1
    this.page_number = 1
    this.getWithdrawalDetails(false, "");
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
        return item.wallet_reference.toLowerCase().indexOf(searchTerm.toLowerCase()) > -1;
    });
  }

}
