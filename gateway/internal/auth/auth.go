// Package auth handles JWT issuance and verification.
//
// Phase 3 build. Key decisions to make and record in an ADR:
//   - access token expiry (short — minutes, not hours)
//   - refresh token strategy (rotation on use is the safer default)
//   - where tokens live client-side (NOT localStorage — discuss why in
//     docs/02-THREAT-MODEL.md)
package auth

// TODO: Login handler — verify credentials, issue access + refresh token
// TODO: Middleware — verify token on protected routes, attach user identity to request context
// TODO: RefreshToken handler
