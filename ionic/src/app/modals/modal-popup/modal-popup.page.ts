import { Component, OnInit } from '@angular/core';

import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { AuthService } from '../../shared/service/auth/auth.service';
import { ToastService } from '../../shared/service/toast/toast.service';
import { UtilsService } from '../../shared/service/utils/utils.service';

import { Router } from '@angular/router';
 
import { ModalController, NavParams } from '@ionic/angular';

import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

@Component({
  selector: 'app-modal-popup',
  templateUrl: './modal-popup.page.html',
  styleUrls: ['./modal-popup.page.scss'],
})

export class ModalPopupPage implements OnInit {

  modalForm: FormGroup;
  rateForm: FormGroup;

  isSubmitted = false;

  platform = "ios"

  id: number;
  rating: number;
  title: string;

  constructor(
    private modalController: ModalController,
    private navParams: NavParams,
    public formBuilder: FormBuilder,
    public authService: AuthService,
    public toast: ToastService,
    public router: Router,
    public utils: UtilsService) { }

  ngOnInit() {
    this.id = this.navParams.data.id;
    this.title = this.navParams.data.title;
    this.rating = this.navParams.data.rating;

    this.modalForm = this.formBuilder.group({
        description: ['', [Validators.required, Validators.minLength(6)]],
    })

    this.rateForm = this.formBuilder.group({
        details: ['']
    })
  }

  get errorControl() {
      return this.modalForm.controls;
  }

  ratings(data){
    if( data['total_number'] == 0)
      return 0
    return ( ((data['total_sum'] / 5)/data['total_number']) * 100 ).toFixed(2)
  }

  closeModal() {
    this.modalController.dismiss({'success':false});
  }

  submit() {

      this.isSubmitted = true;

      if (!this.modalForm.valid) {
        return false;
      } else {
        this.isSubmitted = false;

        let data = this.modalForm.value
        data['success'] = true
        data['rating'] = false

        this.modalForm.controls.description.reset()
        this.modalController.dismiss(data);
      }
      
  }

  rate(){
    let data = this.rateForm.value
    data['success'] = true
    data['rating'] = true

    this.rateForm.controls.details.reset()
    this.modalController.dismiss(data);
  }

  moveFocus(nextElement) {
    nextElement.setFocus();
  }
  logRatingChange(rating){
    console.log("changed rating: ", rating);
  }

}
