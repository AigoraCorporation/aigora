package com.aigora.tutororchestrator.testsupport.fixture;

import com.aigora.tutororchestrator.domain.model.StudentLearningState;

public final class StudentLearningStates {

    public static final StudentLearningState DEFAULT =
            new StudentLearningState(
                    Students.STUDENT_001,
                    Nodes.CURRENT_NODE,
                    GraphVersions.DEFAULT
            );

    private StudentLearningStates() {
    }
}