from dataclasses import dataclass
from .uav_state import UAVState


@dataclass
class ThreatAssessment:
    category: str
    risk_level: str
    reason: str
    recommended_response: str
    indicators: list


class ThreatAssessmentEngine:

    def assess(self, score, consecutive_count, state: UAVState):
        indicators = []
        category = "UNKNOWN_ANOMALY"

        # --- Threat diagnosis ---
        if not state.gps_valid:
            category = "NAVIGATION_ANOMALY"
            indicators.append("GPS invalid")

        elif state.speed() >= 5.0:
            category = "HIGH_MOTION_ANOMALY"
            indicators.append("High UAV velocity")

        elif state.battery_remaining is not None and state.battery_remaining <= 20:
            category = "POWER_RELATED_ANOMALY"
            indicators.append("Low battery")

        else:
            category = "UNKNOWN_ANOMALY"

        # --- Persistence ---
        if consecutive_count >= 5:
            indicators.append("Persistent anomaly")
        elif consecutive_count >= 3:
            indicators.append("Confirmed anomaly")

        # --- Score severity ---
        if score >= 30 or consecutive_count >= 8:
            risk_level = "CRITICAL"
        elif score >= 22 or consecutive_count >= 5:
            risk_level = "HIGH"
        elif score >= 18 or consecutive_count >= 3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # --- Context modifiers ---
        if state.speed() >= 8.0:
            indicators.append("Very high UAV speed")

        if abs(state.roll) >= 0.6 or abs(state.pitch) >= 0.6:
            indicators.append("Large attitude deviation")

        if state.battery_remaining is not None and state.battery_remaining <= 20:
            indicators.append("Battery condition requires attention")

        # --- Response selection ---
        if risk_level == "CRITICAL":
            response = "LAND"
        elif risk_level == "HIGH":
            response = "RTL"
        elif risk_level == "MEDIUM":
            response = "HOLD"
        else:
            response = "MONITOR"

        reason = "; ".join(indicators) if indicators else "No significant contextual indicator"

        return ThreatAssessment(
            category=category,
            risk_level=risk_level,
            reason=reason,
            recommended_response=response,
            indicators=indicators,
        )
