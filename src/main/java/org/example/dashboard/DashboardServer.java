package org.example.dashboard;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;

public final class DashboardServer implements AutoCloseable {
    private static final int MAX_REQUEST_BYTES = 4096;
    private static final Map<String, String> STATIC_FILES = Map.of(
            "/", "/static/index.html",
            "/index.html", "/static/index.html",
            "/styles.css", "/static/styles.css",
            "/app.js", "/static/app.js");

    private final HttpServer server;
    private final ExecutionService executionService;

    public DashboardServer(int port, ExecutionService executionService) throws IOException {
        this.executionService = executionService;
        this.server = HttpServer.create(new InetSocketAddress(port), 0);
        this.server.createContext("/", this::handle);
        this.server.setExecutor(Executors.newFixedThreadPool(8, task -> {
            Thread thread = new Thread(task, "dashboard-http");
            thread.setDaemon(true);
            return thread;
        }));
    }

    public void start() {
        server.start();
    }

    public int port() {
        return server.getAddress().getPort();
    }

    @Override
    public void close() {
        server.stop(0);
        executionService.close();
    }

    public static void main(String[] args) throws IOException {
        int port = args.length == 0 ? Integer.parseInt(System.getenv().getOrDefault("PORT", "8080"))
                : Integer.parseInt(args[0]);
        DashboardServer dashboard = new DashboardServer(port, new ExecutionService());
        dashboard.start();
        System.out.println("UI Test Case Dashboard running at http://localhost:" + dashboard.port());
        Runtime.getRuntime().addShutdownHook(new Thread(dashboard::close));
    }

    private void handle(HttpExchange exchange) throws IOException {
        try {
            String path = exchange.getRequestURI().getPath();
            if (path.equals("/api/health")) {
                if (!methodIs(exchange, "GET")) {
                    sendMethodNotAllowed(exchange, "GET");
                } else {
                    sendJson(exchange, 200, "{\"status\":\"ok\"}");
                }
                return;
            }

            if (path.equals("/api/runs")) {
                handleStartRun(exchange);
                return;
            }

            if (path.equals("/api/stats")) {
                handleStats(exchange);
                return;
            }

            if (path.startsWith("/api/runs/")) {
                handleGetRun(exchange, path.substring("/api/runs/".length()));
                return;
            }

            serveStatic(exchange, path);
        } catch (IllegalArgumentException error) {
            sendJson(exchange, 400, jsonError(error.getMessage()));
        } catch (IOException error) {
            System.err.println("Dashboard connection failed: " + error.getClass().getSimpleName());
        } catch (Exception error) {
            System.err.println("Dashboard request failed: " + error.getClass().getSimpleName());
            sendJson(exchange, 500, jsonError("The dashboard could not complete the request."));
        } finally {
            exchange.close();
        }
    }

    private void handleStartRun(HttpExchange exchange) throws IOException {
        if (!methodIs(exchange, "POST")) {
            sendMethodNotAllowed(exchange, "POST");
            return;
        }
        byte[] requestBody = exchange.getRequestBody().readNBytes(MAX_REQUEST_BYTES + 1);
        if (requestBody.length > MAX_REQUEST_BYTES) {
            sendJson(exchange, 413, jsonError("Request body must be 4096 bytes or fewer."));
            return;
        }

        Map<String, String> form = parseForm(new String(requestBody, StandardCharsets.UTF_8));
        ExecutionService.RunResult result = executionService.start(
                form.get("caseId"), form.get("title"), form.get("outcome"));
        sendJson(exchange, 202, jsonRun(result));
    }

    private void handleStats(HttpExchange exchange) throws IOException {
        if (!methodIs(exchange, "GET")) {
            sendMethodNotAllowed(exchange, "GET");
            return;
        }
        ExecutionService.StatsSnapshot stats = executionService.stats();
        sendJson(exchange, 200, jsonStats(stats));
    }

    private void handleGetRun(HttpExchange exchange, String id) throws IOException {
        if (!methodIs(exchange, "GET")) {
            sendMethodNotAllowed(exchange, "GET");
            return;
        }
        if (id.isBlank() || id.contains("/")) {
            sendJson(exchange, 404, jsonError("Execution report not found."));
            return;
        }
        ExecutionService.RunResult result = executionService.find(id);
        if (result == null) {
            sendJson(exchange, 404, jsonError("Execution report not found."));
            return;
        }
        sendJson(exchange, 200, jsonRun(result));
    }

