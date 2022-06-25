import { Component } from '@angular/core';
import { BadgeService } from '../shared/service/badge/badge.service'

import { Observable } from 'rxjs';

@Component({
  selector: 'app-tabs',
  templateUrl: 'tabs.page.html',
  styleUrls: ['tabs.page.scss']
})
export class TabsPage {

  profileCount: Observable<number>;
  historyCount: Observable<number>;

  constructor(badgeService: BadgeService) {
    this.profileCount = badgeService.profileNotifications;
    this.historyCount = badgeService.paymentFromOthersNotifications;
  }

}
