import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, Subscription } from 'rxjs';
import { NotificationService, Notification } from '../../services/notification.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-notifications-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications-panel.component.html',
  styleUrls: ['./notifications-panel.component.scss']
})
export class NotificationsPanelComponent implements OnInit, OnDestroy {
  isOpen = false;
  unreadCount$!: Observable<number>;
  notifications$!: Observable<Notification[]>;
  private authSub?: Subscription;

  constructor(
    private notificationService: NotificationService,
    private authService: AuthService
  ) { }

  ngOnInit() {
    this.unreadCount$ = this.notificationService.unreadCount$;
    this.notifications$ = this.notificationService.notifications$;

    // Reactively connect/disconnect based on auth state
    this.authSub = this.authService.user$.subscribe((user: any) => {
      if (user) {
        this.notificationService.init();
      } else {
        this.notificationService.disconnect();
      }
    });
  }

  ngOnDestroy() {
    this.authSub?.unsubscribe();
    this.notificationService.disconnect();
  }

  togglePanel() {
    this.isOpen = !this.isOpen;
  }

  closePanel() {
    this.isOpen = false;
  }

  markAllRead() {
    this.notificationService.markAllAsRead();
  }

  handleItemClick(notif: Notification) {
    if (!notif.is_read) {
      this.notificationService.markAsRead(notif.id);
    }
    // E.g., Optionally close panel or route to a specific page
  }

  getIconForCategory(category: string): string {
    switch (category.toUpperCase()) {
      case 'RISK': return 'fa-shield-alt';
      case 'EXECUTION': return 'fa-bolt';
      case 'ML_SIGNAL': return 'fa-brain';
      case 'SYSTEM': return 'fa-server';
      default: return 'fa-info-circle';
    }
  }
}
