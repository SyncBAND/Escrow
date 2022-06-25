import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from "@angular/forms";
import { Router } from '@angular/router';
import { ModalController, NavParams } from '@ionic/angular';

import { AuthService } from '../../shared/service/auth/auth.service';
 
@Component({
  selector: 'app-delivered',
  templateUrl: './delivered.page.html',
  styleUrls: ['./delivered.page.scss'],
})
export class DeliveredPage implements OnInit {

  modalForm: FormGroup;
  rateForm: FormGroup;

  isSubmitted = false;

  platform = "ios"

  id: number;
  rating: number;

  constructor(
    private modalController: ModalController,
    private navParams: NavParams,
    public formBuilder: FormBuilder,
    public authService: AuthService,
    public route: Router) { }

  ngOnInit() {
    localStorage.removeItem('rating')
    this.id = this.navParams.data.id;
    this.rating = this.navParams.data.rating;

      this.rateForm = this.formBuilder.group({
          details: ['']
      })
  }

  closeModal() {
    this.modalController.dismiss({'success':false});
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
    console.log("changed rating: ",rating);
  }

}
