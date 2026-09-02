package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.model.SessionDomainException;
import com.aigora.tutororchestrator.domain.model.*;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import com.aigora.tutororchestrator.shared.validation.Require;
import java.time.Instant;
import java.util.*;
public final class LearningSession {
    private final LearningSessionId id; private final StudentId studentId;
    private LearningSessionStatus status; private SessionVersion version; private NodeId currentNodeId; private ExerciseId currentExerciseId;
    private ExerciseAttempt currentAttempt; private SessionTerminalReason terminalReason; private Instant createdAt; private Instant lastTransitionAt; private Instant terminalAt;
    private final Set<CommandId> processedCommands; private final List<SessionEvent> pendingEvents;
    private LearningSession(LearningSessionId id, StudentId studentId, Instant createdAt) {
        this.id=Require.nonNull(id,"LearningSessionId"); this.studentId=Require.nonNull(studentId,"StudentId"); this.createdAt=Require.nonNull(createdAt,"createdAt"); this.lastTransitionAt=createdAt;
        this.status=LearningSessionStatus.CREATED; this.version=SessionVersion.NEW; this.processedCommands=new HashSet<>(); this.pendingEvents=new ArrayList<>();
    }
    public static LearningSession create(LearningSessionId id, StudentId studentId, Instant createdAt){ return new LearningSession(id,studentId,createdAt); }
    public void start(NodeId nodeId, ExerciseId exerciseId, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; requireStatus(LearningSessionStatus.CREATED); currentNodeId=Require.nonNull(nodeId,"NodeId"); currentExerciseId=Require.nonNull(exerciseId,"ExerciseId"); transition(LearningSessionStatus.ACTIVE,at); mark(commandId);
        pendingEvents.add(new LearningSessionStarted(eventId(),id,version,correlationId,causationId,at,currentNodeId,currentExerciseId));
    }
    public void completeExercise(ExerciseAttemptId attemptId, ExerciseId exerciseId, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; requireStatus(LearningSessionStatus.ACTIVE); Require.nonNull(exerciseId,"ExerciseId");
        if (currentExerciseId==null || !currentExerciseId.equals(exerciseId)) throw new SessionDomainException("Exercise does not match current session exercise");
        if (currentAttempt!=null) throw new SessionDomainException("An exercise attempt is already present");
        currentAttempt=new ExerciseAttempt(Require.nonNull(attemptId,"ExerciseAttemptId"),exerciseId,at); transition(LearningSessionStatus.AWAITING_ASSESSMENT,at); mark(commandId);
        pendingEvents.add(new ExerciseCompleted(eventId(),id,version,correlationId,causationId,at,attemptId,exerciseId));
    }
    public void acceptAssessment(ExerciseAttemptId attemptId, AssessmentResultId resultId, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; requireStatus(LearningSessionStatus.AWAITING_ASSESSMENT); requireAttempt(attemptId); currentAttempt.acceptAssessment(resultId); transition(LearningSessionStatus.PROCESSING_DECISION,at); mark(commandId);
        pendingEvents.add(new AssessmentAccepted(eventId(),id,version,correlationId,causationId,at,attemptId,resultId));
    }
    public void continueCurrentNode(DecisionId decisionId, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; requireStatus(LearningSessionStatus.PROCESSING_DECISION); currentExerciseId=null; currentAttempt=null; transition(LearningSessionStatus.ACTIVE,at); mark(commandId);
        pendingEvents.add(new LearningContinued(eventId(),id,version,correlationId,causationId,at,decisionId,currentNodeId));
    }
    public void applyNextNode(DecisionId decisionId, NodeId nextNodeId, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; requireStatus(LearningSessionStatus.PROCESSING_DECISION); currentNodeId=Require.nonNull(nextNodeId,"NodeId"); currentExerciseId=null; currentAttempt=null; transition(LearningSessionStatus.ACTIVE,at); mark(commandId);
        pendingEvents.add(new NextNodeApplied(eventId(),id,version,correlationId,causationId,at,decisionId,nextNodeId));
    }
    public void completeSession(DecisionId decisionId, SessionTerminalReason reason, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; requireStatus(LearningSessionStatus.PROCESSING_DECISION); terminalReason=Require.nonNull(reason,"SessionTerminalReason"); terminalAt=at; transition(LearningSessionStatus.COMPLETED,at); mark(commandId);
        pendingEvents.add(new LearningSessionCompleted(eventId(),id,version,correlationId,causationId,at,decisionId,reason.name()));
    }
    public void interrupt(SessionTerminalReason reason, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; ensureMutable(); terminalReason=Require.nonNull(reason,"SessionTerminalReason"); terminalAt=at; transition(LearningSessionStatus.INTERRUPTED,at); mark(commandId); pendingEvents.add(new LearningSessionInterrupted(eventId(),id,version,correlationId,causationId,at,reason.name()));
    }
    public void fail(SessionTerminalReason reason, CommandId commandId, CorrelationId correlationId, CausationId causationId, Instant at) {
        if (alreadyProcessed(commandId)) return; ensureMutable(); terminalReason=Require.nonNull(reason,"SessionTerminalReason"); terminalAt=at; transition(LearningSessionStatus.FAILED,at); mark(commandId); pendingEvents.add(new LearningSessionFailed(eventId(),id,version,correlationId,causationId,at,reason.name()));
    }
    private void requireAttempt(ExerciseAttemptId attemptId){ if(currentAttempt==null||!currentAttempt.id().equals(attemptId)) throw new SessionDomainException("Attempt does not match current session attempt"); }
    private void requireStatus(LearningSessionStatus expected){ if(status!=expected) throw new SessionDomainException("Invalid session transition from " + status + "; expected " + expected); }
    private void ensureMutable(){ if(status==LearningSessionStatus.COMPLETED||status==LearningSessionStatus.INTERRUPTED||status==LearningSessionStatus.FAILED) throw new SessionDomainException("Terminal session cannot be mutated"); }
    private void transition(LearningSessionStatus next, Instant at){ ensureMutable(); status=next; version=version.next(); lastTransitionAt=Require.nonNull(at,"occurredAt"); }
    private boolean alreadyProcessed(CommandId commandId){ Require.nonNull(commandId,"CommandId"); return processedCommands.contains(commandId); }
    private void mark(CommandId id){ processedCommands.add(id); }
    private EventId eventId(){ return new EventId(UUID.randomUUID().toString()); }
    public void recordProcessedCommand(CommandId commandId) {
        mark(Require.nonNull(commandId, "CommandId"));
    }
    public List<SessionEvent> drainEvents(){ var out=List.copyOf(pendingEvents); pendingEvents.clear(); return out; }
    public LearningSession copy(){
        LearningSession c=new LearningSession(id,studentId,createdAt); c.status=status;c.version=version;c.currentNodeId=currentNodeId;c.currentExerciseId=currentExerciseId;c.currentAttempt=currentAttempt==null?null:currentAttempt.copy();c.terminalReason=terminalReason;c.lastTransitionAt=lastTransitionAt;c.terminalAt=terminalAt;c.processedCommands.addAll(processedCommands); return c;
    }
    public LearningSessionId id(){return id;} public StudentId studentId(){return studentId;} public LearningSessionStatus status(){return status;} public SessionVersion version(){return version;} public NodeId currentNodeId(){return currentNodeId;} public ExerciseId currentExerciseId(){return currentExerciseId;} public ExerciseAttempt currentAttempt(){return currentAttempt==null?null:currentAttempt.copy();} public SessionTerminalReason terminalReason(){return terminalReason;} public Instant createdAt(){return createdAt;} public Instant lastTransitionAt(){return lastTransitionAt;} public Instant terminalAt(){return terminalAt;} public boolean hasProcessed(CommandId id){return processedCommands.contains(id);}
}
