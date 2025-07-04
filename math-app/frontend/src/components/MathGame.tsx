import {
    ArrowLeft,
    Check,
    Clock,
    Star,
    Target,
    X
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { MathProblem } from '../types';
import './MathGame.css';

const MathGame: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [currentProblem, setCurrentProblem] = useState<MathProblem | null>(null);
  const [userAnswer, setUserAnswer] = useState<string>('');
  const [score, setScore] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [totalQuestions] = useState(10);
  const [timeLeft, setTimeLeft] = useState(30);
  const [gameState, setGameState] = useState<'playing' | 'correct' | 'incorrect' | 'finished'>('playing');
  const [streak, setStreak] = useState(0);
  const [problems, setProblems] = useState<MathProblem[]>([]);

  // 문제 생성 함수
  const generateProblem = (): MathProblem => {
    const grade = user?.grade || 1;
    const operations = grade === 1 ? ['addition', 'subtraction'] : ['addition', 'subtraction', 'multiplication'];
    const operation = operations[Math.floor(Math.random() * operations.length)];
    
    let num1, num2, answer;
    
    switch (operation) {
      case 'addition':
        num1 = Math.floor(Math.random() * 20) + 1;
        num2 = Math.floor(Math.random() * 20) + 1;
        answer = num1 + num2;
        break;
      case 'subtraction':
        num1 = Math.floor(Math.random() * 20) + 10;
        num2 = Math.floor(Math.random() * num1) + 1;
        answer = num1 - num2;
        break;
      case 'multiplication':
        num1 = Math.floor(Math.random() * 10) + 1;
        num2 = Math.floor(Math.random() * 10) + 1;
        answer = num1 * num2;
        break;
      default:
        num1 = 5;
        num2 = 3;
        answer = 8;
    }

    const question = `${num1} ${operation === 'addition' ? '+' : operation === 'subtraction' ? '-' : '×'} ${num2} = ?`;

    return {
      id: Date.now().toString(),
      question,
      answer,
      difficulty: 'easy',
      type: operation as any,
      grade
    };
  };

  // 게임 초기화
  useEffect(() => {
    const newProblems = Array.from({ length: totalQuestions }, () => generateProblem());
    setProblems(newProblems);
    setCurrentProblem(newProblems[0]);
  }, []);

  // 타이머
  useEffect(() => {
    if (gameState === 'playing' && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      handleAnswer('timeout');
    }
  }, [timeLeft, gameState]);

  // 답변 처리
  const handleAnswer = (answer: string | 'timeout') => {
    if (!currentProblem) return;

    const isCorrect = answer === 'timeout' ? false : parseInt(answer) === currentProblem.answer;
    
    if (isCorrect) {
      setScore(score + 10 + Math.floor(timeLeft / 3));
      setStreak(streak + 1);
      setGameState('correct');
    } else {
      setStreak(0);
      setGameState('incorrect');
    }

    setTimeout(() => {
      if (currentQuestion < totalQuestions) {
        setCurrentQuestion(currentQuestion + 1);
        setCurrentProblem(problems[currentQuestion]);
        setUserAnswer('');
        setTimeLeft(30);
        setGameState('playing');
      } else {
        setGameState('finished');
      }
    }, 1500);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userAnswer.trim()) {
      handleAnswer(userAnswer);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (userAnswer.trim()) {
        handleAnswer(userAnswer);
      }
    }
  };

  const goBack = () => {
    navigate('/student');
  };

  const restartGame = () => {
    const newProblems = Array.from({ length: totalQuestions }, () => generateProblem());
    setProblems(newProblems);
    setCurrentProblem(newProblems[0]);
    setScore(0);
    setCurrentQuestion(1);
    setTimeLeft(30);
    setStreak(0);
    setUserAnswer('');
    setGameState('playing');
  };

  if (!user) {
    return <div>로그인이 필요합니다.</div>;
  }

  return (
    <div className="math-game">
      <header className="game-header">
        <button onClick={goBack} className="back-button">
          <ArrowLeft size={24} />
        </button>
        <div className="game-info">
          <div className="info-item">
            <Target size={20} />
            <span>문제 {currentQuestion}/{totalQuestions}</span>
          </div>
          <div className="info-item">
            <Star size={20} />
            <span>점수: {score}</span>
          </div>
          <div className="info-item">
            <Clock size={20} />
            <span>{timeLeft}초</span>
          </div>
        </div>
      </header>

      <div className="game-content">
        {gameState === 'playing' && currentProblem && (
          <div className="problem-container">
            <div className="problem-display">
              <h2>{currentProblem.question}</h2>
            </div>
            
            <form onSubmit={handleSubmit} className="answer-form">
              <input
                type="number"
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="답을 입력하세요"
                className="answer-input"
                autoFocus
              />
              <button type="submit" className="submit-button">
                확인
              </button>
            </form>

            {streak > 0 && (
              <div className="streak-indicator">
                🔥 {streak}연속 정답!
              </div>
            )}
          </div>
        )}

        {gameState === 'correct' && (
          <div className="feedback correct">
            <Check size={60} />
            <h2>정답입니다! 🎉</h2>
            <p>+{10 + Math.floor(timeLeft / 3)}점 획득!</p>
          </div>
        )}

        {gameState === 'incorrect' && currentProblem && (
          <div className="feedback incorrect">
            <X size={60} />
            <h2>틀렸습니다 😢</h2>
            <p>정답: {currentProblem.answer}</p>
          </div>
        )}

        {gameState === 'finished' && (
          <div className="game-result">
            <h2>게임 완료! 🎊</h2>
            <div className="final-score">
              <h3>최종 점수: {score}점</h3>
              <p>정답률: {Math.round((score / (totalQuestions * 10)) * 100)}%</p>
            </div>
            <div className="result-actions">
              <button onClick={restartGame} className="restart-button">
                다시 하기
              </button>
              <button onClick={goBack} className="back-to-dashboard">
                대시보드로
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MathGame; 