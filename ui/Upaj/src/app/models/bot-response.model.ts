import { Option } from './option.model';

export class BotResponse {
    text: string;
    options: Array<Option>;
    key: string;
}