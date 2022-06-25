import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RatingsComponent } from './ratings/ratings.component';
import { LoginOrRegisterComponent } from './login-or-register/login-or-register.component';


@NgModule({
  declarations: [
    [LoginOrRegisterComponent, RatingsComponent]
  ],
  exports: [
    LoginOrRegisterComponent,
    RatingsComponent
  ],
  imports: [
    CommonModule,
  ]
})
export class ComponentsModule { }
