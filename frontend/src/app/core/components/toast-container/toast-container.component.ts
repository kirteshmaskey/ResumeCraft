import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService, Notification } from '../../services/notification.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-toast-container',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-container">
      <div 
        *ngFor="let toast of activeToasts$ | async" 
        class="toast"
        [ngClass]="toast.level.toLowerCase()"
      >
        <div class="toast-icon">
          <i class="fas" [ngClass]="getIcon(toast.level)"></i>
        </div>
        <div class="toast-content">
          <h4 class="toast-title">{{ toast.title }}</h4>
          <p class="toast-message">{{ toast.message }}</p>
        </div>
        <button class="toast-close" (click)="removeToast(toast.id)">&times;</button>
      </div>
    </div>
  `,
  styleUrls: ['./toast-container.component.scss']
})
export class ToastContainerComponent implements OnInit {
  activeToasts$!: Observable<Notification[]>;

  constructor(private notificationService: NotificationService) {}

  ngOnInit() {
    this.activeToasts$ = this.notificationService.activeToasts$;
  }

  removeToast(id: number) {
    this.notificationService.removeToast(id);
  }

  getIcon(level: string): string {
    switch(level.toLowerCase()) {
      case 'success': return 'fa-check-circle';
      case 'error': return 'fa-times-circle';
      case 'warning': return 'fa-exclamation-triangle';
      default: return 'fa-info-circle';
    }
  }
}
