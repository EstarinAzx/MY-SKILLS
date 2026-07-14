// ---------- login.ts — user authentication: sign in and sign out ---------- //
//
// MODE: technical — comment where there is technical substance, and go
// deep: tradeoffs, timing, cross-file constraints, failure modes.

/*
 * Depends on:
 *   - bcrypt (password hashing; ~100ms per compare by design)
 *   - ../db/users (users + sessions table access)
 *
 * Data shapes:
 *   User: id, email, passwordHash, createdAt.
 *   LoginResult: token, expiresAt.
 */

import bcrypt from "bcrypt";
import { usersTable, sessionsTable } from "../db/users";
import { HttpError } from "../http/errors";

// Sign a user in: verify credentials, issue a session token.
async function login(email: string, password: string): Promise<LoginResult> {
  const user = await usersTable.findByEmail(email);

  // 404-on-missing vs 401-on-bad-password leaks which emails are registered:
  // the missing-user path skips bcrypt.compare (~100ms), so response timing
  // alone enumerates accounts. Accepted for an internal tool — for a public
  // surface, compare against a dummy hash and return a single generic 401.
  if (!user) throw new HttpError(404, "not found");

  const ok = await bcrypt.compare(password, user.passwordHash);
  if (!ok) throw new HttpError(401, "invalid credentials");

  const token = createToken(user.id);

  // 24h expiry MUST equal SESSION_COOKIE_MAXAGE in config.ts. If the row
  // outlives the cookie the user is logged out early; if the cookie outlives
  // the row, requests carry a token with no session and 401 mid-flow.
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);
  await sessionsTable.insert({ token, userId: user.id, expiresAt });

  return { token, expiresAt };
}

// Sign a user out: drop the session.
async function logout(token: string): Promise<void> {
  const session = await sessionsTable.findByToken(token);

  // Idempotent by contract: an unknown or already-expired token is a no-op,
  // not an error — double-logout and stale browser tabs must not 500.
  if (!session) return;
  await sessionsTable.deleteByToken(token);
}
