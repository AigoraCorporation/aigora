package com.aigora.tutororchestrator.application.ports;

import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public interface StudentModelClient {

    StudentLearningState getLearningState(StudentId studentId);

    boolean hasCompletedCurrentNode(StudentId studentId);

    boolean isRegressionRecommended(StudentId studentId);
}