import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BadgeService {

  private profileSubject: Subject<number>;
  private _profileNotifications:Observable<number>;

  private paymentSubject: Subject<number>;
  private _paymentFromOthersNotifications:Observable<number>;

  private noticeSubject: Subject<number>;
  private _noticeNotifications:Observable<number>;

  constructor() {

    this.profileSubject = new Subject();
    this._profileNotifications = this.profileSubject.asObservable();

    this.paymentSubject = new Subject();
    this._paymentFromOthersNotifications = this.paymentSubject.asObservable();

    this.noticeSubject = new Subject();
    this._noticeNotifications = this.noticeSubject.asObservable();
    
  }

  // profile tab
  get profileNotifications() {
    return this._profileNotifications;
  }

  updateProfileNotifications(value) {
    this.profileSubject.next(value)
  }

  resetProfileNotifications() {
    this.profileSubject.next(0)
  }

  // history tab
  get paymentFromOthersNotifications() {
    return this._paymentFromOthersNotifications;
  }

  updatePaymentFromOthersNotifications(value) {
    this.paymentSubject.next(value)
  }

  resetPaymentFromOthersNotifications() {
    this.paymentSubject.next(0)
  }

  // under profile - for notifications from admin
  get noticeNotifications() {
    return this._noticeNotifications;
  }

  updateNoticeNotifications(value) {
    this.noticeSubject.next(value)
  }

  resetNoticeNotifications() {
    this.noticeSubject.next(0)
  }

}
