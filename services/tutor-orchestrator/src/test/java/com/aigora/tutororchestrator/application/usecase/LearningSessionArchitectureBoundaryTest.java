package com.aigora.tutororchestrator.application.usecase;

import org.junit.jupiter.api.Test;
import java.io.IOException;
import java.nio.file.*;
import static org.junit.jupiter.api.Assertions.*;

class LearningSessionArchitectureBoundaryTest {
    @Test
    void learningSessionDomainMustNotDependOnApplicationOrInfrastructure() throws IOException {
        Path domain = Path.of("src/main/java/com/aigora/tutororchestrator/domain");
        try (var files = Files.walk(domain)) {
            var violations = files.filter(p -> p.toString().endsWith(".java"))
                    .filter(p -> {
                        try {
                            String name = p.getFileName().toString();
                            if (!(name.startsWith("LearningSession") || name.startsWith("ExerciseAttempt") || name.startsWith("Session") || name.equals("ExerciseCompleted.java") || name.equals("AssessmentAccepted.java") || name.equals("NextNodeApplied.java") || name.equals("LearningContinued.java"))) return false;
                            String source = Files.readString(p);
                            return source.contains("com.aigora.tutororchestrator.application") || source.contains("com.aigora.tutororchestrator.infrastructure");
                        } catch (IOException e) { throw new RuntimeException(e); }
                    }).toList();
            assertTrue(violations.isEmpty(), "Learning Session domain dependency violations: " + violations);
        }
    }
}
