import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../shared/service/auth/auth.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { ActionSheetController } from '@ionic/angular';

import { Router } from '@angular/router';

@Component({
  selector: 'app-support-list',
  templateUrl: './support-list.page.html',
  styleUrls: ['./support-list.page.scss'],
})
export class SupportListPage implements OnInit {

  page_number = 1
  num_pages = 1
  
  support = []

  mode = (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'agent').toUpperCase()

  constructor(private _ACTION : ActionSheetController, public toast: ToastService, public utils: UtilsService, public authService: AuthService, private router: Router
    ) { 
      
  }

  ngOnInit() {
    
  }

  ionViewWillEnter(){

    if(this.authService.isLoggedIn)
      this.refresh()
  }

  back(){
    this.router.navigateByUrl('tabs/profile' );
  }

  doInfinite(event) {
    this.getSupport(true, event);
  }

  getSupport(isFirstLoad, event){

    let url = 'support'

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    this.authService.request_logged_in(url, 'get', {}).then((results:any)=>{

      this.num_pages = results.paginator.num_pages
      if(isFirstLoad)
        event.target.complete();
        
      this.page_number++;

      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        this.support.push(res)
      })

    },(err)=>{

      this.authService.handleError(err)

    })

  }

  refresh(){
    this.support = []
    this.num_pages = 1
    this.page_number = 1
    this.getSupport(false, "");
  }

  chat(id){
    localStorage.setItem('chat_list_object_id', id)
    localStorage.setItem('chat_list_content_type', 'support')
    this.router.navigateByUrl('/chat-list');
  }

  cancel(id){
    this.utils.openModal(id, 'Cancel').then((data) => {
      if (data != undefined) {
        
          if(data.success){
            
              let formData = new FormData();

              formData.append('support_id', id)
              formData.append('status_details', data.description)
              formData.append('current_status', 'Cancelled')
              formData.append('mode', this.mode)

              this.authService.request_logged_in(`support-activity`, "post", formData).then(()=>{
                  this.refresh()
                  this.toast.presentToast('Cancelled')
              },(err)=>{
                  this.authService.handleError(err);
              });

          }
          else
              this.toast.presentToast('Dismissed')
      }
    });
  }

  async rate(id){

    this.utils.openModal(id, "Rate").then((data) => {
      if (data != undefined) {
        
          if(data.success){
              if(data.rating){
                  let rating = parseInt(localStorage.getItem('rating'))
                  if( rating == 0 )
                      this.toast.presentToast("Rating was not set")
                  else{
                    let formData = new FormData();

                    formData.append('support', id)
                    formData.append('rating', rating.toString())
                    formData.append('review', data.description)
                    formData.append('previous_skill_needed', '1')
                    formData.append('mode', this.mode)
                    
                    this.authService.request_logged_in(`enquiries-activity`, "post", formData).then(()=>{
                        this.refresh()
                        this.toast.presentToast('Rating was successful')
                    },(err)=>{
                        this.authService.handleError(err);
                    });
                  }
              }
              else
                this.toast.presentToast("No rating")
          }
          else
              this.toast.presentToast('Dismissed')

      }
    });
  }

}