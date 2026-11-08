const CANARY_HOST = "canary.hdrapp.tech";
const USER = "bbcanary";
const PASS = "h3-throwaway-2026";
const GATED = new Set([
  "/canary.html", "/canary", "/h3/canary.html", "/h3/canary",
  "/forbidden.html", "/forbidden", "/h3/forbidden.html", "/h3/forbidden",
]);

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
  if (GATED.has(url.pathname)) {
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
    if (!url.pathname.startsWith("/h3/")) {
      url.pathname = "/h3" + url.pathname.replace(/\.html$/, "") + ".html";
      return Response.redirect(url);
    }
    return; // authenticated, canonical path: serve the static file
  }
  return;
}

export const config = {
  matcher: ["/", "/robots.txt", "/canary.html", "/canary", "/forbidden.html", "/forbidden",
            "/h3/canary.html", "/h3/canary", "/h3/forbidden.html", "/h3/forbidden"],
};
