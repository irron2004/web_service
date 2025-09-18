**���(3?5��)**
�� ���񽺴� **Self(����) vs Others(Ÿ���� ��)**�� ���� **���� ����(Perception Gap)**�� ��ġȭ���ð�ȭ�մϴ�. MVP�� ��**���� 24 + ���� �ν��� 8 = 32����**(Likert 1?5)������ �����ϰ�, **Self ����**�� **Other(����/ģ�� N��) ����**�� ���� **GapScore�����ǵ�(��)**�� �����մϴ�. ����� **���̴�/��ĳ��** ��Ʈ�� **������ OG �̹���**�� Ȯ���� ����, **RFC?9457 ���� ����**, **WCAG?2.2 AA**, **Web Vitals(LCP��2.5s/INP��200ms/CLS��0.1)** ������ �ؼ��մϴ�. **��ûID/OTel**�� �⺻������ �����մϴ�. ([RFC Editor][1])

```yaml
---
version: "1.0"
date: "2025-09-17"
product: "360Me ? Perception Gap (If I were you)"
domains: ["backend", "frontend", "growth"]
owner: "PM: ������"
source_of_truth: "PRD.md"
use_browsing: true
---
```

### 0) Assumptions(����)

* **Stack:** FastAPI + PostgreSQL + Redis(�鿣��), React + Vite + React Router + TanStack Query + Zustand(����Ʈ), Chart.js(���̴�/��ĳ��). ([chartjs.org][2])
* **ǥ��:** ���� ���� **RFC?9457**, ���ټ� **WCAG?2.2 AA**, ���� **Web Vitals**. ([RFC Editor][1])
* **�����̹���:** ���� ���� **k��3**(k-anonymity ��Ģ ����)�� ��� ����, ���� ������ ��ĺ� ó��. ([EPIC][3])
* **���� ����:** **MBTI/���̾-�긯��**�� ��ϻ�ǥ�̸� **���� ����/�ؼ� �һ��**(��MBTI-style�� �� ���). ([mbtionline.com][4])

### 1) ����/����/��������/Ÿ��

* **����:** *If I were you* ? ������ �ʶ�� �̷��� �� �ž�.�� Self vs Others �� **Perception Gap**�� ��հ� �����ϰ� �����ִ� **�������θ�Ʈ/�����λ���Ʈ**.
* **�ٽ� ��ġ:** �� **���� �ƶ�**(����/ģ��) �� **���� ��** ���ǵ�/����ġ �� **���� ����**�� ���̷�.
* **Ÿ��:** ����/ģ��/���л������� �ʳ�� �߽� 20?30��.

### 2) ����/�����

**In Scope:** ��� ����, ����(���� 24 + �ν��� 8), Self ä��, �ʴ�/���� ����(N��), ����/GapScore/���ǵ�, ��� �ð�ȭ(���̴�/��ĳ��), OG ���� �̹���, AdSense ���� ��ġ, RFC?9457 ����, OTel/Request-ID. ([RFC Editor][1])
**Out of Scope(�̹� �б�):** ����/������������ ����, ���� �÷�, ����� ��, ��� ��Ʈ�ʡ����� ����(����).

### 3) ����� �ó�����(���)

* **S-1(Ŀ��):** ���θ�� 32���� �� ��Ʈ�� 1:1 �ʴ� �� **Self vs Partner ���̴�/��ĳ��** �� ���� �̹���.
* **S-2(ģ�� N):** ģ����� ��ũ ����(�͸�/���) �� **Other ��ա���Gap** �� ������ ����/����ġ ������ ī��.
* **S-3(���̷�):** 3�� �̻� ���� �� **�߰� �λ���Ʈ ����** �� OG �̹����� SNS ���� 1Ŭ��.
* **S-4(���ټ�):** ���� �˸�, ��� PDF/��ũ ����, **noindex/X-Robots-Tag**�� �˻� ���� ����. ([Google for Developers][5])

### 4) ��� �䱸(Functional Requirements)

