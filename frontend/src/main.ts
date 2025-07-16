import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { enableProdMode } from '@angular/core';
import { AppModule } from './app/app.module';
import { environment } from './environments/environment';

// Ensure JIT compiler is available
import '@angular/compiler';

if (environment.production) {
  enableProdMode();
}

// Use JIT compilation explicitly
platformBrowserDynamic().bootstrapModule(AppModule, {
  preserveWhitespaces: false,
  ngZone: 'zone.js'
})
  .catch(err => {
    console.error('Bootstrap error:', err);
    console.error('Error details:', err.message, err.stack);
    
    // Try to provide more helpful error information
    if (err.message && err.message.includes('JIT compiler unavailable')) {
      console.error('JIT compiler is not available. This usually means the application is trying to compile templates at runtime.');
      console.error('Make sure @angular/compiler is included in the bundle and AOT is disabled for development.');
    }
  }); 