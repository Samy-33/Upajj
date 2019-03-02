import { Component, OnInit, ViewChild, AfterContentChecked } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Message } from './models/message.model';
import { Query } from './models/query.model';
import { BotResponse } from './models/bot-response.model';
import { Option } from './models/option.model';
import { NgxAutoScroll } from "ngx-auto-scroll";

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
  withCredentials: true
};
const CHAT_URL = "http://192.168.1.85:8000/bot/chat/";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, AfterContentChecked {
  title = 'Upaj';
  last_request = undefined;
  @ViewChild(NgxAutoScroll) ngxAutoScroll: NgxAutoScroll;
  all_lang = [
    {
      name: "English",
      code: "en"
    },
    {
      name: "Hindi",
      code: "hi"
    }
  ];
  selected_lang = this.all_lang[0].code;
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

  scrollToView() {
    this.ngxAutoScroll.forceScrollDown();
  }

  push_query(query: Query){
    query.key = this.key;
    query.location = "Jabalpur";
    query.lang = this.selected_lang;
    this.push_conv(true, query.text);
    this.scrollToView();
    this.bot_thinking = true;
    this.current_query = new Query();
    this.http.post<BotResponse>(CHAT_URL, query, httpOptions).subscribe((res) => {
      this.bot_thinking = false;
      // console.log(res);
      this.push_conv(false, res.text);
      this.key = res.key;
      this.current_options = res.options ? res.options: new Array<Option>();
    }, (error) => {
      this.last_request = error.statusText;
      console.log(error);
      this.bot_thinking = false;
      this.push_conv(false, "Drat! We ran into an error we didn't expect. Try again maybe!");
    });
    this.scrollToView();
  }

  push_option(opt: Option) {
    var query = this.current_query;
    query.option = opt.key;
    query.text = opt.value;
    this.push_query(query);
  }

  select_lang(lang: string) {
    this.selected_lang = lang;
    console.log(this.selected_lang);
  }

  ngOnInit() {
  }

  ngAfterContentChecked() {
    this.scrollToView();
  }

  constructor(private http: HttpClient) {
  }
}
