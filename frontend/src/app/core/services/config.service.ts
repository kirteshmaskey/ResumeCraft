import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { tap } from 'rxjs/operators';
import { Title } from '@angular/platform-browser';

export interface PublicConfig {
    appName: string;
    version: string;
    environment: string;
    debug: boolean;
}

@Injectable({
    providedIn: 'root',
})
export class ConfigService {
    private configSignal = signal<PublicConfig>({
        appName: environment.appName,
        version: '1.0.0',
        environment: 'development',
        debug: false,
    });

    readonly config = this.configSignal.asReadonly();

    constructor(private http: HttpClient, private titleService: Title) { }

    loadConfig() {
        return this.http.get<PublicConfig>(`${environment.apiUrl}/config`).pipe(
            tap((config) => {
                this.configSignal.set(config);
                this.titleService.setTitle(config.appName);
            })
        );
    }

    get appName() {
        return this.config().appName;
    }
}
