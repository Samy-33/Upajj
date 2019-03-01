import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'Upaj';
  conv_thread: Array<{by_user: Boolean; msg: string}>;
  constructor(private http: HttpClient) {}
}
