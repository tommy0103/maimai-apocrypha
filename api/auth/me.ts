import type { VercelRequest, VercelResponse } from "@vercel/node";
import crypto from "node:crypto";

const JWT_SECRET = process.env.JWT_SECRET || "change-me-in-production";

const base64urlDecode = (input: string) =>
  Buffer.from(input, "base64url").toString("utf8");

// Simple JWT verification (for production, use a library like jsonwebtoken)
function verifyJWT(token: string): Record<string, any> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const [header, payload, signature] = parts;
    const expected = crypto
      .createHmac("sha256", JWT_SECRET)
      .update(`${header}.${payload}`)
      .digest("base64url");
    if (signature !== expected) return null;

    const parsedPayload = JSON.parse(base64urlDecode(payload));
    const exp = parsedPayload.exp;
    if (exp && exp < Math.floor(Date.now() / 1000)) {
      return null; // Expired
    }

    return parsedPayload;
  } catch {
    return null;
  }
}

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const token = authHeader.substring(7);
  const payload = verifyJWT(token);

  if (!payload) {
    return res.status(401).json({ error: "Invalid or expired token" });
  }

  return res.json({
    user_id: payload.user_id,
    username: payload.username,
    avatar_url: payload.avatar_url,
  });
}
