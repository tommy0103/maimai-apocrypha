import type { VercelRequest, VercelResponse } from "@vercel/node";

const JWT_SECRET = process.env.JWT_SECRET || "change-me-in-production";

// Simple JWT verification (for production, use a library like jsonwebtoken)
function verifyJWT(token: string): Record<string, any> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const payload = JSON.parse(atob(parts[1]));
    const exp = payload.exp;
    if (exp && exp < Math.floor(Date.now() / 1000)) {
      return null; // Expired
    }

    return payload;
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
