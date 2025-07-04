export interface User {
  id: string;
  username: string;
  role: 'student' | 'parent' | 'teacher';
  name: string;
  grade?: number;
  parentId?: string;
  children?: string[];
}

export interface MathProblem {
  id: string;
  question: string;
  answer: number;
  options?: number[];
  difficulty: 'easy' | 'medium' | 'hard';
  type: 'addition' | 'subtraction' | 'multiplication' | 'division';
  grade: number;
}

export interface GameSession {
  id: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  problems: MathProblem[];
  answers: { problemId: string; answer: number; correct: boolean; timeSpent: number }[];
  score: number;
  totalProblems: number;
  correctAnswers: number;
}

export interface StudentProgress {
  userId: string;
  totalSessions: number;
  totalProblems: number;
  correctAnswers: number;
  averageScore: number;
  timeSpent: number;
  lastPlayed: Date;
  grade: number;
}

export interface ParentNotification {
  id: string;
  parentId: string;
  childId: string;
  type: 'session_complete' | 'achievement' | 'reminder';
  message: string;
  timestamp: Date;
  read: boolean;
}

export interface TeacherReport {
  studentId: string;
  studentName: string;
  grade: number;
  progress: StudentProgress;
  recentSessions: GameSession[];
} 