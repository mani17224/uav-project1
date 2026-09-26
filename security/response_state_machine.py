from enum import Enum


class SecurityState(Enum):
    NORMAL = "NORMAL"
    SUSPECTED = "SUSPECTED"
    CONFIRMED = "CONFIRMED"
    RESPONSE_ACTIVE = "RESPONSE_ACTIVE"
    RECOVERING = "RECOVERING"
    SAFE = "SAFE"
    RESPONSE_FAILED = "RESPONSE_FAILED"


class ResponseStateMachine:

    def __init__(self):
        self.state = SecurityState.NORMAL
        self.selected_response = "MONITOR"

    def update(self, confirmation, assessment=None):

        confirmation_state = confirmation["state"]

        if confirmation_state == "NORMAL":
            if self.state not in (
                SecurityState.RESPONSE_ACTIVE,
                SecurityState.RECOVERING
            ):
                self.state = SecurityState.NORMAL
                self.selected_response = "MONITOR"

        elif confirmation_state == "SUSPECTED":
            if self.state == SecurityState.NORMAL:
                self.state = SecurityState.SUSPECTED

        elif confirmation_state == "CONFIRMED_ANOMALY":
            self.state = SecurityState.CONFIRMED

            if assessment is not None:
                self.selected_response = assessment.recommended_response

        return {
            "security_state": self.state.value,
            "response": self.selected_response,
            "confirmed": self.state == SecurityState.CONFIRMED,
        }

    def activate_response(self):
        if self.state == SecurityState.CONFIRMED:
            self.state = SecurityState.RESPONSE_ACTIVE

    def start_recovery(self):
        if self.state == SecurityState.RESPONSE_ACTIVE:
            self.state = SecurityState.RECOVERING

    def mark_safe(self):
        self.state = SecurityState.SAFE
        self.selected_response = "NONE"

    def mark_failed(self):
        self.state = SecurityState.RESPONSE_FAILED
