import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Guard to ensure only users with the ADMIN role can access the route.
 */
export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn) {
    let isAdmin = false;
    authService.user$.subscribe(user => {
      if (user && user.name === 'admin') { // Assuming role is checked by name or similar for now
        isAdmin = true;
      }
    }).unsubscribe();
    
    if (isAdmin) {
      return true;
    }
  }

  // Not logged in or not an admin
  return router.parseUrl('/dashboard');
};
