export type MessageType = 'text' | 'invoice' | 'document' | 'voice' | 'photo' | 'video_note' | 'poll';

export type FileUploadType = 'document' | 'voice' | 'photo' | 'video_note';

export interface InlineKeyboardButtonData {
  text?: string;
  callback_data?: string;
}

export type InlineKeyboard = InlineKeyboardButtonData[][];

export interface ReplyKeyboardButtonData {
  text?: string;
}

export type ReplyKeyboard = ReplyKeyboardButtonData[][];

export type ReplyMarkup = {
  inline_keyboard?: InlineKeyboard;
  keyboard?: ReplyKeyboard;
} & Record<string, unknown>;

export interface MessageEntity {
  type: string;
  offset: number;
  length: number;
  url?: string;
  language?: string;
}

export interface MessageResponse {
  type: MessageType;
  text?: string;
  file_id?: string;
  filename?: string;
  message_id: number;
  title?: string;
  description?: string;
  currency?: string;
  total_amount?: number;
  reply_markup?: ReplyMarkup | null;
  poll_question?: string;
  poll_options?: Array<{ text: string; voter_count: number }>;
  poll_id?: string;
  entities?: MessageEntity[];
}

export interface BotCommandInfo {
  command: string;
  description: string;
}

export interface BotStateResponse {
  commands: BotCommandInfo[];
  menu_button_type: string;
}
