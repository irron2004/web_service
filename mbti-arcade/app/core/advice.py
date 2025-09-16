from typing import Dict, List

class MBTIAdvice:
    """MBTI 결과에 따른 개인화된 조언 생성기"""
    
    @staticmethod
    def generate_advice(my_mbti: str, friend_mbti: str, relation: str, scores: Dict) -> str:
        """개인화된 조언 생성"""
        
        # 기본 조언 템플릿
        advice_parts = []
        
        # 관계별 조언
        relation_advice = MBTIAdvice._get_relation_advice(relation, my_mbti, friend_mbti)
        if relation_advice:
            advice_parts.append(relation_advice)
        
        # MBTI 유사도 분석
        similarity_advice = MBTIAdvice._get_similarity_advice(my_mbti, friend_mbti)
        if similarity_advice:
            advice_parts.append(similarity_advice)
        
        # 개별 지표 분석
        indicator_advice = MBTIAdvice._get_indicator_advice(scores)
        if indicator_advice:
            advice_parts.append(indicator_advice)
        
        # 통합 조언
        if not advice_parts:
            advice_parts.append("두 사람의 MBTI를 비교해보니 흥미로운 차이점들이 보입니다. 서로의 성향을 이해하고 존중하는 것이 좋은 관계의 시작입니다.")
        
        return " ".join(advice_parts)
    
    @staticmethod
    def _get_relation_advice(relation: str, my_mbti: str, friend_mbti: str) -> str:
        """관계별 조언"""
        relation_map = {
            "friend": "친구 관계에서는",
            "boyfriend": "연인 관계에서는",
            "girlfriend": "연인 관계에서는", 
            "family": "가족 관계에서는",
            "colleague": "직장 동료 관계에서는",
            "acquaintance": "지인 관계에서는"
        }
        
        relation_text = relation_map.get(relation, "이 관계에서는")
        
        if my_mbti == friend_mbti:
            return f"{relation_text} 서로의 성향이 매우 유사하여 쉽게 이해할 수 있을 것입니다. 하지만 너무 비슷한 성향 때문에 갈등이 생길 수도 있으니 주의하세요."
        else:
            return f"{relation_text} 서로 다른 성향을 가진 만큼, 상호 보완적인 관계를 만들 수 있습니다. 차이점을 인정하고 배우는 자세가 중요합니다."
    
    @staticmethod
    def _get_similarity_advice(my_mbti: str, friend_mbti: str) -> str:
        """MBTI 유사도 분석"""
        # 첫 번째 글자 (E/I) 비교
        ei_match = my_mbti[0] == friend_mbti[0]
        # 두 번째 글자 (S/N) 비교  
        sn_match = my_mbti[1] == friend_mbti[1]
        # 세 번째 글자 (T/F) 비교
        tf_match = my_mbti[2] == friend_mbti[2]
        # 네 번째 글자 (J/P) 비교
        jp_match = my_mbti[3] == friend_mbti[3]
        
        matches = sum([ei_match, sn_match, tf_match, jp_match])
        
        if matches == 4:
            return "두 사람의 MBTI가 완전히 일치합니다! 매우 드문 경우로, 서로를 깊이 이해할 수 있는 특별한 관계일 것입니다."
        elif matches == 3:
            return "세 개의 지표가 일치하는 좋은 궁합입니다. 대부분의 상황에서 서로를 잘 이해할 수 있을 것입니다."
        elif matches == 2:
            return "두 개의 지표가 일치하는 보통의 궁합입니다. 서로 배우고 성장할 수 있는 균형잡힌 관계가 될 것입니다."
        elif matches == 1:
            return "하나의 지표만 일치하는 상반된 성향입니다. 서로 다른 관점에서 배울 수 있는 기회가 많을 것입니다."
        else:
            return "모든 지표가 다른 완전히 상반된 성향입니다. 서로를 이해하는 데 시간이 걸릴 수 있지만, 한번 이해하면 매우 보완적인 관계가 될 수 있습니다."
    
    @staticmethod
    def _get_indicator_advice(scores: Dict) -> str:
        """개별 지표 분석"""
        advice_parts = []
        
        # E/I 분석
        e_score = scores.get("E", 50)
        i_score = scores.get("I", 50)
        if abs(e_score - i_score) > 30:
            if e_score > i_score:
                advice_parts.append("외향적 성향이 강하게 나타났습니다. 활발한 소통과 다양한 활동을 통해 관계를 발전시킬 수 있을 것입니다.")
            else:
                advice_parts.append("내향적 성향이 강하게 나타났습니다. 깊이 있는 대화와 충분한 개인 시간을 통해 관계를 발전시킬 수 있을 것입니다.")
        
        # S/N 분석
        s_score = scores.get("S", 50)
        n_score = scores.get("N", 50)
        if abs(s_score - n_score) > 30:
            if s_score > n_score:
                advice_parts.append("실용적이고 구체적인 성향이 강합니다. 현실적인 계획과 실질적인 도움을 통해 관계를 발전시킬 수 있을 것입니다.")
            else:
                advice_parts.append("직관적이고 창의적인 성향이 강합니다. 새로운 아이디어와 미래지향적인 관점을 통해 관계를 발전시킬 수 있을 것입니다.")
        
        # T/F 분석
        t_score = scores.get("T", 50)
        f_score = scores.get("F", 50)
        if abs(t_score - f_score) > 30:
            if t_score > f_score:
                advice_parts.append("논리적이고 객관적인 성향이 강합니다. 명확한 소통과 합리적인 접근을 통해 관계를 발전시킬 수 있을 것입니다.")
            else:
                advice_parts.append("감정적이고 공감적인 성향이 강합니다. 따뜻한 마음과 정서적 지지를 통해 관계를 발전시킬 수 있을 것입니다.")
        
        # J/P 분석
        j_score = scores.get("J", 50)
        p_score = scores.get("P", 50)
        if abs(j_score - p_score) > 30:
            if j_score > p_score:
                advice_parts.append("계획적이고 체계적인 성향이 강합니다. 명확한 약속과 일정 관리를 통해 관계를 발전시킬 수 있을 것입니다.")
            else:
                advice_parts.append("유연하고 적응적인 성향이 강합니다. 자유로운 분위기와 즉흥적인 활동을 통해 관계를 발전시킬 수 있을 것입니다.")
        
        return " ".join(advice_parts) 