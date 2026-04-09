import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

export interface Notification {
  id: number;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
  category: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private ws: WebSocket | null = null;
  private unreadCountSubj = new BehaviorSubject<number>(0);
  private notificationsSubj = new BehaviorSubject<Notification[]>([]);
  private activeToastsSubj = new BehaviorSubject<Notification[]>([]);
  private pingInterval: any = null;

  unreadCount$ = this.unreadCountSubj.asObservable();
  notifications$ = this.notificationsSubj.asObservable();
  activeToasts$ = this.activeToastsSubj.asObservable();

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  /**
   * Initialize history and connect WebSocket for live updates.
   */
  init() {
    this.fetchHistory();
    this.connectWs();
  }

  private fetchHistory() {
    this.http.get<Notification[]>(`${environment.apiUrl}/notifications?limit=20`)
      .subscribe({
        next: (data) => {
          this.notificationsSubj.next(data);
          this.updateUnreadCount(data);
        },
        error: (err) => console.error('Failed to fetch notification history', err)
      });
  }

  private connectWs() {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      return;
    }

    const token = this.authService.getAccessToken();
    if (!token) {
      console.warn('[NotificationService] No token available for WS connection');
      return;
    }

    if (this.ws) {
      this.stopHeartbeat();
      this.ws.close();
    }

    // Convert http(s):// to ws(s)://
    const wsUrl = environment.apiUrl.replace(/^http/, 'ws');
    this.ws = new WebSocket(`${wsUrl}/notifications/ws?token=${token}`);

    this.ws.onopen = () => {
      console.log('[NotificationService] Connected');
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'pong') return;

        if (payload.type === 'SYSTEM_NOTIFICATION') {
          this.handleIncomingNotification(payload.data);
        }
      } catch (e) {
        console.error('Error parsing notification WS message', e);
      }
    };

    this.ws.onclose = (event: CloseEvent) => {
      console.log(`Notification WS Closed (Code: ${event.code}, Reason: ${event.reason})`);
      this.stopHeartbeat();

      if (event.code === 1008) {
        console.warn('[NotificationService] Auth failure on WS. Attempting token refresh...');
        this.authService.refreshToken().subscribe({
          next: () => {
            console.log('[NotificationService] Token refreshed. Reconnecting...');
            this.connectWs();
          },
          error: () => {
            console.error('[NotificationService] Token refresh failed. Stopping reconnection.');
          }
        });
      } else {
        console.log('Notification WS Closed. Attempting reconnect in 5s...');
        setTimeout(() => this.connectWs(), 5000);
      }
    };
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'ping' }));
      }
    }, 30000);
  }

  private stopHeartbeat() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private handleIncomingNotification(notification: Notification) {
    const current = this.notificationsSubj.getValue();
    // Add to top of list
    const updated = [notification, ...current].slice(0, 50); // Keep last 50
    this.notificationsSubj.next(updated);
    this.updateUnreadCount(updated);

    // Add to toasts list for 5 seconds
    this.showToast(notification);
  }

  private showToast(notification: Notification) {
    const currentToasts = this.activeToastsSubj.getValue();
    const newToasts = [...currentToasts, notification];
    this.activeToastsSubj.next(newToasts);

    setTimeout(() => {
      this.removeToast(notification.id);
    }, 5000);
  }

  removeToast(id: number) {
    const current = this.activeToastsSubj.getValue();
    this.activeToastsSubj.next(current.filter(t => t.id !== id));
  }

  markAsRead(id: number) {
    this.http.put(`${environment.apiUrl}/notifications/${id}/read`, {}).subscribe(() => {
      const current = this.notificationsSubj.getValue();
      const updated = current.map(n => n.id === id ? { ...n, is_read: true } : n);
      this.notificationsSubj.next(updated);
      this.updateUnreadCount(updated);
    });
  }

  markAllAsRead() {
    const unread = this.notificationsSubj.getValue().filter(n => !n.is_read);
    unread.forEach(n => this.markAsRead(n.id));
  }

  private updateUnreadCount(notifications: Notification[]) {
    const unread = notifications.filter(n => !n.is_read).length;
    this.unreadCountSubj.next(unread);
  }

  disconnect() {
    console.log('[NotificationService] Explicitly disconnecting');
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.onclose = null; // Prevent reconnect loop
      this.ws.close();
      this.ws = null;
    }
  }
}
