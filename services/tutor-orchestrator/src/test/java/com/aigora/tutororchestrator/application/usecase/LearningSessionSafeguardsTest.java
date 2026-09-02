package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.contracts.command.*;
import com.aigora.tutororchestrator.application.error.SessionErrorCode;
import com.aigora.tutororchestrator.application.context.*;
import com.aigora.tutororchestrator.application.ports.*;
import com.aigora.tutororchestrator.application.usecase.*;
import com.aigora.tutororchestrator.domain.model.*;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import com.aigora.tutororchestrator.infrastructure.*;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.*;

class LearningSessionSafeguardsTest {

    private final Clock clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);

    @Test
    void shouldDeduplicateStartCommand() {
        var repo = new InMemoryLearningSessionRepository();
        var events = new InMemorySessionEventPublisher();
        var telemetry = new InMemoryLifecycleTelemetrySink();
        var useCase = new StartLearningSessionUseCase(repo, events, telemetry, clock);
        var command = startCommand();

        var first = useCase.execute(command);
        var second = useCase.execute(command);

        assertTrue(first.isSuccess());
        assertTrue(second.isSuccess());
        assertEquals(first.value().version(), second.value().version());
        assertEquals(1, events.publishedEvents().size());
    }

    @Test
    void shouldRejectStaleExerciseCompletionVersion() {
        var fixture = activeFixture();
        var result = fixture.complete.execute(new CompleteExerciseCommand(
                new LearningSessionId("s1"),
                new SessionVersion(0),
                new ExerciseAttemptId("a1"),
                new ExerciseId("e1"),
                new CommandId("complete"),
                new CorrelationId("c"),
                new CausationId("start")
        ));

        assertFalse(result.isSuccess());
        assertEquals(SessionErrorCode.VERSION_CONFLICT, result.error().code());
    }

    @Test
    void shouldRejectStaleAssessment() {
        var fixture = awaitingAssessmentFixture();
        SessionAssessmentClient assessment = id -> new SessionAssessmentSnapshot(
                id,
                new ExerciseAttemptId("other-attempt"),
                new NodeId("n1"),
                false,
                true
        );
        TutorOrchestratorClient tutor = request -> { throw new AssertionError("Tutor must not be called"); };
        var process = new ProcessLearningProgressUseCase(
                fixture.repo,
                fixture.events,
                assessment,
                tutor,
                new InMemorySessionDecisionTraceSink(),
                fixture.telemetry,
                clock
        );

        var result = process.execute(progressCommand(fixture.session.version()));

        assertFalse(result.isSuccess());
        assertEquals(SessionErrorCode.STALE_ASSESSMENT, result.error().code());
    }

    @Test
    void shouldReturnExplicitNoCandidateFailure() {
        var fixture = awaitingAssessmentFixture();
        SessionAssessmentClient assessment = id -> new SessionAssessmentSnapshot(id, new ExerciseAttemptId("a1"), new NodeId("n1"), false, true);
        TutorOrchestratorClient tutor = request -> new SessionOrchestrationDecision(
                new DecisionId("d1"),
                request.sessionId(),
                request.sessionVersion(),
                request.assessmentResultId(),
                OrchestrationOutcome.NO_CANDIDATE,
                null
        );
        var trace = new InMemorySessionDecisionTraceSink();
        var process = new ProcessLearningProgressUseCase(fixture.repo, fixture.events, assessment, tutor, trace, fixture.telemetry, clock);

        var result = process.execute(progressCommand(fixture.session.version()));

        assertFalse(result.isSuccess());
        assertEquals(SessionErrorCode.NO_ELIGIBLE_CANDIDATE, result.error().code());
        assertEquals(1, trace.recordedDecisions().size());
        assertEquals(LearningSessionStatus.PROCESSING_DECISION, fixture.repo.findById(new LearningSessionId("s1")).orElseThrow().status());
    }

    @Test
    void shouldDeduplicateCompletedProgressCommandAfterLostResponse() {
        var fixture = awaitingAssessmentFixture();
        SessionAssessmentClient assessment = id -> new SessionAssessmentSnapshot(id, new ExerciseAttemptId("a1"), new NodeId("n1"), true, false);
        TutorOrchestratorClient tutor = request -> new SessionOrchestrationDecision(
                new DecisionId("d1"), request.sessionId(), request.sessionVersion(), request.assessmentResultId(), OrchestrationOutcome.NEXT_NODE, new NodeId("n2")
        );
        var trace = new InMemorySessionDecisionTraceSink();
        var process = new ProcessLearningProgressUseCase(fixture.repo, fixture.events, assessment, tutor, trace, fixture.telemetry, clock);
        var command = progressCommand(fixture.session.version());

        var first = process.execute(command);
        var second = process.execute(command);

        assertTrue(first.isSuccess());
        assertTrue(second.isSuccess());
        assertEquals(first.value().version(), second.value().version());
        assertEquals(1, trace.recordedDecisions().size());
    }

    private Fixture activeFixture() {
        var repo = new InMemoryLearningSessionRepository();
        var events = new InMemorySessionEventPublisher();
        var telemetry = new InMemoryLifecycleTelemetrySink();
        var start = new StartLearningSessionUseCase(repo, events, telemetry, clock);
        var started = start.execute(startCommand()).value();
        return new Fixture(repo, events, telemetry, new CompleteExerciseUseCase(repo, events, telemetry, clock), started);
    }

    private Fixture awaitingAssessmentFixture() {
        var fixture = activeFixture();
        var completed = fixture.complete.execute(new CompleteExerciseCommand(
                new LearningSessionId("s1"), fixture.session.version(), new ExerciseAttemptId("a1"), new ExerciseId("e1"), new CommandId("complete"), new CorrelationId("c"), new CausationId("start")
        )).value();
        return new Fixture(fixture.repo, fixture.events, fixture.telemetry, fixture.complete, completed);
    }

    private StartLearningSessionCommand startCommand() {
        return new StartLearningSessionCommand(
                new LearningSessionId("s1"), new StudentId("u1"), new NodeId("n1"), new ExerciseId("e1"), new CommandId("start"), new CorrelationId("c"), new CausationId("root")
        );
    }

    private ProcessLearningProgressCommand progressCommand(SessionVersion version) {
        return new ProcessLearningProgressCommand(
                new LearningSessionId("s1"), version, new AssessmentResultId("r1"), new OrchestrationRequestId("req1"), new GraphVersion("g1"), new StudentModelVersion("sm1"), new PolicySetVersion("p1"), new CommandId("progress"), new CorrelationId("c"), new CausationId("complete")
        );
    }

    private record Fixture(
            InMemoryLearningSessionRepository repo,
            InMemorySessionEventPublisher events,
            InMemoryLifecycleTelemetrySink telemetry,
            CompleteExerciseUseCase complete,
            LearningSession session
    ) {}
}
