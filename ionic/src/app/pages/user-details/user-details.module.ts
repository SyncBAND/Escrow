import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { UserDetailsPageRoutingModule } from './user-details-routing.module';

import { NumberFormatterDirective } from '../../shared/number-formatter.directive';

import { UserDetailsPage } from './user-details.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    IonicModule,
    UserDetailsPageRoutingModule
  ],
  declarations: [UserDetailsPage, NumberFormatterDirective]
})
export class UserDetailsPageModule {}
