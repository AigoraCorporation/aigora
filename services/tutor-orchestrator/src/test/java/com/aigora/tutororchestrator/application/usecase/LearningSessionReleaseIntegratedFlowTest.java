package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.adapters.outbound.TutorOrchestratorAdapter;
import com.aigora.tutororchestrator.application.configuration.DefaultTutorOrchestratorFactory;
import com.aigora.tutororchestrator.application.context.SessionAssessmentSnapshot;
import com.aigora.tutororchestrator.application.contracts.command.CompleteExerciseCommand;
import com.aigora.tutororchestrator.application.contracts.command.ProcessLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.command.StartLearningSessionCommand;
import com.aigora.tutororchestrator.application.error.SessionErrorCode;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.CurriculumGraphClient;
import com.aigora.tutororchestrator.application.ports.SessionAssessmentClient;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.AssessmentAccepted;
import com.aigora.tutororchestrator.domain.model.AssessmentSnapshot;
import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.ExerciseCompleted;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.LearningSessionStarted;
import com.aigora.tutororchestrator.domain.model.LearningSessionStatus;
import com.aigora.tutororchestrator.domain.model.NextNodeApplied;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.CausationId;
import com.aigora.tutororchestrator.domain.valueobjects.CommandId;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.LearningSessionId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.OrchestrationRequestId;
import com.aigora.tutororchestrator.domain.valueobjects.PolicySetVersion;
import com.aigora.tutororchestrator.domain.valueobjects.SessionVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;
import com.aigora.tutororchestrator.infrastructure.InMemoryLearningSessionRepository;
import com.aigora.tutororchestrator.infrastructure.InMemoryLifecycleTelemetrySink;
import com.aigora.tutororchestrator.infrastructure.InMemorySessionDecisionTraceSink;
import com.aigora.tutororchestrator.infrastructure.InMemorySessionEventPublisher;
import com.aigora.tutororchestrator.testsupport.fake.decisiontrace.FakeDecisionTraceSink;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Release-level integration specification for v0.3.1.
 *
 * <p>This test intentionally composes the real Learning Session application
 * flow with the real deterministic Tutor Orchestrator pipeline. Only external
 * bounded-context dependencies are replaced by deterministic in-memory test
 * doubles.</p>
 *
 * <p>The scenario verifies lifecycle transitions, snapshot consistency,
 * deterministic orchestration, decision evidence, trace recording, event
 * ordering, persistence, telemetry, and command idempotency as one business
 * story.</p>
 */
class LearningSessionReleaseIntegratedFlowTest {

    private static final Instant FIXED_TIME =
            Instant.parse("2026-08-31T20:00:00Z");

    private static final Clock CLOCK =
            Clock.fixed(FIXED_TIME, ZoneOffset.UTC);

    private static final LearningSessionId SESSION_ID =
            new LearningSessionId("session-release-001");

    private static final StudentId STUDENT_ID =
            new StudentId("student-release-001");

    private static final NodeId CURRENT_NODE =
            new NodeId("node-001");

    private static final NodeId NEXT_NODE =
            new NodeId("node-002");

    private static final ExerciseId EXERCISE_ID =
            new ExerciseId("exercise-001");

    private static final ExerciseAttemptId ATTEMPT_ID =
            new ExerciseAttemptId("attempt-001");

    private static final AssessmentResultId ASSESSMENT_ID =
            new AssessmentResultId("assessment-001");

    private static final GraphVersion GRAPH_VERSION =
            new GraphVersion("graph-v1");

    private static final StudentModelVersion STUDENT_MODEL_VERSION =
            new StudentModelVersion("student-model-v1");

    private static final PolicySetVersion POLICY_SET_VERSION =
            new PolicySetVersion("policy-set-v1");

    private static final CorrelationId CORRELATION_ID =
            new CorrelationId("correlation-release-001");

