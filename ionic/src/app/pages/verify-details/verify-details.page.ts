import { Component, ViewChild, OnInit, ElementRef } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { Router } from '@angular/router';

import { NavController } from '@ionic/angular';

import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

import { UtilsService } from '../../shared/service/utils/utils.service';
import { ToastService } from 'src/app/shared/service/toast/toast.service';
import { AuthService } from 'src/app/shared/service/auth/auth.service';
import { CameraService } from 'src/app/shared/service/camera/camera.service';

@Component({
  selector: 'app-verify-details',
  templateUrl: './verify-details.page.html',
  styleUrls: ['./verify-details.page.scss'],
})
export class VerifyDetailsPage implements OnInit {

  @ViewChild('filechooser') fileInput: ElementRef<HTMLInputElement>;

  userForm: FormGroup;

  // DB variables - have a switch with cases of different amount brackets
  error_details:any = "";
  isError = false;
  isSubmitted = false;
  user_verified_profile_case = [];

  documents = {
    barcoded_id: '',
    front_smart_id: '',
    back_smart_id: '',
    passport_id: '',
    picture_with_id: '',
    certified_copy: '',
    proof_of_address: '',
    company_registration: '',
    company_proof_of_residence: '',
  }

  constructor(
    public authService: AuthService,
    public camera: CameraService,
    public formBuilder: FormBuilder,
    private nav: NavController,
    public router: Router,
    public toast: ToastService,
    public utils: UtilsService) {

  }

  //use guards - to check url
  ngOnInit() {
      
    let res = localStorage.getItem('profile_info')
    let identification = 'smart', account_type = 'individual';

    if(res){
      res = JSON.parse(res)
      
      identification = res['identification_choices']
      account_type = res['account_type_choices']

      this.documents = {
        barcoded_id: res['barcoded_id'],
        front_smart_id: res['front_smart_id'],
        back_smart_id: res['back_smart_id'],
        passport_id: res['passport_id'],
        picture_with_id: res['picture_with_id'],
        certified_copy: res['certified_copy'],
        proof_of_address: res['proof_of_address'],
        company_registration: res['company_registration'],
        company_proof_of_residence: res['company_proof_of_residence'],
      }

      this.user_verified_profile_case = res['user_verified_profile_case']
    }

    this.userForm = this.formBuilder.group({
        identification: [identification, [Validators.required, ]],
        account_type: [account_type, [Validators.required, ]]
    }) 

    this.userForm.valueChanges.subscribe( obj => {
      
      // console.log(obj)

    });

  }

  back() {
      this.nav.navigateRoot('/tabs/profile');
  }

  get getControl() {
      return this.userForm.controls;
  }


  /**
    * @public
    * @method selectFile
    * @param event  {any}        The DOM event that we are capturing from the File input field
    * @description               Web only - Returns the image selected by the user and renders 
    *                            this to the component view
    * @return {none}
    */
  selectFile(position: string) : void
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
          const pattern_pdf = 'application/pdf';
          const reader = new FileReader();
          
          if (!file.type.match(pattern) && !file.type.match(pattern_pdf)) {
              this.toast.presentToast('File format not supported');
              return;
          }

