import { ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, NavigationExtras } from '@angular/router';
import { Router } from '@angular/router';

import { AuthService } from '../shared/service/auth/auth.service';
import { CameraService } from '../shared/service/camera/camera.service';
import { ModalService } from '../shared/service/modal/modal.service';
import { ToastService } from '../shared/service/toast/toast.service';
import { UtilsService } from '../shared/service/utils/utils.service';

import { SafeResourceUrl } from '@angular/platform-browser';

import { ActionSheetController, AlertController, NavController } from '@ionic/angular';

import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';


@Component({
  selector: 'app-tab1',
  templateUrl: 'tab1.page.html',
  styleUrls: ['tab1.page.scss']
})
export class Tab1Page {
  
  @ViewChild('filechooser') fileInput: ElementRef<HTMLInputElement>;

  photo: SafeResourceUrl = "../../../assets/user.png";
  currentUser: Object = {};

  activated = false
  verified_details = false

  push_notifications = true

  constructor(
    public authService: AuthService,
    private cdref: ChangeDetectorRef, 
    public router: Router,
    public camera: CameraService,
    public modal: ModalService,
    private route: ActivatedRoute,
    private _ACTION : ActionSheetController,
    private _ALERT 		: AlertController,
    private nav: NavController,
    private toast: ToastService,
    public utils: UtilsService
  ) {
    this.route.queryParams.subscribe(params => {
      
      if(localStorage.getItem('profile_info') == null || localStorage.getItem('profile_info') == undefined)
        localStorage.removeItem('profile_loaded')
        
      if(this.authService.isLoggedIn){
        localStorage.removeItem('current_page')
        localStorage.removeItem('withdrawal_current_page')
        this.load()
      }
    });
  }

  ngOnInit() { 

  }

  ngAfterContentChecked() {
    // https://stackoverflow.com/questions/45467881/expressionchangedafterithasbeencheckederror-expression-has-changed-after-it-was#answer-45467987
    this.cdref.detectChanges();
  }

  // push() { 
  //   if(this.push_notifications == false){

  //     PushNotifications.requestPermission().then((permission) => {
  //       if (permission.granted) {
  //         this.push_notifications = true
  //         localStorage.setItem('push_notification', 'set') 
  //       }
  //       else{
  //         this.utils.showAlert('Note', 'To recieve push notifications please enable them in your device settings manually')
  //         localStorage.setItem('push_notification', 'unset') 
  //       }
  //     })
  //   }
  //   else{
  //     this.push_notifications = false
  //     PushNotifications.removeAllListeners()
  //     localStorage.setItem('push_notification', 'unset') 

  //   }
  // }

  login_message(){
    this.toast.presentToast("Login to add your profile image")
  }

  verify_or_update_email(){
    localStorage.removeItem('profile_loaded')
    this.load('verify-email')
  }

  security(){
    localStorage.setItem('current_page', this.router.url)
    this.router.navigateByUrl(`/update-password`);
  }

  user_details(){
    localStorage.setItem('current_page', this.router.url)
    this.router.navigateByUrl(`/user-details`);
  }

  wallet() {
    localStorage.removeItem('withdrawal_reload')
    localStorage.setItem('current_page', this.router.url)
    this.router.navigateByUrl('/wallet-transactions');
  }

  support(){
    localStorage.setItem('current_page', this.router.url)
    this.router.navigateByUrl(`/support-list`);
  }

  verify_details(){
    localStorage.removeItem('profile_loaded')
    this.load('verify-details')
  }

  reload(){
      localStorage.removeItem('profile_loaded')
      this.load()
  }