    @Test
    void shouldExecuteAuditableDeterministicLearningSessionFromExerciseCompletionToNextNode() {
        TestEnvironment environment = TestEnvironment.validNextNodeScenario();

        var started = environment.startSession();

        assertTrue(started.isSuccess());
        assertEquals(LearningSessionStatus.ACTIVE, started.value().status());
        assertEquals(CURRENT_NODE, started.value().currentNodeId());
        assertEquals(EXERCISE_ID, started.value().currentExerciseId());
        assertEquals(new SessionVersion(1), started.value().version());

        var completed = environment.completeExercise(started.value().version());

        assertTrue(completed.isSuccess());
        assertEquals(
                LearningSessionStatus.AWAITING_ASSESSMENT,
                completed.value().status()
        );
        assertEquals(new SessionVersion(2), completed.value().version());
        assertNotNull(completed.value().currentAttempt());
        assertEquals(ATTEMPT_ID, completed.value().currentAttempt().id());

        var processed = environment.processProgress(completed.value().version());

        assertTrue(processed.isSuccess());
        assertEquals(LearningSessionStatus.ACTIVE, processed.value().status());
        assertEquals(NEXT_NODE, processed.value().currentNodeId());
        assertEquals(new SessionVersion(4), processed.value().version());
        assertEquals(null, processed.value().currentExerciseId());
        assertEquals(null, processed.value().currentAttempt());

        var persisted = environment.repository.findById(SESSION_ID).orElseThrow();

        assertEquals(processed.value().version(), persisted.version());
        assertEquals(processed.value().status(), persisted.status());
        assertEquals(processed.value().currentNodeId(), persisted.currentNodeId());

        assertEquals(1, environment.tutorDecisionTrace.recordedDecisionCount());

        var tutorDecision = environment.tutorDecisionTrace.lastRecordedDecision();
        var trace = tutorDecision.trace();

        assertEquals(STUDENT_ID, tutorDecision.studentId());
        assertEquals(NEXT_NODE, tutorDecision.selectedNodeId());
        assertEquals(new OrchestrationRequestId("orchestration-request-001"), trace.orchestrationRequestId());
        assertEquals(SESSION_ID, trace.learningSessionId());
        assertEquals(ATTEMPT_ID, trace.exerciseAttemptId());
        assertEquals(ASSESSMENT_ID, trace.assessmentResultId());
        assertEquals(STUDENT_MODEL_VERSION, trace.studentModelVersion());
        assertEquals(GRAPH_VERSION, trace.graphVersion());
        assertEquals(POLICY_SET_VERSION, trace.policySetVersion());
        assertEquals(CORRELATION_ID, trace.correlationId());
        assertEquals(new CausationId("complete-exercise"), trace.causationId());
        assertEquals(FIXED_TIME, trace.decidedAt());

        assertEquals(1, environment.sessionDecisionTrace.recordedDecisions().size());
        var sessionDecision = environment.sessionDecisionTrace.recordedDecisions().get(0);

        assertEquals(SESSION_ID, sessionDecision.sessionId());
        assertEquals(ASSESSMENT_ID, sessionDecision.assessmentResultId());
        assertEquals(NEXT_NODE, sessionDecision.nextNodeId());

        var events = environment.events.publishedEvents();

        assertEquals(4, events.size());
        assertInstanceOf(LearningSessionStarted.class, events.get(0));
        assertInstanceOf(ExerciseCompleted.class, events.get(1));
        assertInstanceOf(AssessmentAccepted.class, events.get(2));
        assertInstanceOf(NextNodeApplied.class, events.get(3));

        assertEquals(List.of(1L, 2L, 3L, 4L), events.stream()
                .map(event -> event.sessionVersion().value())
                .toList());

        assertTrue(events.stream()
                .allMatch(event -> event.correlationId().equals(CORRELATION_ID)));

        assertTrue(events.stream()
                .allMatch(event -> event.occurredAt().equals(FIXED_TIME)));

        assertEquals(3, environment.telemetry.entries().size());
        assertEquals(
                List.of("start", "complete-exercise", "process-progress"),
                environment.telemetry.entries().stream()
                        .map(InMemoryLifecycleTelemetrySink.Entry::operation)
                        .toList()
        );
        assertTrue(environment.telemetry.entries().stream()
                .allMatch(entry -> "success".equals(entry.outcome())));
    }

