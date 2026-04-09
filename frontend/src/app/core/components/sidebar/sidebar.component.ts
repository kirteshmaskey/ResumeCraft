import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService, User } from '../../services/auth.service';

@Component({
    selector: 'app-sidebar',
    standalone: true,
    imports: [CommonModule, RouterModule],
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit, OnDestroy {
    user: User | null = null;
    private subs: Subscription[] = [];

    constructor(
        private authService: AuthService
    ) { }

    ngOnInit(): void {
        this.subs.push(
            this.authService.user$.subscribe((u) => (this.user = u))
        );
    }

    logout(): void {
        this.authService.logout();
    }

    ngOnDestroy(): void {
        this.subs.forEach((s) => s.unsubscribe());
    }
}
