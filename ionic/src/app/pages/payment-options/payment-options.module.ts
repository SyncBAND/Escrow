import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { PaymentOptionsPageRoutingModule } from './payment-options-routing.module';

import { NumberFormatterDirective } from '../../shared/number-formatter.directive';

import { PaymentOptionsPage } from './payment-options.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    IonicModule,
    PaymentOptionsPageRoutingModule
  ],
  declarations: [PaymentOptionsPage, NumberFormatterDirective]
})
export class PaymentOptionsPageModule {}
