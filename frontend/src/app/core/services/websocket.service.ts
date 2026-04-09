import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable, Subject, timer, EMPTY } from 'rxjs';
import { switchMap, retryWhen, delay } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket$: WebSocketSubject<any> | null = null;
  private messagesSubject = new Subject<any>();
  messages$ = this.messagesSubject.asObservable();

  connect(endpoint: string = '/market/ws/feed'): void {
    if (this.socket$ && !this.socket$.closed) {
      return;
    }

    const wsUrl = environment.wsUrl + endpoint;
    this.socket$ = webSocket({
      url: wsUrl,
      openObserver: {
        next: () => console.log('[WS] Connected to ' + endpoint),
      },
      closeObserver: {
        next: () => {
          console.log('[WS] Disconnected from ' + endpoint);
          this.socket$ = null;
          // Attempt reconnect on graceful close too
          this.scheduleReconnect(endpoint);
        },
      },
    });

    this.socket$.subscribe({
      next: (msg) => this.messagesSubject.next(msg),
      error: (err) => {
        console.error('[WS] Error:', err);
        this.socket$ = null;
        this.scheduleReconnect(endpoint);
      },
    });
  }

  private scheduleReconnect(endpoint: string): void {
    console.log('[WS] Scheduling reconnect for ' + endpoint);
    timer(3000).subscribe(() => this.connect(endpoint));
  }

  send(message: any): void {
    this.socket$?.next(message);
  }

  disconnect(): void {
    this.socket$?.complete();
    this.socket$ = null;
  }
}