    private void serveStatic(HttpExchange exchange, String path) throws IOException {
        if (!methodIs(exchange, "GET")) {
            sendMethodNotAllowed(exchange, "GET");
            return;
        }
        String resource = STATIC_FILES.get(path);
        if (resource == null) {
            sendText(exchange, 404, "Not found.", "text/plain; charset=utf-8");
            return;
        }
        try (var input = DashboardServer.class.getResourceAsStream(resource)) {
            if (input == null) {
                sendText(exchange, 500, "Dashboard assets are missing.", "text/plain; charset=utf-8");
                return;
            }
            String contentType = resource.endsWith(".css") ? "text/css; charset=utf-8"
                    : resource.endsWith(".js") ? "text/javascript; charset=utf-8"
                    : "text/html; charset=utf-8";
            send(exchange, 200, input.readAllBytes(), contentType);
        }
    }

    private static Map<String, String> parseForm(String body) {
        Map<String, String> values = new HashMap<>();
        if (body.isBlank()) {
            return values;
        }
        for (String part : body.split("&")) {
            String[] pair = part.split("=", 2);
            String key = URLDecoder.decode(pair[0], StandardCharsets.UTF_8);
            String value = pair.length == 2 ? URLDecoder.decode(pair[1], StandardCharsets.UTF_8) : "";
            values.put(key, value);
        }
        return values;
    }

    private static boolean methodIs(HttpExchange exchange, String expected) {
        return expected.equals(exchange.getRequestMethod());
    }

    private static void sendMethodNotAllowed(HttpExchange exchange, String expected) throws IOException {
        exchange.getResponseHeaders().set("Allow", expected);
        sendJson(exchange, 405, jsonError("Use the " + expected + " method for this endpoint."));
    }

    private static String jsonRun(ExecutionService.RunResult result) {
        return "{\"id\":" + quote(result.id())
                + ",\"caseId\":" + quote(result.caseId())
                + ",\"title\":" + quote(result.title())
                + ",\"status\":" + quote(result.status())
                + ",\"durationMs\":" + result.durationMs()
                + ",\"timestamp\":" + quote(result.timestamp())
                + ",\"failureDetails\":" + quote(result.failureDetails()) + "}";
    }

    private static String jsonStats(ExecutionService.StatsSnapshot stats) {
        return "{\"totalRuns\":" + stats.totalRuns()
                + ",\"inProgress\":" + stats.inProgress()
                + ",\"passed\":" + stats.passed()
                + ",\"failed\":" + stats.failed() + "}";
    }

    private static String jsonError(String message) {
        return "{\"error\":" + quote(message) + "}";
    }

    private static String quote(String value) {
        StringBuilder escaped = new StringBuilder("\"");
        for (char character : value.toCharArray()) {
            switch (character) {
                case '"' -> escaped.append("\\\"");
                case '\\' -> escaped.append("\\\\");
                case '\n' -> escaped.append("\\n");
                case '\r' -> escaped.append("\\r");
                case '\t' -> escaped.append("\\t");
                default -> {
                    if (character < 0x20) {
                        escaped.append(String.format("\\u%04x", (int) character));
                    } else {
                        escaped.append(character);
                    }
                }
            }
        }
        return escaped.append('"').toString();
    }

    private static void sendJson(HttpExchange exchange, int status, String body) throws IOException {
        exchange.getResponseHeaders().set("Cache-Control", "no-store");
        sendText(exchange, status, body, "application/json; charset=utf-8");
    }

    private static void sendText(HttpExchange exchange, int status, String body, String contentType)
            throws IOException {
        send(exchange, status, body.getBytes(StandardCharsets.UTF_8), contentType);
    }

    private static void send(HttpExchange exchange, int status, byte[] body, String contentType) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", contentType);
        exchange.getResponseHeaders().set("X-Content-Type-Options", "nosniff");
        exchange.getResponseHeaders().set(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; "
                        + "img-src 'self' data:; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");
        exchange.sendResponseHeaders(status, body.length);
        exchange.getResponseBody().write(body);
    }
}