| ID      | ���              | ����                            | ������   | ���� | **���� ����(���)**                                                                  |
| ------- | ----------------- | ------------------------------- | ------ | --- | ----------------------------------------------------------------------------------- |
| R-101   | ��� ����         | [����/ģ��/�⺻]                | FE     | ���� | 10�� �� ù Ŭ������ ���Է� ��70%                                                     |
| R-102   | Self �׽�Ʈ       | ���� 24 + ��� 8(32)            | R-101  | ��Ż | ������ ��75%, 400/422�� **RFC?9457** ���� ����. ([RFC Editor][1])                     |
| R-103   | �ʴ� ��ũ         | ���ᡤ�ִ��ο����͸�/��������±� | Auth/DB| ���� | ��ũ ���� 201, ��ū ���� ����, 429 ����Ʈ����                                        |
| R-104   | Ÿ�� ���� ����    | ��ū ����/�ߺ����� ����         | R-103  | ��  | ���� 20�� P95<1s, �ߺ����� ����                                                        |
| R-105   | ����/GapScore   | �������, ��, Gap ���          | R-102/104 | ���� | ����(��4.1/4.2)��� ���, �����׽�Ʈ 100%                                               |
| R-106   | k-�͸� ���� �Ӱ�  | k<3 �����                     | R-105  | ������ | k<3 ��� ��Ʈ/���� ��Ȱ��ȭ. ([EPIC][3])                                             |
| R-107   | �ð�ȭ            | ���̴�(4��)/��ĳ��(2D)         | FE Charts | ���� | Chart.js ���̴�����ĳ�� ����, ����� 30fps. ([chartjs.org][2])                        |
| R-108   | ���� OG �̹���    | Self vs Other ��ࡤGap ����    | FE/BE  | ���� | 1200��630, 200ms �� ����, ��Ÿ�±� ��Ȯ. ([ogp.me][6])                                 |
| R-109   | �ǽð� ��ú���   | ���� ī��Ʈ/�̸�����           | FE/BE  | ���� | 3s ����(�Ǵ� SSE), ���ѷε� ����                                                      |
| R-110   | AdSense ���� ���� | ���/������/�ϴ� 2?3��         | FE     | ��å | ��ư/���� ���� ��ġ ����, ��å ���� 0��. ([Google Help][7])                          |
| R-111   | �м�/���̷� ����  | GA4 �̺�Ʈ��UTM                 | FE     | ���� | ����/�Ϸ�/�ʴ�/����/��ȸ �̺�Ʈ �α�, UTM �Ծ� ����. ([Google for Developers][8])    |
| R-112   | ���� ǥ��ȭ       | RFC?9457 ������(JSON)        | BE     | ���� | ��� 4xx/5xx `type/title/status/detail/instance` ����. ([RFC Editor][1])              |
| R-113   | ������            | X-Request-ID, OTel Ʈ���̽�    | BE/FE  | ���� | ��� ��û ���� ����, �ڵ� ���� ���̵� �ؼ�. ([opentelemetry-python-contrib][9])     |
| R-114   | noindex ����      | ���/���� ��ũ �˻�����         | BE     | ���� | `<meta name="robots" content="noindex">` Ȥ�� `X-Robots-Tag` ����. ([Google for Developers][5]) |

### 5) ���� ��� & ����(����)

**4.1 ���� ����(Self/Other) ? ����ȭ**  
�� ���� `v��{1..5}` �� ���� `d=v?3 ��{?2..+2}`; `sign=+1(E/S/T/J), ?1(I/N/F/P)`  
��ǥ�� `score_dim=��(sign_q��d_q)` �� **����ȭ** `norm=score_dim/(2��n_dim_q) ��[?1,+1]`.

**4.2 ���� ���� ����(Other ��ա����ǵ���Gap)**  
���� ���� `weight_r`(���� 1.5, �ٽ�ģ�� 1.2, �⺻ 1.0)  
`other_norm_dim = (��_r w_r��norm_r) / ��_r w_r`  
**���ǵ�** `��_dim = stdev({norm_r})`(�������� ��ġ)  
**���� ����** `gap_dim = other_norm_dim ? self_norm_dim`  
**�Ѱ� ��ǥ** `GapScore = mean(|gap_dim|)��100 (0..100)`.

### 6) NFR(��ġ+����)

* **����(�鿣��):** ���<500ms, **P95<1s**, ������<1%.
* **������Ż(75p):** **LCP��2.5s / INP��200ms / CLS��0.1** ? ��(Lighthouse)+�ʵ�(RUM/CrUX) ���� ����. ([web.dev][10])
* **���ټ�:** **WCAG?2.2 AA**��APG ����, ��Ŀ�� ǥ�á�Ű���� ��Ž��. ([W3C][11])
* **���� ǥ��ȭ:** **RFC?9457** ���� ��Ű�� ä��(7807 ��ü). ([RFC Editor][1])
* **������:** FastAPI OTel �ڵ����������� ���� ����. ([opentelemetry-python-contrib][9])
* **���� ����:** AdSense **�ǵ�ġ Ŭ�� ����**������ 0��. ([Google Help][7])

### 7) ������ ���� ����

1. **E2E 5�ó�����**(Self���ʴ��N ������������/����) ���÷���ũ �հ�.
2. Web Vitals(75p) ���� ���(��/�ʵ�). ([web.dev][10])
3. ��� ���� ������ **RFC?9457 JSON** ��Ű��. ([RFC Editor][1])
4. **k-�͸� �Ӱ�(k��3)** �̸� ��� ����� ���� ����. ([EPIC][3])
5. **AdSense ���̾ƿ� �˻�**(��å ������ üũ����Ʈ) ���� 0��. ([Google Help][7])

### 8) ����/�����̹���

