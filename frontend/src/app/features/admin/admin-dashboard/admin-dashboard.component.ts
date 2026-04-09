import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

interface SystemHealth {
  status: string;
  components: {
    database: string;
    redis: string;
    upstox_http: string;
  };
}

interface SystemSetting {
  id: number;
  key: string;
  value: string;
  description?: string;
  updated_at: string;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  health: SystemHealth | null = null;
  settings: SystemSetting[] = [];
  
  newSetting = { key: '', value: '' };
  
  isLoadingHealth = false;
  isLoadingSettings = false;
  isSaving = false;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadHealth();
    this.loadSettings();
  }

  loadHealth() {
    this.isLoadingHealth = true;
    this.http.get<SystemHealth>(`${environment.apiUrl}/admin/health`)
      .subscribe({
        next: (data) => {
          this.health = data;
          this.isLoadingHealth = false;
        },
        error: (err) => {
          console.error('Failed to load system health', err);
          this.isLoadingHealth = false;
        }
      });
  }

  loadSettings() {
    this.isLoadingSettings = true;
    this.http.get<SystemSetting[]>(`${environment.apiUrl}/admin/settings`)
      .subscribe({
        next: (data) => {
          this.settings = data;
          this.isLoadingSettings = false;
        },
        error: (err) => {
          console.error('Failed to load system settings', err);
          this.isLoadingSettings = false;
        }
      });
  }

  saveSetting(setting: SystemSetting) {
    this.isSaving = true;
    this.http.put<SystemSetting>(`${environment.apiUrl}/admin/settings/${setting.key}`, { value: setting.value })
      .subscribe({
        next: (data) => {
          const index = this.settings.findIndex(s => s.key === data.key);
          if (index !== -1) this.settings[index] = data;
          this.isSaving = false;
        },
        error: (err) => {
          console.error('Failed to save setting', err);
          this.isSaving = false;
        }
      });
  }

  addSetting() {
    if (!this.newSetting.key || !this.newSetting.value) return;
    
    this.isSaving = true;
    this.http.put<SystemSetting>(`${environment.apiUrl}/admin/settings/${this.newSetting.key}`, { value: this.newSetting.value })
      .subscribe({
        next: (data) => {
          this.settings.push(data);
          this.newSetting = { key: '', value: '' }; // reset
          this.isSaving = false;
        },
        error: (err) => {
          console.error('Failed to add setting', err);
          this.isSaving = false;
        }
      });
  }
}
