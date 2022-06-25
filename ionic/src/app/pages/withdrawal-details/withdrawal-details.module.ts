import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { WithdrawalDetailsPageRoutingModule } from './withdrawal-details-routing.module';

import { WithdrawalDetailsPage } from './withdrawal-details.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    WithdrawalDetailsPageRoutingModule
  ],
  declarations: [WithdrawalDetailsPage]
})
export class WithdrawalDetailsPageModule {}
