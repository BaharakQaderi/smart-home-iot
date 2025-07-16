/**
 * This file includes polyfills needed by Angular and is loaded before the app.
 * You can add your own extra polyfills to this file.
 */

import 'zone.js/dist/zone';  // Included with Angular CLI.

// Import JIT compiler for development - this ensures it's available at runtime
import '@angular/compiler';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

// Ensure JIT compiler is available globally
declare const require: any;
if (typeof require !== 'undefined') {
  require('@angular/compiler');
} 