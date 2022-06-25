import { Component, ViewChild, OnInit, ElementRef } from '@angular/core';
import { ModalController, NavController } from '@ionic/angular';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";

import { AuthService } from '../../shared/service/auth/auth.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { Observable } from 'rxjs';

import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

import { Router } from '@angular/router';
import { CameraService } from 'src/app/shared/service/camera/camera.service';


@Component({
  selector: 'app-support',
  templateUrl: './support.page.html',
  styleUrls: ['./support.page.scss'],
})
export class SupportPage implements OnInit {

  @ViewChild('filechooser') fileInput: ElementRef<HTMLInputElement>;

  supportForm: FormGroup;
  isSubmitted = false;

  items: any;
  acService: any;
  placesService: any;
  selectedItem: any;
  buttonDisabled = true;
  sessionToken: any;


  data: Observable<string[]>;
  
  constructor(public authService: AuthService,
    public nav: NavController,
    public camera: CameraService,
    public utils: UtilsService,
    public toast: ToastService,
    public formBuilder: FormBuilder,
    private router: Router,
    private modalCtrl:ModalController) {
      
  }

  ionViewWillEnter(){
    
  }

  dismiss() {
    console.log("Clear search")
    this.items = [];
    this.supportForm.controls.location.setValue('')
    this.selectedItem = undefined
  }

  
  
  ngOnInit() {
    
    this.supportForm = this.formBuilder.group({
      title: ['', [Validators.required, Validators.minLength(4)]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      user: [1],
    })
    
  }

  get errorControl() {
    return this.supportForm.controls;
  }

  event = {
    photo_1: '../../../assets/camera.png',
    photo_2: '../../../assets/camera.png',
    photo_3: '../../../assets/camera.png',
    photo_4: '../../../assets/camera.png',
  }

  /**
    * @public
    * @method selectImage
    * @param event  {any}        The DOM event that we are capturing from the File input field
    * @description               Web only - Returns the image selected by the user and renders 
    *                            this to the component view
    * @return {none}
    */
   selectImage(position: string) : void
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
              if(position == '1'){
                this.event['photo_1'] = reader.result.toString()
                this.supportForm.addControl('image_1', this.formBuilder.control(''))
                this.supportForm.controls['image_1'].setValue(file)
              }
              else if(position == '2'){
                this.event['photo_2'] = reader.result.toString()
                this.supportForm.addControl('image_2', this.formBuilder.control(''))
                this.supportForm.controls['image_2'].setValue(file)
              }
              else if(position == '3'){
                this.event['photo_3'] = reader.result.toString()
                this.supportForm.addControl('image_3', this.formBuilder.control(''))
                this.supportForm.controls['image_3'].setValue(file)
              }
              else if(position == '4'){
                this.event['photo_4'] = reader.result.toString()
                this.supportForm.addControl('image_4', this.formBuilder.control(''))
                this.supportForm.controls['image_4'].setValue(file)
              }
            };
            reader.readAsDataURL(file);

        }, false);
      
   }

   async capture(position){

    if(localStorage.getItem('camera_permission') == null)
      this.utils.showAlert('Camera and storage Permission', 'The reason why we need your camera is for you take images for your bookings')
    

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
        
        if(position == '1'){
          this.event['photo_1'] = imageUrl
          this.supportForm.addControl('image_1', this.formBuilder.control(''))
          this.supportForm.controls['image_1'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '2'){
          this.event['photo_2'] = imageUrl

          this.supportForm.addControl('image_2', this.formBuilder.control(''))
          this.supportForm.controls['image_2'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '3'){
          this.event['photo_3'] = imageUrl
          this.supportForm.addControl('image_3', this.formBuilder.control(''))
          this.supportForm.controls['image_3'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
        else if(position == '4'){
          this.event['photo_4'] = imageUrl
          this.supportForm.addControl('image_4', this.formBuilder.control(''))
          this.supportForm.controls['image_4'].setValue(this.dataURLtoFile(imageUrl, this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg"))
        }
      }
      else{
        this.selectImage(position);
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

    moveFocus(nextElement) {
        nextElement.setFocus();
    }

    async sendSupport() {
      this.isSubmitted = true;
      if (!this.supportForm.valid)
        return false;
      
      setTimeout(() => {
        let form = new FormData()
        
        form.append('title', this.supportForm.controls.title.value)
        form.append('problem', 'Support')
        form.append('description', this.supportForm.controls.description.value)
        form.append('user', '1')
        
        if(this.supportForm.controls.image_1)
          form.append('image_1', this.supportForm.controls.image_1.value, this.supportForm.controls.image_1.value.name)
        if(this.supportForm.controls.image_2)
          form.append('image_2', this.supportForm.controls.image_2.value, this.supportForm.controls.image_2.value.name)
        if(this.supportForm.controls.image_3)
          form.append('image_3', this.supportForm.controls.image_3.value, this.supportForm.controls.image_3.value.name)
        if(this.supportForm.controls.image_4)
          form.append('image_4', this.supportForm.controls.image_4.value, this.supportForm.controls.image_4.value.name)
        
        this.authService.request_logged_in('support', 'post', form).then((res)=>{
          this.reset()
          this.toast.presentToast("Support notified")
          this.isSubmitted = false;
          this.back()
        },
        (err)=>{

          this.isSubmitted = false;
          return this.authService.handleError(err)

        })
      });
      
    }

    reset(){
      this.supportForm.controls.title.reset()
      this.supportForm.controls.description.reset()

      if(this.supportForm.controls.image_1)
        this.supportForm.removeControl('image_1')
      if(this.supportForm.controls.image_2)
        this.supportForm.removeControl('image_2')
      if(this.supportForm.controls.image_3)
        this.supportForm.removeControl('image_3')
      if(this.supportForm.controls.image_4)
        this.supportForm.removeControl('image_4')

    }
    
    back(){
      this.router.navigateByUrl('support-list');
    }

}
