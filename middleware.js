const CANARY_HOST = "canary.hdrapp.tech";
const USER = "bbcanary";
const PASS = "h3-throwaway-2026";
const GATED = ["/canary.html", "/forbidden.html"];

export default function middleware(request) {
  const url = new URL(request.url);
  const host = request.headers.get("host") || "";
  if (host !== CANARY_HOST) return; // product domains: pass through untouched

  if (url.pathname === "/robots.txt") {
    return new Response(
      "User-agent: atlassian-bot\nAllow: /canary.html\nDisallow: /forbidden.html\n\nUser-agent: *\nDisallow: /\n",
      { headers: { "content-type": "text/plain" } }
    );
  }
  if (url.pathname === "/") {
    url.pathname = "/h3/index.html";
    return Response.redirect(url);
  }
  if (url.pathname === "/canary.html" || url.pathname === "/forbidden.html") {
    const auth = request.headers.get("authorization") || "";
    let ok = false;
    if (auth.startsWith("Basic ")) {
      try { ok = atob(auth.slice(6)) === USER + ":" + PASS; } catch (e) { ok = false; }
    }
    if (!ok) {
      return new Response("auth required", {
        status: 401,
        headers: { "WWW-Authenticate": 'Basic realm="bb-canary"' },
      });
    }
    url.pathname = "/h3" + url.pathname;
    return Response.redirect(url);
  }
  return; // any other path on the canary host: default handling
}

export const config = { matcher: ["/", "/robots.txt", "/canary.html", "/forbidden.html"] };
