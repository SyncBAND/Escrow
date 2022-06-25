import { ElementRef, OnInit, ViewChild } from '@angular/core';

import { Platform } from '@ionic/angular';

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CameraService {

  // @ViewChild('filePicker', { static: false }) filePickerRef: ElementRef<HTMLInputElement>;

  // isDesktop: boolean;


  // constructor(private platform: Platform, private sanitizer: DomSanitizer) { }

  // ngOnInit() {
  //   if ((this.platform.is('mobile') && this.platform.is('hybrid')) || this.platform.is('desktop')) {
  //     this.isDesktop = true;
  //   }
  // }

  // async getPicture(type: string) {

  //   const image = await Camera.getPhoto({
  //     quality: 100,
  //     allowEditing: false,
  //     resultType: CameraResultType.Uri,
  //     source: CameraSource.Prompt
  //   }).catch((err)=>{
  //     return err
  //   });

  //   return image.webPath;
  // }

  // onFileChoose(event: Event) {
    
  //   const file = (event.target as HTMLInputElement).files[0];
  //   const pattern = /image-*/;
  //   const reader = new FileReader();

  //   if (!file.type.match(pattern)) {
  //     this.toast.presentToast('File format not supported');
  //     return;
  //   }

  //   reader.onload = () => {
  //     return reader.result.toString();
  //   };
  //   reader.readAsDataURL(file);

  // }



   /**
    * @name _READER
    * @type object
    * @private
    * @description              Creates a FileReader API object
    */
   private _READER 					: any  			=	new FileReader();




   /**
    * @name _IMAGE
    * @type object
    * @private
    * @description              Create an image object using the Angular SafeResourceUrl 
    * 							Interface property to define a URL as safe for loading 
    *							executable code from
    */
   private _IMAGE 					: SafeResourceUrl;



   /**
    * @name platformIs
    * @type String
    * @public
    * @description               Property that stores the environment reference and is 
    *                            used as a flag for determining which features to 
    *                            'switch on' inside the component template
    */
   public platformIs 				: string 		=	'';


   constructor(public http 			: HttpClient,
        private _PLAT 		: Platform, 
   			   private sanitizer 	: DomSanitizer) 
   {  

    // Are we on mobile?
    if(this._PLAT.is('ios') || this._PLAT.is('android'))
    {
       this.platformIs = 'mobile';
    }

    // Or web?
    else
    {
       this.platformIs = 'browser';
    }
   }




   /* ----------------------------------------------------------------

      Mobile environment specific methods - used for iOS/Android only

      ---------------------------------------------------------------- */




   /**
    * @public
    * @method takePicture
    * @description    			Uses the getPhoto method of the Capacitor Camera plugin 
    *							API to return a file Uri which is then made available 
    *							to the parent script as a resolved (or rejected) Promise 
    * 							object courtesy of the async/await functions
    * 							
    * @return {Promise}
    */
   async takePicture() : Promise<any> 
   {

      /* Define the options for the getPhoto method - particularly the source for where 
         the image will be taken from (I.e. the device camera) and how we want the captured 
         image data returned (I.e. base64 string or a file uri) */
      const image  	= await Camera.getPhoto({
         quality 		: 	90,
         allowEditing 	: 	true,
         resultType 	: 	CameraResultType.Uri,
         source 		: 	CameraSource.Camera
      });



      /* We need to run the returned Image URL through Angular's DomSanitizer to 'trust' 
         this for use within the application (I.e. so that Angular knows this isn't an 
         XSS attempt or similarly malicious code) */
         
      return image;
   }




   /**
    * @public
    * @method selectPhoto
    * @description    			Uses the getPhoto method of the Capacitor Camera plugin 
    *							API to return a file Uri from the Photolibrary selected 
    *							image which is then made available to the parent script 
    *							as a resolved (or rejected) Promise object courtesy of the 
    *							async/await functions
    * 							
    * @return {Promise}
    */
   async selectPhoto() : Promise<any> 
   {

      /* Define the options for the getPhoto method - particularly how we want the
         image data returned (I.e. base64 string or a file uri) */
      const image 	= await Camera.getPhoto({
         quality 		:	90,
         allowEditing 	: 	false,
         resultType 	: 	CameraResultType.Uri,
         source 		: 	CameraSource.Photos
      });

      return image;
      
   }

   b64toBlob(b64Data, contentType = '', sliceSize = 512) {
      const byteCharacters = atob(b64Data);
      const byteArrays = [];
   
      for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);
   
        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
          byteNumbers[i] = slice.charCodeAt(i);
        }
   
        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
      }
   
      const blob = new Blob(byteArrays, { type: contentType });
      return blob;
    }


   /* ----------------------------------------------------------------

      Web environment specific methods - used for Progressive Web Apps

      ---------------------------------------------------------------- */



   /**
    * @public
    * @method selectImage
    * @param event  {any}     	The DOM event that we are capturing from the File input field
    * @description    			Uses the FileReader API to capture the input field event, 
    *							retrieve the selected image and return that as a base64 data 
    *							URL courtesy of an Observable
    * @return {Observable}
    */
   selectImage(event) : Observable<any> 
   {
      return Observable.create((observer) =>
      {
         this.handleImageSelection(event)
         .subscribe((res) =>
         {      
            observer.next(res);
            observer.complete();   
         });
      });
   }




   /**
    * @public
    * @method handleImageSelection
    * @param event  {any}     	The DOM event that we are capturing from the File input field
    * @description    			Uses the FileReader API to capture the input field event, 
    *							retrieve the selected image and return that as a base64 data 
    *							URL courtesy of an Observable
    * @return {Observable}
    */
   handleImageSelection(event : any) : Observable<any> 
   {
      let file 		: any 		= event.target.files[0];

      this._READER.readAsDataURL(file);
      return Observable.create((observer) =>
      {
         this._READER.onloadend = () =>
         {
            observer.next(this._READER.result);
            observer.complete();
         }
      });
   }

}