    @Test
    void shouldTreatReplayedProgressCommandAsIdempotentWithoutDuplicatingDecisionOrEvents() {
        TestEnvironment environment = TestEnvironment.validNextNodeScenario();

        var started = environment.startSession();
        var completed = environment.completeExercise(started.value().version());

        var first = environment.processProgress(completed.value().version());

        assertTrue(first.isSuccess());

        int eventCountAfterFirstExecution =
                environment.events.publishedEvents().size();

        int tutorTraceCountAfterFirstExecution =
                environment.tutorDecisionTrace.recordedDecisionCount();

        int sessionTraceCountAfterFirstExecution =
                environment.sessionDecisionTrace.recordedDecisions().size();

        var replay = environment.processProgress(completed.value().version());

        assertTrue(replay.isSuccess());
        assertEquals(first.value().version(), replay.value().version());
        assertEquals(first.value().status(), replay.value().status());
        assertEquals(first.value().currentNodeId(), replay.value().currentNodeId());

        assertEquals(
                eventCountAfterFirstExecution,
                environment.events.publishedEvents().size()
        );

        assertEquals(
                tutorTraceCountAfterFirstExecution,
                environment.tutorDecisionTrace.recordedDecisionCount()
        );

        assertEquals(
                sessionTraceCountAfterFirstExecution,
                environment.sessionDecisionTrace.recordedDecisions().size()
        );
    }

    @Test
    void shouldRejectStaleAssessmentBeforeCallingTutorOrchestrator() {
        TestEnvironment environment = TestEnvironment.staleAssessmentScenario();

        var started = environment.startSession();
        var completed = environment.completeExercise(started.value().version());

        var processed = environment.processProgress(completed.value().version());

        assertFalse(processed.isSuccess());
        assertEquals(SessionErrorCode.STALE_ASSESSMENT, processed.error().code());

        var persisted = environment.repository.findById(SESSION_ID).orElseThrow();

        assertEquals(LearningSessionStatus.AWAITING_ASSESSMENT, persisted.status());
        assertEquals(new SessionVersion(2), persisted.version());
        assertEquals(0, environment.tutorDecisionTrace.recordedDecisionCount());
        assertEquals(0, environment.sessionDecisionTrace.recordedDecisions().size());
        assertEquals(2, environment.events.publishedEvents().size());
    }

    private static final class TestEnvironment {

        private final InMemoryLearningSessionRepository repository =
                new InMemoryLearningSessionRepository();

        private final InMemorySessionEventPublisher events =
                new InMemorySessionEventPublisher();

        private final InMemorySessionDecisionTraceSink sessionDecisionTrace =
                new InMemorySessionDecisionTraceSink();

        private final InMemoryLifecycleTelemetrySink telemetry =
                new InMemoryLifecycleTelemetrySink();

        private final FakeDecisionTraceSink tutorDecisionTrace =
                new FakeDecisionTraceSink();

        private final SessionAssessmentClient sessionAssessmentClient;
        private final StartLearningSessionUseCase startUseCase;
        private final CompleteExerciseUseCase completeExerciseUseCase;
        private final ProcessLearningProgressUseCase processLearningProgressUseCase;

        private TestEnvironment(SessionAssessmentClient sessionAssessmentClient) {
            this.sessionAssessmentClient = sessionAssessmentClient;

            var tutorConfiguration = new DefaultTutorOrchestratorFactory(
                    curriculumGraphClient(),
                    studentModelClient(),
                    tutorAssessmentClient(),
                    tutorDecisionTrace,
                    CLOCK
            ).build();

            var tutorAdapter = new TutorOrchestratorAdapter(
                    tutorConfiguration.orchestrationPipeline()
            );

            this.startUseCase = new StartLearningSessionUseCase(
                    repository,
                    events,
                    telemetry,
                    CLOCK
            );

            this.completeExerciseUseCase = new CompleteExerciseUseCase(
                    repository,
                    events,
                    telemetry,
                    CLOCK
            );

            this.processLearningProgressUseCase = new ProcessLearningProgressUseCase(
                    repository,
                    events,
                    this.sessionAssessmentClient,
                    tutorAdapter,
                    sessionDecisionTrace,
                    telemetry,
                    CLOCK
            );
        }

