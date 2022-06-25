import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { ViewAllHistoryPageRoutingModule } from './view-all-history-routing.module';

import { ViewAllHistoryPage } from './view-all-history.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    ViewAllHistoryPageRoutingModule
  ],
  declarations: [ViewAllHistoryPage]
})
export class ViewAllHistoryPageModule {}