  load(page=''){
    
    if(localStorage.getItem('push_notification') == null || localStorage.getItem('push_notification') == 'set'){
      this.push_notifications = true
      localStorage.setItem('push_notification', 'set') 
    }
    else{
      this.push_notifications = false
    }

    let id = this.authService.getUserId()

    if(!localStorage.getItem('profile_loaded')){
      
        this.authService.request_logged_in(`user-profiles/${id}`, 'get', {}).then((res: any) => {
          this.loaded(res)
          if(page != ''){
            localStorage.setItem('current_page', this.router.url)
            this.router.navigateByUrl(`/${page}`);
          }
        },
        (err: any)=>{
          this.authService.handleError(err);
          if(page != ''){
            localStorage.setItem('current_page', this.router.url)
            this.router.navigateByUrl(`/${page}`);
          }
        })
      }
    else{
        let res = JSON.parse(localStorage.getItem('profile_info'))
        this.loaded(res)
        if(page != ''){
          localStorage.setItem('current_page', this.router.url)
          this.router.navigateByUrl(`/${page}`);
        }
    }
  }

  loaded(res){
      this.currentUser = res;
      
      this.currentUser['get_full_name'] = res.user_details.get_full_name
      
      if(res['user_details']['avatar']['full_size'])
        this.photo = res['user_details']['avatar']['full_size']

      localStorage.setItem('profile_loaded', 'loaded')
      localStorage.setItem('profile_info', JSON.stringify(res))

      if(res['verified_email'] === false){
        localStorage.setItem('email', this.currentUser['email'])
        localStorage.setItem('email_verified', 'None')
        this.activated = false
      }
      else{
        localStorage.setItem('email', this.currentUser['email'])
        localStorage.setItem('email_verified', this.currentUser['user_details']['email'])
        this.activated = true;
      }

      if(res['verified_details']){
        this.verified_details = true
      }
  }

  public imageSource 				: string 		=	'';

  /**
    * @public
    * @method selectImage
    * @param event  {any}        The DOM event that we are capturing from the File input field
    * @description               Web only - Returns the image selected by the user and renders 
    *                            this to the component view
    * @return {none}
    */
  selectImage() : void
  {

      const a = document.createElement("input");
      const event = document.createEvent('MouseEvents');
      event.initEvent('click', true, true);
      a['type'] = 'file' ;
      a.dispatchEvent(event);

      localStorage.setItem('camera_permission', 'set')
      
      a.addEventListener('change', (evt: any) => {
          const files = evt.target.files as File[];
          // for (let i = 0; i < files.length; i++) {
          //    this.items.push(files[i]);
          // }
          const file = (evt.target as HTMLInputElement).files[0];
          const pattern = /image-*/;
          const reader = new FileReader();

          if (!file.type.match(pattern)) {
            this.toast.presentToast('File format not supported');
            return;
          }
    
          reader.onload = () => {

            let profile = this.currentUser;
            profile['avatar'] = file

            this.uploadImage(file, file.name, reader.result.toString())

          };
          reader.readAsDataURL(file);

      }, false);
      
  }

  async capture(){

    if(localStorage.getItem('camera_permission') == null)
      this.utils.showAlert('Camera and storage Permission', 'The reason why we need your camera is for you take images of your details')

    if( this.camera.platformIs == 'mobile'){
      localStorage.setItem('camera_permission', 'set')
      
      const image = await Camera.getPhoto({
        quality: 50,
        allowEditing: true,
        resultType: CameraResultType.DataUrl,
        source: CameraSource.Prompt,
      });
      
      // image.webPath will contain a path that can be set as an image src.
      // You can access the original file using image.path, which can be
      // passed to the Filesystem API to read the raw data of the image,
      // if desired (or pass resultType: CameraResultType.Base64 to getPhoto)
      
      // Can be set to the src of an image now
      let imageUrl = image.dataUrl;

      let file = this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg");
      
      this.uploadImage(file, file.name, imageUrl)
    }
    else{
      this.selectImage();
    }
  }
  getRndInteger(min, max) {
      return Math.floor(Math.random() * (max - min) ) + min;
  }
  dataURLtoFile(dataurl, filename) {
      let arr = dataurl.split(','),
          mime = arr[0].match(/:(.*?);/)[1],
          bstr = atob(arr[1]),
          n = bstr.length,
          u8arr = new Uint8Array(n);
      while (n--) {
          u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, {type: mime});
  }

