import { Injectable } from '@angular/core';
import { CanLoad, Router } from '@angular/router';

import { intro } from '../../local_storage_variables';

@Injectable({
  providedIn: 'root'
})
export class IntroGuard implements CanLoad {
  
  constructor(private router: Router) { }
 
  async canLoad(): Promise<boolean> {
      const hasSeenIntro = localStorage.getItem(intro);
      if (hasSeenIntro && (hasSeenIntro === 'true')) {
        return true;
      } else {
        this.router.navigateByUrl('/intro', { replaceUrl: true });
        return false;
      }
  }

}