import {
    BarChart3,
    Clock,
    LogOut,
    Play,
    Settings,
    Star,
    Target,
    Trophy
} from 'lucide-react';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './StudentDashboard.css';

const StudentDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalGames: 15,
    averageScore: 85,
    totalTime: 120,
    streak: 5
  });

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const startGame = () => {
    navigate('/game');
  };

  if (!user || user.role !== 'student') {
    return <div>접근 권한이 없습니다.</div>;
  }

  return (
    <div className="student-dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>안녕하세요, {user.name}님! 👋</h1>
          <p>{user.grade}학년 수학 학습을 시작해보세요</p>
        </div>
        <button onClick={handleLogout} className="logout-button">
          <LogOut size={20} />
        </button>
      </header>

      <div className="dashboard-content">
        {/* 통계 카드 */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <Trophy color="#FFD700" />
            </div>
            <div className="stat-info">
              <h3>{stats.totalGames}</h3>
              <p>총 게임 수</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Star color="#FF6B6B" />
            </div>
            <div className="stat-info">
              <h3>{stats.averageScore}%</h3>
              <p>평균 점수</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Clock color="#4ECDC4" />
            </div>
            <div className="stat-info">
              <h3>{stats.totalTime}분</h3>
              <p>총 학습 시간</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Target color="#45B7D1" />
            </div>
            <div className="stat-info">
              <h3>{stats.streak}일</h3>
              <p>연속 학습</p>
            </div>
          </div>
        </div>

        {/* 메인 액션 버튼 */}
        <div className="main-action">
          <button onClick={startGame} className="start-game-button">
            <Play size={30} />
            <span>수학 게임 시작하기</span>
          </button>
        </div>

        {/* 학습 옵션 */}
        <div className="learning-options">
          <h2>학습 옵션</h2>
          <div className="options-grid">
            <div className="option-card">
              <div className="option-icon">
                <BarChart3 size={24} />
              </div>
              <h3>진도 확인</h3>
              <p>나의 학습 진도를 확인해보세요</p>
            </div>

            <div className="option-card">
              <div className="option-icon">
                <Trophy size={24} />
              </div>
              <h3>성취도</h3>
              <p>획득한 배지와 성취를 확인하세요</p>
            </div>

            <div className="option-card">
              <div className="option-icon">
                <Settings size={24} />
              </div>
              <h3>설정</h3>
              <p>게임 설정을 변경하세요</p>
            </div>
          </div>
        </div>

        {/* 오늘의 목표 */}
        <div className="today-goal">
          <h2>오늘의 목표</h2>
          <div className="goal-card">
            <div className="goal-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: '60%' }}></div>
              </div>
              <span className="progress-text">3/5 문제 완료</span>
            </div>
            <p>오늘 5개의 수학 문제를 풀어보세요!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard; 