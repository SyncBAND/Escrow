import { Injectable } from '@angular/core';
import { User } from '../../user';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { ToastService } from '../../../shared/service/toast/toast.service';

import { ModalController, NavController } from '@ionic/angular';

import { LoginPage } from '../../../modals/login/login.page';
import { RegisterPage } from '../../../modals/register/register.page';

@Injectable({
  providedIn: 'root'
})

export class AuthService {

  loginDataReturned: any;
  signupDataReturned: any;
  
  // Init with null to filter out the first value in a guard!
  isAuthenticated: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(null);
  token = '';
  
    endpoint: string = 'https://nikanika.metsiapp.co.za/api';
    //endpoint: string = 'http://localhost:8000/api';
    // endpoint: string = 'http://localhost:8080/api';
    headers = new HttpHeaders();
    currentUser = {};

    constructor(
        public http: HttpClient,
        public modalController: ModalController, 
        private nav: NavController,
        public router: Router,
        public toast: ToastService
    ) {
        this.headers['Content-Type'] = "application/json; charset=UTF-8"
        this.headers["Access-Control-Allow-Origin"] = "*"
        this.headers["Access-Control-Allow-Methods"] = "POST, PUT, OPTIONS, DELETE, GET"
        this.headers['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept, x-access-token"
        this.headers['Access-Control-Allow-Credentials'] = "true"
    }

    // Sign-up
    signUp(user: User): Observable<any> {
        let api = `${this.endpoint}/auth/register-user/`;
        return this.http.post(api, user)
          .pipe(
            catchError((err)=>{
                this.handleError(err);
                return throwError(err);
            })
          )
    }

    resetPassword(user: User): Observable<any> {
        let api = `${this.endpoint}/auth/reset-password/`;
        return this.http.post(api, user)
          .pipe(
            catchError((err)=>{
                this.handleError(err);
                return throwError(err);
            })
          )
    }
  
    parseJwt (token: string) {
        let base64Url = token.split('.')[1];
        let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        let jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        return JSON.parse(jsonPayload);
    };

    getValues(object) {
        let values = '';
        
        if (object.constructor !== Object) 
          return JSON.stringify(object)

        let count = Object.keys(object).length;
        for (var key in object) { 
            if (object.hasOwnProperty(key)) {
                if (count > 1)
                    values = values + key + ': ' + object[key] + '\n' ;
                else
                    values = values + key + ': ' + object[key] ;
            } 
            count--;
        } 

        return values
    } 

    // Sign-in
    signIn(user: User) {
        return this.http.post<any>(`${this.endpoint}/auth/login/`, user)
          .subscribe((res: any) => {
              this.setItems(res);
              this.nav.navigateRoot(localStorage.getItem('current_page') != null ? "/"+localStorage.getItem('current_page') : '/tabs');
          },
          (err: any)=>{
              this.handleError(err)
          })
    }

    getToken() {
        return localStorage.getItem('access_token');
    }

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    getUserId() {
        return localStorage.getItem('user_id');
    }

    get isLoggedIn(): boolean {
        let authToken = this.getToken();
        let authRefreshToken = this.getRefreshToken();
        let authUserId = this.getUserId();
        return (authToken !== null && authRefreshToken !== null && authUserId !== null) ? true : false;
    }

    async logout(path: string) {
      
        if (this.isLoggedIn) {
          
          this.refreshToken().subscribe(()=>{

            return this.http.post<any>(`${this.endpoint}/${path}/${this.getUserId()}/`, {'refresh': this.getRefreshToken(), 'access': this.getToken()}, { headers: this.headers })
              .subscribe((res: any) => {
                  this.removeItems()
              },
              (err: any)=>{
                  return this.removeItems()
              })
            },
            (err)=>{
                return this.removeItems()
            }

          )

        }
        else{
            return this.removeItems()
        }
      
    }

    // Error 
    handleError(error: HttpErrorResponse) {
        let msg = '';
        
        if (error.error.messages) {
            // client-side error
            msg = error.error.messages[0]['message'];
        }
        else if(error.error.detail) {
            msg = error.error.detail
        }
        else if(error.error) {
            msg = this.getValues(error.error)
        }
        else {
            // server-side error
            msg = `Error Code: ${error.status}\nMessage: ${error.message}`;
        }

        if(msg == "Token is blacklisted" || msg == "User not found"){
            return this.logout('logout')
        }
        // else if(msg == "Token is invalid or expired" || msg == "Token 'exp' claim has expired"){
          
        //   if(localStorage.getItem('refresh_counter') == "0"){
        //     localStorage.setItem('refresh_counter', "1")
        //     return this.refreshToken(path)
        //   }
        //   else
        //     return this.logout(path)
        // }
        // console.log("10 "+msg)
        this.toast.presentToast(msg)
        //this.toast.presentToast(JSON.stringify(error))
        
    }

    refreshToken(): Observable<any> {
        return this.http.post<any>(`${this.endpoint}/auth/login/refresh/`, {'refresh': this.getRefreshToken()})
          .pipe(
            map((res)=>{
                // console.log(res)
                this.setItems(res);

                this.headers['Content-Type'] = "application/json"
                this.headers['Authorization'] = "Bearer " + this.getToken()
            }),
            catchError((err)=>{
                // console.log("1: "+ JSON.stringify(err))
                this.handleError(err);
                return throwError(err);
            })
          )
    }

    setItems(res: any) {

        let user_id = this.parseJwt(res.access)['user_id']

        if(res.refresh)
            localStorage.setItem('refresh_token', res.refresh)

        localStorage.setItem('access_token', res.access)
        localStorage.setItem('refresh_counter', "0")
        localStorage.setItem('user_id', user_id)

        return user_id

    }

    async request_logged_in(url: string, method: string, profile: any): Promise <any>  {
        
        return await new Promise<any>((resolve, reject) => {
            this.refreshToken().subscribe((res: any) => {
                resolve(this.request(url, method, profile))
            }, (err)=> {
                reject(err);
            })
        });

    }

    async request(url: string, method: string, profile: any): Promise <any>  {
    
        return await new Promise<any>((resolve, reject) => {
              
            let api = `${this.endpoint}/${url}/`;
            
            if(method == 'get')
                this.http[method](api, { headers: this.headers, params: profile }).subscribe(
                    (res: any) => {
                        resolve(res|| {})
                    },(err)=>{
                        reject(err);
                    }
                )
            else
                this.http[method](api, profile, { headers: this.headers }).subscribe(
                    (res: any) => {
                        resolve(res|| {})
                    },(err)=>{
                        reject(err);
                    }
                )
    
        });
    
    }

    removeItems() {

        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('refresh_counter');
        
        localStorage.removeItem('type');
        localStorage.removeItem('current_page')

        localStorage.removeItem('email')
        localStorage.removeItem('email_verified')

        localStorage.removeItem('rating')
        localStorage.removeItem('current_first_level_url')
        localStorage.removeItem('current_second_level_url')

        // cg
        localStorage.removeItem('chat_list_object_id')
        localStorage.removeItem('chat_list_content_type')
        localStorage.removeItem('chat_list_id')
        localStorage.removeItem('respondent')
        localStorage.removeItem('creator')
        
        localStorage.removeItem('camera_permission')

        localStorage.removeItem('profile_info')
        localStorage.removeItem('profile_loaded')
        localStorage.removeItem('transaction')
        localStorage.removeItem('pay_again_share_code')
        localStorage.removeItem('pay_again_amount')
        localStorage.removeItem('pay_again_details')
        
        localStorage.removeItem('transaction_id')
        localStorage.removeItem('withdrawal_reload')
        localStorage.removeItem('withdrawal_reference')
        localStorage.removeItem('withdrawal_amount')

        this.nav.navigateRoot('/login');

    }
        
    async openLoginModal() {
        const modal = await this.modalController.create({
        component: LoginPage,
        componentProps: {
            "paramID": 123,
            "paramTitle": "Test Title"
        }
        });

        modal.onDidDismiss().then((dataReturned) => {
        if (dataReturned !== null) {
            this.loginDataReturned = dataReturned.data;
            //alert('Modal Sent Data :'+ dataReturned);
        }
        });

        await modal.present();
        const { data } = await modal.onWillDismiss();
        return data
    }

    async openSignupModal() {
        const modal = await this.modalController.create({
        component: RegisterPage,
        componentProps: {
            "paramID": 1234,
            "paramTitle": "Testy Title"
        }
        });

        modal.onDidDismiss().then((dataReturned) => {
        if (dataReturned !== null) {
            this.signupDataReturned = dataReturned.data;
            //alert('Modal Sent Data :'+ dataReturned);
        }
        });

        await modal.present();
        const { data } = await modal.onWillDismiss();
        return data
    }
    
}