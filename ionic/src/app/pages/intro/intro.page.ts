import { Component, OnInit, ViewChild } from '@angular/core';
import { IonSlides } from '@ionic/angular';
import { Router } from '@angular/router';

import { intro } from '../../shared/local_storage_variables';

@Component({
  selector: 'app-intro',
  templateUrl: './intro.page.html',
  styleUrls: ['./intro.page.scss'],
})
export class IntroPage implements OnInit {

  @ViewChild(IonSlides)slides: IonSlides;
 
  constructor(private router: Router) { }
 
  ngOnInit() {
    this.start()
  }
 
  next() {
    this.slides.slideNext();
  }
 
  async start() {
    localStorage.setItem(intro, 'true');
    this.router.navigateByUrl('/tabs/pay', { replaceUrl:true });
  }

}
