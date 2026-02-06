import type { VercelRequest, VercelResponse } from "@vercel/node";
import crypto from "node:crypto";

const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID;
const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET;
const JWT_SECRET = process.env.JWT_SECRET || "change-me-in-production";

const base64url = (input: string | Buffer) =>
  Buffer.from(input).toString("base64url");

// Simple JWT implementation (for production, use a library like jsonwebtoken)
function signJWT(payload: Record<string, any>): string {
  const header = base64url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const encodedPayload = base64url(JSON.stringify(payload));
  const signature = crypto
    .createHmac("sha256", JWT_SECRET)
    .update(`${header}.${encodedPayload}`)
    .digest("base64url");
  return `${header}.${encodedPayload}.${signature}`;
}

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { code } = req.query;

  if (!code) {
    return res.status(400).json({ error: "Missing code parameter" });
  }

  if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) {
    return res.status(500).json({ error: "GitHub OAuth not configured" });
  }

  try {
    // Exchange code for access token
    const tokenResponse = await fetch(
      "https://github.com/login/oauth/access_token",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          client_id: GITHUB_CLIENT_ID,
          client_secret: GITHUB_CLIENT_SECRET,
          code: code as string,
        }),
      }
    );

    const tokenData = await tokenResponse.json();

    if (tokenData.error) {
      return res.status(400).json({ error: tokenData.error_description });
    }

    const accessToken = tokenData.access_token;

    // Get user info from GitHub
    const userResponse = await fetch("https://api.github.com/user", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/json",
      },
    });

    const userData = await userResponse.json();

    if (!userData.login) {
      return res.status(400).json({ error: "Failed to get user info" });
    }

    // Create JWT
    const jwt = signJWT({
      user_id: userData.id,
      username: userData.login,
      avatar_url: userData.avatar_url,
      exp: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60, // 7 days
    });

    const forwardedProto = req.headers["x-forwarded-proto"] as string | undefined;
    const forwardedHost = req.headers["x-forwarded-host"] as string | undefined;
    const host = forwardedHost || req.headers.host || "";
    const proto = forwardedProto || "https";
    const baseUrl = process.env.BASE_URL || `${proto}://${host}`;

    // Redirect back to site with token
    const redirectUrl = new URL(`${baseUrl}/auth/callback`);
    redirectUrl.searchParams.set("token", jwt);

    return res.redirect(redirectUrl.toString());
  } catch (error) {
    console.error("OAuth callback error:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
}

// JWT not secure
// TODO: use http only cookie to store token
