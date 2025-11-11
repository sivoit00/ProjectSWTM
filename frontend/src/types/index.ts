/**
 * Type definitions for the application
 */

export interface Kunde {
  id?: number;
  name: string;
  email: string;
  telefon: string;
}

export interface Fahrzeug {
  id?: number;
  marke: string;
  modell: string;
  baujahr: number;
  kunde_id: number;
}

export interface Werkstatt {
  id?: number;
  name: string;
  adresse: string;
  plz: string;
  ort: string;
}

export interface Auftrag {
  id?: number;
  beschreibung: string;
  status: string;
  fahrzeug_id: number;
  werkstatt_id: number;
  kosten?: number;
  erstellt_am?: string;
}

export interface ChatMessage {
  message: string;
}

export interface ChatResponse {
  response: string;
}
