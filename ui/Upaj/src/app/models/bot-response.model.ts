import { Option } from './option.model';

export class BotResponse {
    text: string;
    options: Array<Option>;
    links: Array<{name: string, address: string}>;
    list: Array<string>;
    image: string;
    key: string;
}