package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.contracts.command.*;
import com.aigora.tutororchestrator.application.context.SessionAssessmentSnapshot;
import com.aigora.tutororchestrator.application.ports.SessionAssessmentClient;
import com.aigora.tutororchestrator.application.usecase.*;
import com.aigora.tutororchestrator.domain.model.LearningSessionStatus;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import com.aigora.tutororchestrator.infrastructure.*;
import com.aigora.tutororchestrator.adapters.outbound.TutorOrchestratorAdapter;
import com.aigora.tutororchestrator.application.configuration.DefaultTutorOrchestratorFactory;
import com.aigora.tutororchestrator.application.ports.CurriculumGraphClient;
import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.testsupport.fake.decisiontrace.FakeDecisionTraceSink;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class RealTutorOrchestratorIntegrationTest {

    @Test
    void shouldCompleteCrossBoundedContextFlowUsingRealTutorOrchestratorPipeline() {
        var graphVersion = new com.aigora.tutororchestrator.domain.valueobjects.GraphVersion("g1");
        var studentVersion = new com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion("sm1");

        CurriculumGraphClient graphClient = new CurriculumGraphClient() {
            public com.aigora.tutororchestrator.domain.valueobjects.NodeId getCurrentLearningNode(com.aigora.tutororchestrator.domain.valueobjects.StudentId studentId, com.aigora.tutororchestrator.domain.valueobjects.GraphVersion version) { return new com.aigora.tutororchestrator.domain.valueobjects.NodeId("n1"); }
            public List<com.aigora.tutororchestrator.domain.valueobjects.NodeId> getPrerequisites(com.aigora.tutororchestrator.domain.valueobjects.NodeId nodeId, com.aigora.tutororchestrator.domain.valueobjects.GraphVersion version) { return List.of(); }
            public List<LearningCandidate> getNextCandidateLearningNodes(com.aigora.tutororchestrator.domain.valueobjects.NodeId currentNodeId, com.aigora.tutororchestrator.domain.valueobjects.StudentId studentId, com.aigora.tutororchestrator.domain.valueobjects.GraphVersion version) { return List.of(new LearningCandidate(new com.aigora.tutororchestrator.domain.valueobjects.NodeId("n2"), CandidateClassification.NEXT_LEARNING)); }
            public List<com.aigora.tutororchestrator.domain.valueobjects.NodeId> getUnlockedNodes(com.aigora.tutororchestrator.domain.valueobjects.StudentId studentId, com.aigora.tutororchestrator.domain.valueobjects.GraphVersion version) { return List.of(new com.aigora.tutororchestrator.domain.valueobjects.NodeId("n2")); }
            public boolean nodeExists(com.aigora.tutororchestrator.domain.valueobjects.NodeId nodeId, com.aigora.tutororchestrator.domain.valueobjects.GraphVersion version) { return true; }
        };

        var studentClient = (com.aigora.tutororchestrator.application.ports.StudentModelClient) studentId ->
                new StudentLearningState(studentId, new com.aigora.tutororchestrator.domain.valueobjects.NodeId("n1"), graphVersion, studentVersion, true, false);

        var tutorAssessmentClient = (com.aigora.tutororchestrator.application.ports.AssessmentClient) resultId ->
                new com.aigora.tutororchestrator.domain.model.AssessmentSnapshot(
                        resultId,
                        new com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId("a1"),
                        new com.aigora.tutororchestrator.domain.valueobjects.NodeId("n1"),
                        true,
                        false,
                        BigDecimal.ONE,
                        BigDecimal.ONE
                );

        var tutorTrace = new FakeDecisionTraceSink();
        var clock = Clock.fixed(Instant.parse("2026-08-20T12:00:00Z"), ZoneOffset.UTC);
        var tutor = new DefaultTutorOrchestratorFactory(
                graphClient,
                studentClient,
                tutorAssessmentClient,
                tutorTrace,
                clock
        ).build();
        var tutorAdapter = new TutorOrchestratorAdapter(tutor.orchestrationPipeline());

        var repo = new InMemoryLearningSessionRepository();
        var events = new InMemorySessionEventPublisher();
        var sessionTrace = new InMemorySessionDecisionTraceSink();
        var telemetry = new InMemoryLifecycleTelemetrySink();
        SessionAssessmentClient sessionAssessment = id -> new SessionAssessmentSnapshot(id, new ExerciseAttemptId("a1"), new NodeId("n1"), true, false);

        var start = new StartLearningSessionUseCase(repo, events, telemetry, clock);
        var complete = new CompleteExerciseUseCase(repo, events, telemetry, clock);
        var process = new ProcessLearningProgressUseCase(repo, events, sessionAssessment, tutorAdapter, sessionTrace, telemetry, clock);

        var started = start.execute(new StartLearningSessionCommand(new LearningSessionId("s1"), new StudentId("u1"), new NodeId("n1"), new ExerciseId("e1"), new CommandId("start"), new CorrelationId("c1"), new CausationId("root")));
        var completedAttempt = complete.execute(new CompleteExerciseCommand(new LearningSessionId("s1"), started.value().version(), new ExerciseAttemptId("a1"), new ExerciseId("e1"), new CommandId("complete"), new CorrelationId("c1"), new CausationId("start")));
        var processed = process.execute(new ProcessLearningProgressCommand(new LearningSessionId("s1"), completedAttempt.value().version(), new AssessmentResultId("r1"), new OrchestrationRequestId("req1"), new GraphVersion("g1"), new StudentModelVersion("sm1"), new PolicySetVersion("p1"), new CommandId("progress"), new CorrelationId("c1"), new CausationId("complete")));

        assertTrue(processed.isSuccess());
        assertEquals(LearningSessionStatus.ACTIVE, processed.value().status());
        assertEquals(new NodeId("n2"), processed.value().currentNodeId());
        assertEquals(1, tutorTrace.recordedDecisions().size());
        assertEquals(1, sessionTrace.recordedDecisions().size());
    }
}
