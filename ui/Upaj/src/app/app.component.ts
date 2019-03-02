import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Message } from './models/message.model';
import { Query } from './models/query.model';
import { BotResponse } from './models/bot-response.model';
import { Option } from './models/option.model';

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
  withCredentials: true
};
const CHAT_URL = "http://localhost:8000/bot/chat/";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'Upaj';
  key: string;
  conv_thread = new Array<Message>();
  current_query: Query = new Query();
  current_options = new Array<Option>();
  bot_thinking = false;

  push_conv(by_user: Boolean, msg: string){
    var message = new Message();
    message.msg = msg;
    message.by_user = by_user;
    this.conv_thread.push(message);
  }

  push_query(query: Query){
    query.key = this.key;
    query.location = "Jabalpur";
    if(query.option)
      this.push_conv(true, query.option);
    else
      this.push_conv(true, this.current_query.text);
    this.bot_thinking = true;
    this.current_query = new Query();
    this.http.post<BotResponse>(CHAT_URL, query, httpOptions).subscribe((res) => { 
      this.bot_thinking = false;
      console.log(res);
      this.push_conv(false, res.text);
      this.key = res.key;
      this.current_options = res.options;
    }, () => {
      this.bot_thinking = false;
      this.push_conv(false, "Drat! We ran into an error we didn't expect. Try again maybe!");
    });
  }

  push_option(opt: Option) {
    console.log(this.key);
    var query = this.current_query;
    query.option = opt.key;
    this.push_query(query);
  }

  ngOnInit() {
  }

  constructor(private http: HttpClient) {}
}
