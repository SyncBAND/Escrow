import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { AuthService } from '../../../shared/service/auth/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AutocompleteService {

  constructor(private authService: AuthService, private http: HttpClient) { }

  getData(term: string = null, getdata: string): Observable<string[]> {
    return new Observable((observer) => {
      let getDataNamePromise: Promise<any>;

      getDataNamePromise = new Promise((resolve, reject) => {

        this.authService.refreshToken().subscribe(()=>{

          this.http.get<string[]>(getdata, {'params': {'term': term, 'mode': (localStorage.getItem('mode') != null ? localStorage.getItem('mode') : 'enduser').toUpperCase()} }).subscribe((data: any) => {
            resolve(data);
          },(err: any)=>{
            reject(err)
          });

        },(err: any)=>{
          reject(err)
        });

      });

      getDataNamePromise.then((data) => {
        observer.next(data);
      });

    });
  }

}
