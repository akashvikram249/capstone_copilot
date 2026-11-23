package org.example.dashboard;

import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ExecutionServiceTest {
    @Test
    void freshStatsAndImmutableSnapshot() {
        try (ExecutionService service = new ExecutionService(Duration.ofMillis(70))) {
            ExecutionService.StatsSnapshot stats = service.stats();

            assertEquals(0, stats.totalRuns());
            assertEquals(0, stats.inProgress());
            assertEquals(0, stats.passed());
            assertEquals(0, stats.failed());
            assertEquals(0, service.stats().totalRuns());
        }
    }

    @Test
    void statsTrackPassedFailedAndInProgressWithInvariant() throws Exception {
        try (ExecutionService service = new ExecutionService(Duration.ofMillis(70))) {
            ExecutionService.RunResult passed = service.start("TC-1", "Sign in", "pass");
            ExecutionService.RunResult failed = service.start("TC-2", "Checkout", "fail");

            ExecutionService.StatsSnapshot inProgress = service.stats();
            assertEquals(2, inProgress.totalRuns());
            assertEquals(2, inProgress.inProgress());
            assertEquals(0, inProgress.passed());
            assertEquals(0, inProgress.failed());

            TimeUnit.MILLISECONDS.sleep(130);
            ExecutionService.StatsSnapshot completed = service.stats();
            assertEquals(2, completed.totalRuns());
            assertEquals(0, completed.inProgress());
            assertEquals(1, completed.passed());
            assertEquals(1, completed.failed());
            assertEquals(completed.totalRuns(),
                    completed.inProgress() + completed.passed() + completed.failed());
            assertEquals("Passed", service.find(passed.id()).status());
            assertEquals("Failed", service.find(failed.id()).status());
        }
    }

    @Test
    void duplicateCompletionDoesNotChangeStats() {
        try (ExecutionService service = new ExecutionService(Duration.ZERO)) {
            ExecutionService.RunResult started = service.start("TC-1", "Sign in", "pass");

            service.complete(started.id());
            service.complete(started.id());

            ExecutionService.StatsSnapshot stats = service.stats();
            assertEquals(1, stats.totalRuns());
            assertEquals(0, stats.inProgress());
            assertEquals(1, stats.passed());
            assertEquals(0, stats.failed());
        }
    }

    @Test
    void schedulingFailureRollsBackAdmissionCounters() {
        ExecutionService service = new ExecutionService(Duration.ZERO);
        service.close();

        assertThrows(java.util.concurrent.RejectedExecutionException.class,
                () -> service.start("TC-1", "Sign in", "pass"));
        ExecutionService.StatsSnapshot stats = service.stats();
        assertEquals(0, stats.totalRuns());
        assertEquals(0, stats.inProgress());
        assertEquals(0, stats.passed());
        assertEquals(0, stats.failed());
    }

    @Test
    void concurrentAdmissionsPreserveSnapshotInvariant() throws Exception {
        try (ExecutionService service = new ExecutionService(Duration.ofMillis(10))) {
            var executor = Executors.newFixedThreadPool(8);
            List<java.util.concurrent.Future<ExecutionService.RunResult>> starts = new ArrayList<>();
            for (int i = 0; i < 20; i++) {
                int index = i;
                starts.add(executor.submit(() -> service.start(
                        "TC-" + index, "Concurrent run " + index,
                        index % 2 == 0 ? "pass" : "fail")));
            }
            for (var start : starts) {
                start.get();
            }
            executor.shutdown();
            assertTrue(executor.awaitTermination(2, TimeUnit.SECONDS));
            TimeUnit.MILLISECONDS.sleep(40);

            ExecutionService.StatsSnapshot stats = service.stats();
            assertEquals(20, stats.totalRuns());
            assertEquals(0, stats.inProgress());
            assertEquals(10, stats.passed());
            assertEquals(10, stats.failed());
            assertEquals(stats.totalRuns(),
                    stats.inProgress() + stats.passed() + stats.failed());
        }
    }

    @Test
    void runTransitionsFromInProgressToPassed() throws Exception {
        try (ExecutionService service = new ExecutionService(Duration.ofMillis(70))) {
            ExecutionService.RunResult started = service.start("TC-1", "Sign in", "pass");

            assertEquals("In Progress", started.status());
            assertEquals("", started.failureDetails());

            TimeUnit.MILLISECONDS.sleep(130);
            ExecutionService.RunResult completed = service.find(started.id());

            assertNotNull(completed);
            assertEquals("Passed", completed.status());
            assertTrue(completed.durationMs() >= 0);
            assertNotNull(completed.timestamp());
            assertEquals("", completed.failureDetails());
        }
    }

    @Test
    void failedRunIncludesActionableFailureDetails() throws Exception {
        try (ExecutionService service = new ExecutionService(Duration.ZERO)) {
            ExecutionService.RunResult started = service.start("TC-2", "Checkout", "fail");
            TimeUnit.MILLISECONDS.sleep(30);

            ExecutionService.RunResult completed = service.find(started.id());

            assertEquals("Failed", completed.status());
            assertFalse(completed.failureDetails().isBlank());
        }
    }

    @Test
    void rejectsMissingFieldsUnsupportedOutcomesAndOversizedNames() {
        try (ExecutionService service = new ExecutionService(Duration.ZERO)) {
            assertThrows(IllegalArgumentException.class, () -> service.start("", "Sign in", "pass"));
            assertThrows(IllegalArgumentException.class, () -> service.start("TC-1", "Sign in", "maybe"));
            assertThrows(IllegalArgumentException.class,
                    () -> service.start("TC-1", "x".repeat(121), "pass"));
        }
    }

    @Test
    void unknownRunReturnsNull() {
        try (ExecutionService service = new ExecutionService(Duration.ZERO)) {
            assertNull(service.find("missing"));
        }
    }
}
