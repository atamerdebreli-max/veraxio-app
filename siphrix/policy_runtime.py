"""
siphrix.policy_runtime - Basit Policy Manager
AI Act Madde 50 kararlari icin.
"""
import uuid


class PolicyDecision:
    """Policy karar sonucu."""
    def __init__(self, verdict, reason, decision_id, matched_rule_id):
        self.verdict = verdict
        self.reason = reason
        self.decision_id = decision_id
        self.matched_rule_id = matched_rule_id


class PolicyManager:
    """Basit policy manager - AI Act Madde 50(1) chatbot kurali."""
    
    def __init__(self, policy=None):
        self.policy = policy or {}
    
    def decide(self, context):
        """Karar ver. context: {"action_name": "..."}"""
        action = context.get("action_name", "")
        decision_id = "DEC-" + uuid.uuid4().hex[:8].upper()
        
        if action == "chatbot_interaction_with_disclosure":
            return PolicyDecision(
                verdict="UYUMLU",
                reason="AI bildirimi mevcut - Madde 50(1) karsilandi",
                decision_id=decision_id,
                matched_rule_id="AI_ACT_50_1_DISCLOSURE",
            )
        elif action == "chatbot_interaction":
            return PolicyDecision(
                verdict="UYUMSUZ",
                reason="AI bildirimi yok - Madde 50(1) ihlali",
                decision_id=decision_id,
                matched_rule_id="AI_ACT_50_1_NO_DISCLOSURE",
            )
        else:
            return PolicyDecision(
                verdict="N/A",
                reason="Bilinmeyen aksiyon: " + action,
                decision_id=decision_id,
                matched_rule_id="N/A",
            )
