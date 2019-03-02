import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Message } from './models/message.model';

const httpOptions = {
  headers: new HttpHeaders({ 'Access-Control-Allow-Origin': '*' })
};

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'Upaj';
  conv_thread: Array<Message>;
  text = "";

  push_query(){
    this.http.post("http://localhost:8000/bot/chat/", {}, httpOptions).subscribe(() => { console.log("Hogaya"); });
  }

  ngOnInit() {

  }

  constructor(private http: HttpClient) {}
}
