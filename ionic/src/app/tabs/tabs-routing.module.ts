import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TabsPage } from './tabs.page';

import { IntroGuard } from '../shared/guards/intro/intro.guard';

const routes: Routes = [
  {
    path: 'tabs',
    component: TabsPage,
    children: [
      {
        path: 'profile',
        loadChildren: () => import('../tab1/tab1.module').then(m => m.Tab1PageModule),
        canLoad: [IntroGuard] // Check if we should show the walk-through or forward to inside
      },
      {
        path: 'pay',
        loadChildren: () => import('../tab2/tab2.module').then(m => m.Tab2PageModule),
        canLoad: [IntroGuard] // Check if we should show the walk-through or forward to inside
      },
      {
        path: 'history',
        loadChildren: () => import('../tab3/tab3.module').then(m => m.Tab3PageModule),
        canLoad: [IntroGuard] // Check if we should show the walk-through or forward to inside
      },
      {
        path: '',
        redirectTo: '/tabs/pay',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: '',
    redirectTo: '/tabs/pay',
    pathMatch: 'full'
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
})
export class TabsPageRoutingModule {}
