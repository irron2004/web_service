import { BookOpen, Lock, User } from 'lucide-react';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const success = await login(username, password);
      if (success) {
        // 사용자 역할에 따라 다른 페이지로 이동
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        switch (user.role) {
          case 'student':
            navigate('/student');
            break;
          case 'parent':
            navigate('/parent');
            break;
          case 'teacher':
            navigate('/teacher');
            break;
          default:
            navigate('/student');
        }
      } else {
        setError('로그인에 실패했습니다. 사용자명과 비밀번호를 확인해주세요.');
      }
    } catch (err) {
      setError('로그인 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <BookOpen className="logo-icon" />
          <h1>수학 놀이터</h1>
          <p>재미있는 수학 학습을 시작해보세요!</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <div className="input-wrapper">
              <User className="input-icon" />
              <input
                type="text"
                placeholder="사용자명"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="login-input"
              />
            </div>
          </div>

          <div className="input-group">
            <div className="input-wrapper">
              <Lock className="input-icon" />
              <input
                type="password"
                placeholder="비밀번호"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="login-input"
              />
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            disabled={loading}
            className="login-button"
          >
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <div className="demo-accounts">
          <h3>데모 계정</h3>
          <div className="demo-account">
            <strong>학생:</strong> student1 / password
          </div>
          <div className="demo-account">
            <strong>부모:</strong> parent1 / password
          </div>
          <div className="demo-account">
            <strong>선생님:</strong> teacher1 / password
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login; 