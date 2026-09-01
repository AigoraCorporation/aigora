package com.aigora.tutororchestrator.domain.valueobjects;
public record SessionVersion(long value) implements Comparable<SessionVersion> {
    public static final SessionVersion NEW = new SessionVersion(0);
    public SessionVersion { if (value < 0) throw new IllegalArgumentException("SessionVersion must not be negative"); }
    public SessionVersion next() { if (value == Long.MAX_VALUE) throw new ArithmeticException("SessionVersion overflow"); return new SessionVersion(value + 1); }
    @Override public int compareTo(SessionVersion other) { return Long.compare(value, other.value); }
}