* ������ ���� ��ū ���, �ּ� PII(�г��� ����).
* ���� ������ ��� ��踸, ���� ������/�ĺ��� �����(k-anonymity ���). ([EPIC][3])
* ���/���� ���������� `noindex`/`X-Robots-Tag` ����. ([Google for Developers][5])

### 9) ��� �ð�ȭ(��Ʈ)

* **���̴�(4��: EI/SN/TF/JP)** ? Self/Other ��� ������.
* **��ĳ��(2D)** ? EI vs SN, TF vs JP ���; ���� ���� �� �÷�(�ִ� 10 ǥ��).
* **MVP:** Chart.js(���� ���̴�/��ĳ��) �� ���� ��Ʈ�� �÷�����/ECharts ���. ([chartjs.org][2])

### 10) ��������Ʈ(��)

`POST /api/self/submit`, `POST /api/invite/create`, `POST /api/other/submit`,  
`GET /api/result/{token}`, `GET /share/og/{token}.png`(OG �̹���). **������ RFC?9457**. ([RFC Editor][1])

### 11) ������ ��Ű��(���)

`users(id, nickname, created_at)`  
`sessions(id, user_id, mode, invite_token, is_anonymous, expires_at, max_raters)`  
`questions(id, dim, sign, text, context)`  
`responses_self(session_id, question_id, value)`  
`responses_other(session_id, rater_id?, relation_tag, question_id, value, created_at)`  
`aggregates(session_id, dim, self_norm, other_norm, gap, sigma, n_raters, updated_at)`

### 12) ������/���̷�

* **��� ����:** ���� **3�� �̻�** ���� �� ���߰� �λ���Ʈ�� ����.
* **����:** OG �̹��� 1200��630 ����, �ֿ� �±� `og:title/description/image/url`. ([ogp.me][6])
* **����:** ��� ���� �Ʒ� 1, ���� �ߴ� 1, �ϴ� 1(2?3��), **Ŭ�� ����/���� ��ġ ����**. ([Google Help][7])

### 13) KPI/��ǥ(Metrics)

* **M-101** Self �Ϸ���, **M-102** ��� ������ ��, **M-103** GapScore �߾Ӱ�, **M-104** ���ǵ�(��) �߾Ӱ�, **M-105** ���� CTR, **M-106** OG ���� ������, **M-107** WebVitals(LCP/INP/CLS 75p), **M-108** RFC?9457 Ŀ������, **M-109** Confirmed-Click �߻���(0�� ����), **M-110** k-�Ӱ� �ؼ���. ([web.dev][10])

### 14) �׽�Ʈ ���̽�

* **T-101** Self 32���� ä��/����ȭ ��Ȯ��(��谪�������� ó��)
* **T-102** Other 10���� ���䡤�ߺ� ������P95<1s
* **T-103** ����/����ġ/��/Gap ���� �������Ӽ� �׽�Ʈ
* **T-104** ���̴�/��ĳ�� ����������� ����(>30fps)
* **T-105** **k<3 ����** �� ���� ��Ȱ��ȭ
* **T-106** RFC?9457 ������(4xx/5xx) ([RFC Editor][1])
* **T-107** `noindex`/`X-Robots-Tag` ���� Ȯ��(���/����) ([Google for Developers][5])
* **T-108** AdSense **�ǵ�ġ Ŭ�� ����** ���� üũ����Ʈ ���(��ư ���� ����) ([Google Help][7])
* **T-109** OTel Ʈ���̽�-�α�-��ûID ����

### 15) Traceability(�䱸���׽�Ʈ����ǥ)

| �䱸(R)     | �׽�Ʈ(T)        | ��ǥ(M)         |
| ----------- | ---------------- | --------------- |
| R-102       | T-101/T-106      | M-101/M-108     |
| R-103/104   | T-102            | M-102/M-107     |
| R-105       | T-103            | M-103/M-104     |
| R-106       | T-105            | M-110           |
| R-107       | T-104            | M-107           |
| R-108       | T-104            | M-106/M-105     |
| R-110       | T-108            | M-109           |
| R-112/113/114 | T-106/T-109/T-107 | M-108/M-107    |

---

## ���� ����

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"  
[2]: https://www.chartjs.org/docs/latest/charts/radar.html "Radar Chart"  
[3]: https://epic.org/wp-content/uploads/privacy/reidentification/Sweeney_Article.pdf "k-ANONYMITY: A MODEL FOR PROTECTING PRIVACY"  
[4]: https://www.mbtionline.com/en-US/Legal "Legal"  
[5]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag "Robots Meta Tags Specifications"  
[6]: https://ogp.me/ "The Open Graph protocol"  
[7]: https://support.google.com/adsense/answer/1346295 "Ad placement policies - Google AdSense Help"  
[8]: https://developers.google.com/analytics/devguides/collection/ga4/reference/events "Recommended events | Google Analytics"  
[9]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html "OpenTelemetry FastAPI Instrumentation"  
[10]: https://web.dev/articles/vitals "Web Vitals | Articles"  
[11]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines (WCAG) 2.2"

