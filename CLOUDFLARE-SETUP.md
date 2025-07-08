# Cloudflare 설정 가이드

## 🚀 Cloudflare와 함께 사용하는 이유

### 1. **보안 강화**
- DDoS 공격 방어
- SSL/TLS 자동 처리
- 방화벽 규칙 설정

### 2. **성능 향상**
- 전 세계 CDN
- 정적 파일 캐싱
- 이미지 최적화

### 3. **관리 편의성**
- DNS 관리
- 트래픽 분석
- 실시간 모니터링

## 📋 설정 단계

### 1. Cloudflare 계정 설정

1. **Cloudflare 가입**: https://cloudflare.com
2. **도메인 추가**: 대시보드에서 "Add a Site" 클릭
3. **DNS 레코드 설정**:
   ```
   Type: A
   Name: @ (또는 도메인명)
   Content: [서버 IP 주소]
   Proxy status: Proxied (주황색 구름)
   ```

### 2. DNS 설정

#### 기본 A 레코드
```
Type: A
Name: @
Content: [서버 IP]
Proxy: Enabled (주황색)
TTL: Auto
```

#### 서브도메인 (선택사항)
```
Type: A
Name: www
Content: [서버 IP]
Proxy: Enabled
TTL: Auto
```

### 3. SSL/TLS 설정

1. **SSL/TLS 탭으로 이동**
2. **Encryption mode**: "Full (strict)" 선택
3. **Always Use HTTPS**: 활성화
4. **Minimum TLS Version**: TLS 1.2 이상

### 4. 페이지 규칙 설정 (선택사항)

#### HTTPS 리다이렉트
```
URL: http://yourdomain.com/*
Settings: Always Use HTTPS
```

#### 캐시 설정
```
URL: yourdomain.com/static/*
Settings: Cache Level: Cache Everything
```

## 🔧 서버 측 설정

### 1. Nginx 설정 업데이트

현재 설정된 `nginx/conf.d/default.conf`는 이미 Cloudflare와 호환되도록 구성되어 있습니다:

- **실제 IP 처리**: Cloudflare 프록시 IP 대신 실제 사용자 IP 사용
- **헤더 전달**: Cloudflare 특수 헤더들 전달
- **SSL 처리**: Cloudflare에서 SSL 종료

### 2. 환경 변수 설정

```bash
# .env 파일 생성
DOMAIN=yourdomain.com
CLOUDFLARE_ENABLED=true
```

### 3. 도메인 설정 업데이트

실제 도메인으로 nginx 설정 업데이트:

```nginx
# nginx/conf.d/default.conf
server {
    listen 80;
    server_name yourdomain.com;  # 실제 도메인으로 변경
    
    # Cloudflare 설정은 이미 포함됨
    # ...
}
```

## 🛡️ 보안 설정

### 1. Cloudflare 방화벽 규칙

#### 기본 보안 규칙
```
Rule: (http.request.method eq "POST") and (http.host eq "yourdomain.com")
Action: Challenge (Captcha)
```

#### 봇 차단
```
Rule: (http.user_agent contains "bot") and (http.host eq "yourdomain.com")
Action: Block
```

### 2. Rate Limiting

```
Rule: (http.request.method eq "POST") and (http.host eq "yourdomain.com")
Action: Rate Limit
Rate: 10 requests per 10 minutes
```

### 3. WAF (Web Application Firewall)

1. **Security 탭** → **WAF** 활성화
2. **Managed Rules** → **Cloudflare Managed Ruleset** 활성화
3. **OWASP Top 10** 규칙 활성화

## 📊 모니터링 및 분석

### 1. Analytics 설정

1. **Analytics 탭** → **Web Analytics** 활성화
2. **Real-time** 모니터링 활성화
3. **Logs** 설정 (선택사항)

### 2. 성능 모니터링

- **Speed** 탭에서 성능 분석
- **Caching** 설정 확인
- **Optimization** 설정

## 🔄 배포 프로세스

### 1. 개발 환경

```bash
# 로컬 테스트
docker-compose up --build

# 접속 테스트
curl -H "Host: yourdomain.com" http://localhost
```

### 2. 프로덕션 배포

```bash
# 서버에서 실행
docker-compose -f docker-compose.yml up -d

# 헬스 체크
curl https://yourdomain.com/health
```

### 3. DNS 전파 확인

```bash
# DNS 전파 확인
nslookup yourdomain.com
dig yourdomain.com

# Cloudflare 프록시 확인
curl -I https://yourdomain.com
```

## 🐛 문제 해결

### 1. SSL 오류

**증상**: SSL 연결 실패
**해결책**:
1. Cloudflare SSL/TLS 모드를 "Full" 또는 "Full (strict)"로 설정
2. 서버에서 SSL 인증서 확인
3. nginx SSL 설정 확인

### 2. 502 Bad Gateway

**증상**: 서비스 접속 불가
**해결책**:
1. Docker 컨테이너 상태 확인
2. nginx 로그 확인
3. 서비스 포트 확인

### 3. 캐시 문제

**증상**: 변경사항이 반영되지 않음
**해결책**:
1. Cloudflare 캐시 퍼지
2. 브라우저 캐시 삭제
3. Cache-Control 헤더 설정

## 📈 성능 최적화

### 1. 캐싱 전략

```nginx
# 정적 파일 캐싱
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Gzip 압축

```nginx
# nginx.conf에 이미 포함됨
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### 3. 이미지 최적화

1. **Cloudflare Images** 사용
2. **WebP** 포맷 사용
3. **Lazy Loading** 구현

## 🔒 보안 체크리스트

- [ ] SSL/TLS 설정 완료
- [ ] HTTPS 리다이렉트 활성화
- [ ] WAF 규칙 설정
- [ ] Rate Limiting 설정
- [ ] 봇 차단 규칙 설정
- [ ] 로그 모니터링 설정
- [ ] 백업 전략 수립

## 📞 지원

문제가 발생하면:

1. **Cloudflare 대시보드** → **Analytics** 확인
2. **nginx 로그** 확인: `docker-compose logs nginx`
3. **서비스 로그** 확인: `docker-compose logs [service-name]`
4. **헬스 체크**: `curl https://yourdomain.com/health` 