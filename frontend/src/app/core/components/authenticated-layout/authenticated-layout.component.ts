import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { Subscription, filter, map } from 'rxjs';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { AuthService, User } from '../../services/auth.service';

@Component({
    selector: 'app-authenticated-layout',
    standalone: true,
    imports: [CommonModule, RouterOutlet, SidebarComponent],
    templateUrl: './authenticated-layout.component.html',
    styleUrls: ['./authenticated-layout.component.scss']
})
export class AuthenticatedLayoutComponent implements OnInit, OnDestroy {
    user: User | null = null;
    pageTitle = 'Dashboard';
    private subs: Subscription[] = [];

    private readonly titleMap: Record<string, string> = {
        '/dashboard': 'Dashboard',
        '/templates': 'Resume Templates',
        '/resumes': 'Master Resumes',
        '/generator': 'AI Generator',
        '/settings': 'Settings',
    };

    constructor(
        private authService: AuthService,
        private router: Router
    ) { }

    ngOnInit(): void {
        // Load user profile
        this.subs.push(
            this.authService.user$.subscribe((u) => (this.user = u))
        );
        this.authService.initAuth();

        // Dynamic page title based on route
        this.subs.push(
            this.router.events
                .pipe(
                    filter((event) => event instanceof NavigationEnd),
                    map((event) => (event as NavigationEnd).urlAfterRedirects || (event as NavigationEnd).url)
                )
                .subscribe((url) => {
                    // Find the most specific matching title
                    const match = Object.keys(this.titleMap)
                        .sort((a, b) => b.length - a.length)
                        .find((path) => url.startsWith(path));
                    this.pageTitle = match ? this.titleMap[match] : 'Dashboard';
                })
        );

        // Set initial title
        const currentUrl = this.router.url;
        const match = Object.keys(this.titleMap)
            .sort((a, b) => b.length - a.length)
            .find((path) => currentUrl.startsWith(path));
        this.pageTitle = match ? this.titleMap[match] : 'Dashboard';
    }

    ngOnDestroy(): void {
        this.subs.forEach((s) => s.unsubscribe());
    }
}
