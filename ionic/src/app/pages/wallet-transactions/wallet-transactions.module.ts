import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { IonicModule } from '@ionic/angular';

import { WalletTransactionsPageRoutingModule } from './wallet-transactions-routing.module';

import { WalletTransactionsPage } from './wallet-transactions.page';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    WalletTransactionsPageRoutingModule
  ],
  declarations: [WalletTransactionsPage]
})
export class WalletTransactionsPageModule {}