  uploadImage(image: any, image_name: any, photo: any){
      
      const formData = new FormData();

      formData.append("first_name", this.currentUser['user_details']['first_name']);
      formData.append("email", this.currentUser['user_details']['email']);
      formData.append("cell", this.currentUser['user_details']['cell']);
      formData.append("last_name", this.currentUser['user_details']['last_name']);
      formData.append('avatar', image, image_name);

      let id = this.authService.getUserId()
      this.authService.request_logged_in(`update-profile/${id}`, 'put', formData).then((res:any) => {
        this.reload()
      },
      (err: any)=>{
        this.authService.handleError(err);
      })

  }


  /**
    * @public
    * @method captureImage
    * @description               Mobile only - Launches the ActionSheet component to allow the 
    *                            user to select whether they are to capture an image using the
    *                            device camera or photolibrary
    * @return {none}
    */
  captureImage() : void
  {
      //this.launchActionSheet();
      this.parseImage('camera');
  }


  /**
   * @public
   * @method parseImage
   * @param mode  {string}      The device feature that was used (camera or library)
   * @description               Mobile only - Renders the selected image to the component view
   * @return {none}
   */
  parseImage(mode : string) : void
  {
    switch(mode) {

        // Handle image requests via the device camera
        case "camera":
          
          this.camera
          .takePicture()  
          .then((data) => {
              this.photo = data;
              const blob = fetch(data).then(r => {
                r.blob()

                  this.uploadImage(r.blob, 'file_name', data)

              });
          })
          .catch((error) => {
              this.displayErrorWarning(error);
          });
        break;

        // Handle image requests via the device photolibrary
        case "library":
          
          this.camera
          .selectPhoto()
          .then((data) => {
              this.photo = data;
              const blob = fetch(data).then(r => {
                  r.blob()
                  this.uploadImage(r.blob, 'file_name', data)
              });
          })
          .catch((error) => {
              this.displayErrorWarning(error);
          });
        break;

    }
  }


  /**
   * @public
   * @method launchActionSheet
   * @description               Mobile only - Uses the ActionSheet component to present the 
   *                            user with options to select an image using the device camera 
   *                            or photolibrary
   * @return {none}
   */
  async launchActionSheet() : Promise<void>
  {
    let action  	= this._ACTION.create({
        header 		: 'Select your preferred image source',
        buttons 	: [
          {
              text 	: 'Camera',
              handler 	: () =>
              {
                this.parseImage('camera');
              }
          },
          {
              text 	: 'Photolibrary',
              handler 	: () =>
              {
                this.parseImage('library');
              }
          },
          {
              text 	: 'Cancel',
              handler 	: () =>
              {
                
              }
          }
        ]
    });
    (await action).present();
  }

  /**
   * @public
   * @method displayErrorWarning
   * @param message  {string}      A description of the returned error
   * @description      Displays an alert window informing the user of an error
   *                   that has occurred      
   * @return {none}
   */
  displayErrorWarning(message : string) : void
  {
    let alert : any = this._ALERT.create({
        header          : 'Error',
        subHeader       : message,
        buttons      : ['Ok']
          
    });
    alert.present();
  }


  /**
    * @public
    * @method captureImage
    * @description               Mobile only - Launches the ActionSheet component to allow the 
    *                            user to select whether they are to capture an image using the
    *                            device camera or photolibrary
    * @return {none}
    */
  logout() : void
  {
      this.launchLogoutSheet();
  }

  /**
   * @public
   * @method launchLogoutSheet
   * @description               Mobile only - Uses the ActionSheet component to present the 
   *                            user with options to select an image using the device camera 
   *                            or photolibrary
   * @return {none}
   */
  async launchLogoutSheet() : Promise<void>
  {
    let action  	= this._ACTION.create({
        header 		: 'Logging out?',
        buttons 	: [
          {
              text 	: 'Logout on this device',
              handler 	: () =>
              {
                this.authService.logout('logout');
              }
          },
          {
              text 	: 'Logout on all devices',
              handler 	: () =>
              {
                this.authService.logout('logout-all');
              }
          },
          {
              text 	: 'Cancel',
              handler 	: () =>
              {
                
              }
          }
        ]
    });
    (await action).present();
  }

}