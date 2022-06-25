import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ModalPopupPageRoutingModule } from './modal-popup-routing.module';

import { ModalPopupPage } from './modal-popup.page';
import { ComponentsModule } from 'src/app/components/components.module';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ModalPopupPageRoutingModule,
    ReactiveFormsModule,
    ComponentsModule
  ],
  declarations: [ModalPopupPage]
})
export class ModalPopupPageModule {}
