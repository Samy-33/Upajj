import { Option } from './option.model';

export class BotResponse {
    text: string;
    options: Array<Option>;
    links: Array<string>;
    list: Array<string>;
    key: string;
}