import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { WithdrawalDetailsPage } from './withdrawal-details.page';

const routes: Routes = [
  {
    path: '',
    component: WithdrawalDetailsPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class WithdrawalDetailsPageRoutingModule {}
