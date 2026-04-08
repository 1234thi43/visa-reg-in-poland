export type City = 'Пинск' | 'Барановичи';

export interface SlotInfo {
  city: City;
  date: string;
  time: string | null;
  details: string;
}

export type CheckStatus = 'idle' | 'checking' | 'waiting_for_auth' | 'ok' | 'error';

export interface SlotsResponse {
  slots: SlotInfo[];
  last_check: string | null;
  status: CheckStatus;
}

export interface StatusResponse {
  status: CheckStatus;
  last_check: string | null;
  error_message: string | null;
  is_monitoring: boolean;
}

export const VFS_BOOKING_URL = 'https://visa.vfsglobal.com/blr/ru/pol/book-an-appointment';
