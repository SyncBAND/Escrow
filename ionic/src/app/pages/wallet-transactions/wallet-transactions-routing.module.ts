import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { WalletTransactionsPage } from './wallet-transactions.page';

const routes: Routes = [
  {
    path: '',
    component: WalletTransactionsPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class WalletTransactionsPageRoutingModule {}