          reader.onload = () => {

            if(position == 'barcoded_id'){
              this.documents['barcoded_id'] = file.name
              this.userForm.addControl('barcoded_id', this.formBuilder.control(''))
              this.userForm.controls['barcoded_id'].setValue(file)
            }
            else if(position == 'front_smart_id'){
              this.documents['front_smart_id'] = file.name
              this.userForm.addControl('front_smart_id', this.formBuilder.control(''))
              this.userForm.controls['front_smart_id'].setValue(file)
            }
            else if(position == 'back_smart_id'){
              this.documents['back_smart_id'] = file.name
              this.userForm.addControl('back_smart_id', this.formBuilder.control(''))
              this.userForm.controls['back_smart_id'].setValue(file)
            }
            else if(position == 'passport'){
              this.documents['passport_id'] = file.name
              this.userForm.addControl('passport_id', this.formBuilder.control(''))
              this.userForm.controls['passport_id'].setValue(file)
            }
            else if(position == 'certified_copy'){
              this.documents['certified_copy'] = file.name
              this.userForm.addControl('certified_copy', this.formBuilder.control(''))
              this.userForm.controls['certified_copy'].setValue(file)
            }
            else if(position == 'picture_with_id'){
              this.documents['picture_with_id'] = file.name
              this.userForm.addControl('picture_with_id', this.formBuilder.control(''))
              this.userForm.controls['picture_with_id'].setValue(file)
            }
            else if(position == 'proof_of_address'){
              this.documents['proof_of_address'] = file.name
              this.userForm.addControl('proof_of_address', this.formBuilder.control(''))
              this.userForm.controls['proof_of_address'].setValue(file)
            }
            else if(position == 'company_registration'){
              this.documents['company_registration'] = file.name
              this.userForm.addControl('company_registration', this.formBuilder.control(''))
              this.userForm.controls['company_registration'].setValue(file)
            }
            else if(position == 'company_proof_of_residence'){
              this.documents['company_proof_of_residence'] = file.name
              this.userForm.addControl('company_proof_of_residence', this.formBuilder.control(''))
              this.userForm.controls['company_proof_of_residence'].setValue(file)
            }
          };
          reader.readAsDataURL(file);

      }, false);
      
  }

  async capture(position){
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
      let image_name = this.getRndInteger(10,20)+new Date().getTime()+this.getRndInteger(50,100)+".jpg";
      

      if(position == 'barcoded_id'){
        this.documents['barcoded_id'] = image_name
        this.userForm.addControl('barcoded_id', this.formBuilder.control(''))
        this.userForm.controls['barcoded_id'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'front_smart_id'){
        this.documents['front_smart_id'] = image_name
        this.userForm.addControl('front_smart_id', this.formBuilder.control(''))
        this.userForm.controls['front_smart_id'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'back_smart_id'){
        this.documents['back_smart_id'] = image_name
        this.userForm.addControl('back_smart_id', this.formBuilder.control(''))
        this.userForm.controls['back_smart_id'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'passport'){
        this.documents['passport_id'] = image_name
        this.userForm.addControl('passport_id', this.formBuilder.control(''))
        this.userForm.controls['passport_id'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'certified_copy'){
        this.documents['certified_copy'] = image_name
        this.userForm.addControl('certified_copy', this.formBuilder.control(''))
        this.userForm.controls['certified_copy'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'picture_with_id'){
        this.documents['picture_with_id'] = image_name
        this.userForm.addControl('picture_with_id', this.formBuilder.control(''))
        this.userForm.controls['picture_with_id'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'proof_of_address'){
        this.documents['proof_of_address'] = image_name
        this.userForm.addControl('proof_of_address', this.formBuilder.control(''))
        this.userForm.controls['proof_of_address'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'company_registration'){
        this.documents['company_registration'] = image_name
        this.userForm.addControl('company_registration', this.formBuilder.control(''))
        this.userForm.controls['company_registration'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }
      else if(position == 'company_proof_of_residence'){
        this.documents['company_proof_of_residence'] = image_name
        this.userForm.addControl('company_proof_of_residence', this.formBuilder.control(''))
        this.userForm.controls['company_proof_of_residence'].setValue(this.dataURLtoFile(imageUrl, image_name))
      }

    }
    else{
      this.selectFile(position);
    }
  }

  getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
  }

  help(document) {
    console.log(document)
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


  async save() {

    this.isSubmitted = true;
    if (!this.userForm.valid) 
      return false;
    
    setTimeout(() => {
      let form = new FormData()
      
      form.append('identification', this.userForm.controls.identification.value)
      form.append('account_type', this.userForm.controls.account_type.value)

      if(this.userForm.controls.identification.value == 'barcode'){
        if(!this.documents['barcoded_id']){
          return this.toast.presentToast("Barcode ID image is required")
        }
      }
      else if(this.userForm.controls.identification.value == 'smart'){
        if(!this.documents['front_smart_id']){
          return this.toast.presentToast("Front image of smart ID is required")
        }
        else if(!this.documents['back_smart_id']){
          return this.toast.presentToast("Back image of smart ID is required")
        }
      }
      else if(this.userForm.controls.identification.value == 'passport'){
        if(!this.documents['passport_id']){
          return this.toast.presentToast("Passport image is required")
        }
      }
      
      if(!this.documents['picture_with_id']){
        return this.toast.presentToast("Selfie image holding up ID is required")
      }
      else if(!this.documents['certified_copy']){
        return this.toast.presentToast(`Certified copy of ${this.userForm.controls.identification.value} ID is required`)
      }
      else if(!this.documents['proof_of_address']){
        return this.toast.presentToast(`Copy of proof of address is required`)
      }
      else if(this.userForm.controls.account_type.value == 'company'){
        if(!this.documents['company_registration'])
          return this.toast.presentToast(`Copy of company registration is required`)
        else if(!this.documents['company_proof_of_residence'])
          return this.toast.presentToast(`Copy of company proof of address is required`)
      }
      

      if(this.userForm.controls.barcoded_id)
        form.append('barcoded_id', this.userForm.controls.barcoded_id.value, this.userForm.controls.barcoded_id.value.name)
      if(this.userForm.controls.picture_with_id)
        form.append('picture_with_id', this.userForm.controls.picture_with_id.value, this.userForm.controls.picture_with_id.value.name)
      if(this.userForm.controls.front_smart_id)
        form.append('front_smart_id', this.userForm.controls.front_smart_id.value, this.userForm.controls.front_smart_id.value.name)
      if(this.userForm.controls.back_smart_id)
        form.append('back_smart_id', this.userForm.controls.back_smart_id.value, this.userForm.controls.back_smart_id.value.name)
      if(this.userForm.controls.passport_id)
        form.append('passport_id', this.userForm.controls.passport_id.value, this.userForm.controls.passport_id.value.name)
      if(this.userForm.controls.certified_copy)
        form.append('certified_copy', this.userForm.controls.certified_copy.value, this.userForm.controls.certified_copy.value.name)
      if(this.userForm.controls.proof_of_address)
        form.append('proof_of_address', this.userForm.controls.proof_of_address.value, this.userForm.controls.proof_of_address.value.name)
      if(this.userForm.controls.company_registration)
        form.append('company_registration', this.userForm.controls.company_registration.value, this.userForm.controls.company_registration.value.name)
      if(this.userForm.controls.company_proof_of_residence)
        form.append('company_proof_of_residence', this.userForm.controls.company_proof_of_residence.value, this.userForm.controls.company_proof_of_residence.value.name)
      

      let id = this.authService.getUserId()
      
      this.authService.request_logged_in(`user-profiles/${id}`, 'patch', form).then((res)=>{
        this.toast.presentToast("Your details will be processed")
        this.isSubmitted = false;
        localStorage.removeItem('profile_loaded')
        this.toast.presentToast("Details updated.")
        this.back()
      },
      (err)=>{
        this.isSubmitted = false;
        let  error = JSON.stringify(err)
        if('error' in err)
          error = JSON.stringify(err['error'])
        this.error_details = error;
        this.isError = true;
        this.utils.showAlert('Error', error)
        return this.authService.handleError(err)
      })

    });
    
  }

}

