// Run from the backend/websocket bench; auth JSON contains an existing session cookie.
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import assert from "node:assert/strict";
import { request as httpRequest } from "node:http";
import { request as httpsRequest } from "node:https";

const require = createRequire(resolve("apps/frappe/package.json"));
const { io } = require("socket.io-client");
const { cookie } = JSON.parse(readFileSync(process.argv[2], "utf8"));
const origin = process.env.ATLAS_REALTIME_ORIGIN || "https://erp.atlasuse.site";
const site = process.env.ATLAS_REALTIME_SITE || "erp.atlasuse.site";
const base = process.env.ATLAS_REALTIME_URL || origin;

async function polling(headers) {
    // Native HTTP preserves Host and browser metadata; Node XHR/fetch drop some.
    const url = `${base}/socket.io/?EIO=4&transport=polling`;
    const request = (target, options = {}) => new Promise((resolveResponse, reject) => {
        const send = target.startsWith("https:") ? httpsRequest : httpRequest;
        const req = send(target, { headers, method: options.method || "GET" }, response => {
            let body = "";
            response.setEncoding("utf8");
            response.on("data", chunk => { body += chunk; });
            response.on("end", () => resolveResponse({ status: response.statusCode, body }));
            response.on("error", reject);
        });
        req.setTimeout(15000, () => req.destroy(new Error("Polling timeout")));
        req.on("error", reject);
        req.end(options.body);
    });
    const open = await request(url);
    assert.equal(open.status, 200);
    const engine = JSON.parse(open.body.slice(1));
    const sessionUrl = `${url}&sid=${encodeURIComponent(engine.sid)}`;
    try {
        const post = await request(sessionUrl, { method: "POST", body: `40/${site},` });
        assert.equal(post.status, 200);
        const response = await request(sessionUrl);
        const packets = response.body.split("\x1e");
        if (packets.some(packet => packet.startsWith(`40/${site},`))) return "connected";
        const error = packets.find(packet => packet.startsWith(`44/${site},`));
        assert.ok(error, "No namespace result in polling response");
        return JSON.parse(error.slice(`44/${site},`.length)).message;
    } finally {
        await request(sessionUrl, { method: "POST", body: "1" });
    }
}

async function check(label, transport, extraHeaders, allowed) {
    const headers = { Host: new URL(origin).host, Cookie: cookie, ...extraHeaders };
    const outcome = transport === "polling" ? await polling(headers) : await new Promise((resolveResult, reject) => {
        const socket = io(`${base}/${site}`, {
            transports: [transport], reconnection: false, timeout: 15000,
            extraHeaders: headers,
        });
        const timer = setTimeout(() => { socket.close(); reject(new Error(`${label}: timeout`)); }, 18000);
        const finish = result => { clearTimeout(timer); socket.close(); resolveResult(result); };
        socket.once("connect", () => finish("connected"));
        socket.once("connect_error", error => finish(error.message));
    });
    assert.equal(outcome, allowed ? "connected" : "Invalid origin", label);
    console.log(`PASS: ${label}`);
}

await check("authenticated WebSocket", "websocket", { Origin: origin }, true);
await check("browser same-origin polling", "polling", { "Sec-Fetch-Site": "same-origin" }, true);
await check("foreign origin rejected", "websocket", { Origin: "https://foreign.example.invalid", "Sec-Fetch-Site": "same-origin" }, false);
await check("missing cross-site origin rejected", "polling", { "Sec-Fetch-Site": "cross-site" }, false);
