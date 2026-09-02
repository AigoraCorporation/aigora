package com.aigora.tutororchestrator.testsupport.fake.assessment;

import com.aigora.tutororchestrator.domain.model.AssessmentSnapshot;
import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class FakeAssessmentClientTest {

    @Test
    void shouldReturnConfiguredAssessmentSnapshot() {
        AssessmentSnapshot snapshot = new AssessmentSnapshot(
                new AssessmentResultId("assessment-001"),
                new ExerciseAttemptId("attempt-001"),
                new NodeId("node-001"),
                true,
                false,
                BigDecimal.ONE,
                BigDecimal.ONE
        );

        var client = new FakeAssessmentClient(snapshot);

        AssessmentSnapshot result = client.getAssessment(
                new AssessmentResultId("assessment-001")
        );

        assertEquals(snapshot, result);
        assertTrue(result.mastered());
    }

    @Test
    void shouldRejectUnknownAssessmentResultId() {
        var client = new FakeAssessmentClient(true, false);

        assertThrows(
                IllegalStateException.class,
                () -> client.getAssessment(
                        new AssessmentResultId("assessment-unknown")
                )
        );
    }
}
