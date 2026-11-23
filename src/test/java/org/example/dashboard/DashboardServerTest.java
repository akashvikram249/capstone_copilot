package org.example.dashboard;

import org.junit.jupiter.api.Test;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DashboardServerTest {
    private final HttpClient client = HttpClient.newHttpClient();

    @Test
    void statsReturnsFreshAndLifecycleDrivenExactJson() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(40));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            HttpResponse<String> fresh = get(server, "/api/stats");
            assertEquals(200, fresh.statusCode());
            assertEquals("application/json; charset=utf-8",
                    fresh.headers().firstValue("Content-Type").orElse(""));
            assertEquals("no-store", fresh.headers().firstValue("Cache-Control").orElse(""));
            assertEquals("nosniff", fresh.headers().firstValue("X-Content-Type-Options").orElse(""));
            assertEquals("{\"totalRuns\":0,\"inProgress\":0,\"passed\":0,\"failed\":0}", fresh.body());

            URI base = URI.create("http://localhost:" + server.port());
            HttpResponse<String> passed = client.send(
                    HttpRequest.newBuilder(base.resolve("/api/runs"))
                            .header("Content-Type", "application/x-www-form-urlencoded")
                            .POST(HttpRequest.BodyPublishers.ofString("caseId=TC-1&title=Sign+in&outcome=pass"))
                            .build(),
                    HttpResponse.BodyHandlers.ofString());
            assertEquals(202, passed.statusCode());

            HttpResponse<String> inProgress = get(server, "/api/stats");
            assertEquals("{\"totalRuns\":1,\"inProgress\":1,\"passed\":0,\"failed\":0}",
                    inProgress.body());

            Thread.sleep(100);
            HttpResponse<String> complete = get(server, "/api/stats");
            assertEquals("{\"totalRuns\":1,\"inProgress\":0,\"passed\":1,\"failed\":0}",
                    complete.body());
        }
    }

    @Test
    void statsReturnsFailedCountAndRejectsEveryNonGetWithoutMutation() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ZERO);
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();
            URI base = URI.create("http://localhost:" + server.port());

            client.send(
                    HttpRequest.newBuilder(base.resolve("/api/runs"))
                            .header("Content-Type", "application/x-www-form-urlencoded")
                            .POST(HttpRequest.BodyPublishers.ofString("caseId=TC-2&title=Checkout&outcome=fail"))
                            .build(),
                    HttpResponse.BodyHandlers.ofString());
            Thread.sleep(30);

            assertEquals("{\"totalRuns\":1,\"inProgress\":0,\"passed\":0,\"failed\":1}",
                    get(server, "/api/stats").body());

            for (String method : new String[]{"POST", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"}) {
                HttpResponse<String> rejected = client.send(
                        HttpRequest.newBuilder(base.resolve("/api/stats"))
                                .method(method, method.equals("POST")
                                        ? HttpRequest.BodyPublishers.ofString("")
                                        : HttpRequest.BodyPublishers.noBody())
                                .build(),
                        HttpResponse.BodyHandlers.ofString());
                assertEquals(405, rejected.statusCode());
                assertEquals("GET", rejected.headers().firstValue("Allow").orElse(""));
                if (!method.equals("HEAD")) {
                    assertEquals("{\"error\":\"Use the GET method for this endpoint.\"}", rejected.body());
                }
                assertEquals("{\"totalRuns\":1,\"inProgress\":0,\"passed\":0,\"failed\":1}",
                        get(server, "/api/stats").body());
            }
        }
    }

    @Test
    void servesDashboardAndHealthEndpoint() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(20));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            HttpResponse<String> page = get(server, "/");
            HttpResponse<String> health = get(server, "/api/health");

            assertEquals(200, page.statusCode());
            assertTrue(page.body().contains("Caseflow"));
            assertTrue(page.headers().firstValue("Content-Security-Policy").orElse("").contains("default-src 'self'"));
            assertEquals(200, health.statusCode());
            assertEquals("{\"status\":\"ok\"}", health.body());
        }
    }

    @Test
    void startsAndPollsRunAndRejectsBadRequests() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(40));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();
            URI base = URI.create("http://localhost:" + server.port());

            HttpResponse<String> started = client.send(
                    HttpRequest.newBuilder(base.resolve("/api/runs"))
                            .header("Content-Type", "application/x-www-form-urlencoded")
                            .POST(HttpRequest.BodyPublishers.ofString("caseId=TC-9&title=Saved+case&outcome=fail"))
                            .build(),
                    HttpResponse.BodyHandlers.ofString());

            assertEquals(202, started.statusCode());
            assertTrue(started.body().contains("\"status\":\"In Progress\""));
            String id = started.body().split("\"id\":\"")[1].split("\"")[0];

            Thread.sleep(100);
            HttpResponse<String> completed = get(server, "/api/runs/" + id);
            assertEquals(200, completed.statusCode());
            assertTrue(completed.body().contains("\"status\":\"Failed\""));
            assertTrue(completed.body().contains("Simulated UI assertion failed"));

            HttpResponse<String> invalid = client.send(
                    HttpRequest.newBuilder(base.resolve("/api/runs"))
                            .header("Content-Type", "application/x-www-form-urlencoded")
                            .POST(HttpRequest.BodyPublishers.ofString("caseId=TC-9&title=Saved+case&outcome=other"))
                            .build(),
                    HttpResponse.BodyHandlers.ofString());
            assertEquals(400, invalid.statusCode());
            assertTrue(invalid.body().contains("\"error\""));

            HttpResponse<String> missing = get(server, "/api/runs/missing");
            assertEquals(404, missing.statusCode());
            assertFalse(missing.body().isBlank());
        }
    }

    @Test
    void returnsNotFoundForUnknownStaticPath() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ZERO);
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();
            HttpResponse<String> response = get(server, "/not-a-page");

            assertEquals(404, response.statusCode());
            assertTrue(response.body().contains("Not found"));
        }
    }

    private HttpResponse<String> get(DashboardServer server, String path) throws Exception {
        HttpRequest request = HttpRequest.newBuilder(
                URI.create("http://localhost:" + server.port() + path)).GET().build();
        return client.send(request, HttpResponse.BodyHandlers.ofString());
    }
}
