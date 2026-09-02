package com.aigora.tutororchestrator.testsupport.fixture;

import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;

public final class StudentLearningStates {

    public static final StudentLearningState DEFAULT =
            new StudentLearningState(
                    Students.STUDENT_001,
                    Nodes.CURRENT_NODE,
                    GraphVersions.DEFAULT,
                    new StudentModelVersion("student-model-v1"),
                    true,
                    false
            );

    private StudentLearningStates() {
    }
}