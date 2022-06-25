import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { WithdrawalPage } from './withdrawal.page';

const routes: Routes = [
  {
    path: '',
    component: WithdrawalPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class WithdrawalPageRoutingModule {}
