// ---------- login.ts — user authentication: sign in and sign out ---------- //
//
// MODE: default — only the few most critical why-comments. The title banner
// and file-top block carry the structure; bodies stay sparse.

/*
 * Depends on:
 *   - bcrypt (password hashing)
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
  if (!user) throw new HttpError(404, "not found");

  const ok = await bcrypt.compare(password, user.passwordHash);
  if (!ok) throw new HttpError(401, "invalid credentials");

  const token = createToken(user.id);

  // 24h expiry must match SESSION_COOKIE_MAXAGE in config.ts.
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);
  await sessionsTable.insert({ token, userId: user.id, expiresAt });

  return { token, expiresAt };
}

// Sign a user out: drop the session. Idempotent.
async function logout(token: string): Promise<void> {
  const session = await sessionsTable.findByToken(token);
  if (!session) return;
  await sessionsTable.deleteByToken(token);
}
