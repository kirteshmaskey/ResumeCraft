import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { InstrumentSearchResponse } from '../models/instrument.model';

@Injectable({
    providedIn: 'root'
})
export class MarketDataService {
    private endpoint = '/market';

    constructor(private api: ApiService) { }

    searchInstruments(query: string): Observable<InstrumentSearchResponse> {
        return this.api.get<InstrumentSearchResponse>(`${this.endpoint}/instruments/search`, { q: query });
    }
}
