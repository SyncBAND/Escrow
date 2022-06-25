import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ViewAllHistoryPage } from './view-all-history.page';

const routes: Routes = [
  {
    path: '',
    component: ViewAllHistoryPage
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ViewAllHistoryPageRoutingModule {}