        static TestEnvironment validNextNodeScenario() {
            return new TestEnvironment(assessmentId ->
                    new SessionAssessmentSnapshot(
                            assessmentId,
                            ATTEMPT_ID,
                            CURRENT_NODE,
                            true,
                            false
                    )
            );
        }

        static TestEnvironment staleAssessmentScenario() {
            return new TestEnvironment(assessmentId ->
                    new SessionAssessmentSnapshot(
                            assessmentId,
                            new ExerciseAttemptId("attempt-stale"),
                            CURRENT_NODE,
                            true,
                            false
                    )
            );
        }

        private com.aigora.tutororchestrator.application.contracts.result.SessionResult<com.aigora.tutororchestrator.domain.model.LearningSession> startSession() {
            return startUseCase.execute(
                    new StartLearningSessionCommand(
                            SESSION_ID,
                            STUDENT_ID,
                            CURRENT_NODE,
                            EXERCISE_ID,
                            new CommandId("start-session"),
                            CORRELATION_ID,
                            new CausationId("root")
                    )
            );
        }

        private com.aigora.tutororchestrator.application.contracts.result.SessionResult<com.aigora.tutororchestrator.domain.model.LearningSession> completeExercise(
                SessionVersion expectedVersion
        ) {
            return completeExerciseUseCase.execute(
                    new CompleteExerciseCommand(
                            SESSION_ID,
                            expectedVersion,
                            ATTEMPT_ID,
                            EXERCISE_ID,
                            new CommandId("complete-exercise"),
                            CORRELATION_ID,
                            new CausationId("start-session")
                    )
            );
        }

        private com.aigora.tutororchestrator.application.contracts.result.SessionResult<com.aigora.tutororchestrator.domain.model.LearningSession> processProgress(
                SessionVersion expectedVersion
        ) {
            return processLearningProgressUseCase.execute(
                    new ProcessLearningProgressCommand(
                            SESSION_ID,
                            expectedVersion,
                            ASSESSMENT_ID,
                            new OrchestrationRequestId("orchestration-request-001"),
                            GRAPH_VERSION,
                            STUDENT_MODEL_VERSION,
                            POLICY_SET_VERSION,
                            new CommandId("process-progress"),
                            CORRELATION_ID,
                            new CausationId("complete-exercise")
                    )
            );
        }

        private CurriculumGraphClient curriculumGraphClient() {
            return new CurriculumGraphClient() {
                @Override
                public NodeId getCurrentLearningNode(
                        StudentId studentId,
                        GraphVersion graphVersion
                ) {
                    return CURRENT_NODE;
                }

                @Override
                public List<NodeId> getPrerequisites(
                        NodeId nodeId,
                        GraphVersion graphVersion
                ) {
                    return List.of();
                }

                @Override
                public List<LearningCandidate> getNextCandidateLearningNodes(
                        NodeId currentNodeId,
                        StudentId studentId,
                        GraphVersion graphVersion
                ) {
                    return List.of(
                            new LearningCandidate(
                                    NEXT_NODE,
                                    CandidateClassification.NEXT_LEARNING
                            )
                    );
                }

                @Override
                public List<NodeId> getUnlockedNodes(
                        StudentId studentId,
                        GraphVersion graphVersion
                ) {
                    return List.of(NEXT_NODE);
                }

                @Override
                public boolean nodeExists(
                        NodeId nodeId,
                        GraphVersion graphVersion
                ) {
                    return true;
                }
            };
        }

        private StudentModelClient studentModelClient() {
            return studentId -> new StudentLearningState(
                    studentId,
                    CURRENT_NODE,
                    GRAPH_VERSION,
                    STUDENT_MODEL_VERSION,
                    true,
                    false
            );
        }

        private AssessmentClient tutorAssessmentClient() {
            return assessmentResultId -> new AssessmentSnapshot(
                    assessmentResultId,
                    ATTEMPT_ID,
                    CURRENT_NODE,
                    true,
                    false,
                    BigDecimal.ONE,
                    BigDecimal.ONE
            );
        }
    }
}
