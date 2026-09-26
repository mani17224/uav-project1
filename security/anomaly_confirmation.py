class AnomalyConfirmation:
    def __init__(self, threshold=15.4998929848081, required_consecutive=3):
        self.threshold = threshold
        self.required_consecutive = required_consecutive
        self.consecutive_count = 0

    def update(self, score):
        score = float(score)
        is_anomaly = score > self.threshold

        if is_anomaly:
            self.consecutive_count += 1
        else:
            self.consecutive_count = 0

        if self.consecutive_count >= self.required_consecutive:
            state = "CONFIRMED_ANOMALY"
        elif is_anomaly:
            state = "SUSPECTED"
        else:
            state = "NORMAL"

        return {
            "score": score,
            "threshold": self.threshold,
            "raw_anomaly": is_anomaly,
            "consecutive_count": self.consecutive_count,
            "state": state,
            "confirmed": state == "CONFIRMED_ANOMALY"
        }
