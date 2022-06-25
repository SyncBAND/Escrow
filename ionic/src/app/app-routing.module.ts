import { NgModule } from '@angular/core';
import { PreloadAllModules, RouterModule, Routes } from '@angular/router';

import { AuthGuard } from './shared/guards/auth/auth.guard';
import { LoggedinGuard } from './shared/guards/loggedin/loggedin.guard';

const routes: Routes = [
  {
    path: '',
    loadChildren: () => import('./tabs/tabs.module').then(m => m.TabsPageModule)
  },
  {
    path: 'intro',
    loadChildren: () => import('./pages/intro/intro.module').then( m => m.IntroPageModule)
  },
  {
    path: 'user-details',
    loadChildren: () => import('./pages/user-details/user-details.module').then( m => m.UserDetailsPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'verify-details',
    loadChildren: () => import('./pages/verify-details/verify-details.module').then( m => m.VerifyDetailsPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'verify-email',
    loadChildren: () => import('./pages/verify-email/verify-email.module').then( m => m.VerifyEmailPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'update-password',
    loadChildren: () => import('./pages/update-password/update-password.module').then( m => m.UpdatePasswordPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'support',
    loadChildren: () => import('./pages/support/support.module').then( m => m.SupportPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'payment-options',
    loadChildren: () => import('./pages/payment-options/payment-options.module').then( m => m.PaymentOptionsPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'view-all-history',
    loadChildren: () => import('./pages/view-all-history/view-all-history.module').then( m => m.ViewAllHistoryPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'view-history',
    loadChildren: () => import('./pages/view-history/view-history.module').then( m => m.ViewHistoryPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'chat',
    loadChildren: () => import('./pages/chat/chat.module').then( m => m.ChatPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'chat-list',
    loadChildren: () => import('./pages/chat-list/chat-list.module').then( m => m.ChatListPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'withdrawal-details',
    loadChildren: () => import('./pages/withdrawal-details/withdrawal-details.module').then( m => m.WithdrawalDetailsPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'withdrawal',
    loadChildren: () => import('./pages/withdrawal/withdrawal.module').then( m => m.WithdrawalPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'support-list',
    loadChildren: () => import('./pages/support-list/support-list.module').then( m => m.SupportListPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'wallet-transactions',
    loadChildren: () => import('./pages/wallet-transactions/wallet-transactions.module').then( m => m.WalletTransactionsPageModule),
    canActivate: [AuthGuard]
  },
  // --- modals --- //
  {
    path: 'payment',
    loadChildren: () => import('./modals/payment/payment.module').then( m => m.PaymentPageModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'login',
    loadChildren: () => import('./modals/login/login.module').then( m => m.LoginPageModule),
    canActivate: [LoggedinGuard]
  },
  {
    path: 'register',
    loadChildren: () => import('./modals/register/register.module').then( m => m.RegisterPageModule),
    canActivate: [LoggedinGuard]
  },
  {
    path: 'forgot-password',
    loadChildren: () => import('./modals/forgot-password/forgot-password.module').then( m => m.ForgotPasswordPageModule),
    canActivate: [LoggedinGuard]
  },
  {
    path: 'delivered',
    loadChildren: () => import('./modals/delivered/delivered.module').then( m => m.DeliveredPageModule)
  },
  {
    path: 'modal-popup',
    loadChildren: () => import('./modals/modal-popup/modal-popup.module').then( m => m.ModalPopupPageModule),
  },
  // --- end of modals --- //
];
@NgModule({
  imports: [
    RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule {}
