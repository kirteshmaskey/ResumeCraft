export interface InstrumentInfo {
    instrument_key: string;
    symbol: string;
    name: string;
    exchange: string;
    segment?: string;
    instrument_type?: string;
    lot_size?: number;
    tick_size?: number;
    expiry?: string;
}

export interface InstrumentSearchResponse {
    query: string;
    results: InstrumentInfo[];
    total: number;
}
