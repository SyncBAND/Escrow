import { Component, OnInit } from '@angular/core';

import { AuthService } from '../../shared/service/auth/auth.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-chat-list',
  templateUrl: './chat-list.page.html',
  styleUrls: ['./chat-list.page.scss'],
})
export class ChatListPage implements OnInit {

  chat_list_object_id: any;
  chat_list_content_type: any;
  chats = []
  
  page_number = 1
  num_pages = 1

  constructor(public toast: ToastService, private route: ActivatedRoute, public authService: AuthService, public utils: UtilsService, private router: Router
    ) { 
      
    }

  ngOnInit() {
  }

  ionViewWillEnter(){
    this.chat_list_object_id = localStorage.getItem('chat_list_object_id')
    this.chat_list_content_type = localStorage.getItem('chat_list_content_type')

    localStorage.setItem('current_second_level_url', this.router.url)
    
    this.refresh()
  }

  back(){
    this.router.navigateByUrl( '/support-list' );
  }

  delete(id){
    this.utils.openModal(id, "Cancel").then((data) => {
      if (data != undefined) {
        
          if(data.success){
              
              let formData = new FormData();

              formData.append('id', id)
              formData.append('user', '1')
              formData.append('status_details', data.description)
              formData.append('current_status', 'Deleted')
              
              this.authService.request_logged_in(`chat-list/delete`, "put", formData).then(()=>{
                  this.refresh()
              },(err)=>{
                  this.authService.handleError(err);
              });
                  
          }
          else
              this.toast.presentToast('Dismissed')

      }
    });
  }


  notifications(id, creator, respondent){
    localStorage.setItem('chat_list_id', id)
    localStorage.setItem('respondent', respondent)
    localStorage.setItem('creator', creator)
    this.router.navigateByUrl('/chat')
  }

  doInfinite(event) {
    this.getChatList(true, event);
  }

  getChatList(isFirstLoad, event){

    let url = this.chat_list_content_type + "/chatlist"

    if(isFirstLoad)
      url = url + '?page=' + this.page_number + '&_limit=' + this.num_pages;

    
    this.authService.request_logged_in(url, 'get', {'id': this.chat_list_object_id, 'model': 'Support'}).then((results:any)=>{

      this.num_pages = results.paginator.num_pages
      if(isFirstLoad)
        event.target.complete();
        
      this.page_number++;

      results.results.map((res)=>{
        res['created'] = new Date(res['created'])
        res['modified'] = new Date(res['modified'])
        this.chats.push(res)
      })

    },(err)=>{
      this.authService.handleError(err);
    })

  }

  refresh(){
    this.chats = []
    this.num_pages = 1
    this.page_number = 1
    this.getChatList(false, "");
  }

}
