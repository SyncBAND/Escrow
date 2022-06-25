import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { WithdrawalPageRoutingModule } from './withdrawal-routing.module';

import { NumberFormatterDirective } from '../../shared/number-formatter.directive';

import { WithdrawalPage } from './withdrawal.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ReactiveFormsModule,
    WithdrawalPageRoutingModule
  ],
  declarations: [WithdrawalPage, NumberFormatterDirective]
})
export class WithdrawalPageModule {}
