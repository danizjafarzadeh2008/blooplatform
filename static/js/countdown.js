class CountdownTimer {
    constructor(targetDate, displayElement) {
        this.targetDate = new Date(targetDate).getTime();
        this.displayElement = displayElement;
        this.timerInterval = null;
    }

    start() {
        this.updateTimer();
        this.timerInterval = setInterval(() => this.updateTimer(), 1000);
    }

    updateTimer() {
        const now = new Date().getTime();
        const distance = this.targetDate - now;

        if (distance < 0) {
            clearInterval(this.timerInterval);
            this.displayElement.innerHTML = "EXPIRED";
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        this.displayElement.innerHTML = `
            <div class="countdown-box">
                <div class="text-3xl sm:text-4xl font-bold text-white">${days.toString().padStart(2, '0')}</div>
                <div class="text-sm text-gray-200 mt-2">Days</div>
            </div>
            <div class="countdown-box">
                <div class="text-3xl sm:text-4xl font-bold text-white">${hours.toString().padStart(2, '0')}</div>
                <div class="text-sm text-gray-200 mt-2">Hours</div>
            </div>
            <div class="countdown-box">
                <div class="text-3xl sm:text-4xl font-bold text-white">${minutes.toString().padStart(2, '0')}</div>
                <div class="text-sm text-gray-200 mt-2">Minutes</div>
            </div>
            <div class="countdown-box">
                <div class="text-3xl sm:text-4xl font-bold text-white">${seconds.toString().padStart(2, '0')}</div>
                <div class="text-sm text-gray-200 mt-2">Seconds</div>
            </div>
        `;
    }

    stop() {
        clearInterval(this.timerInterval);
    }
}
document.addEventListener('DOMContentLoaded', function () {
    const countdownElements = document.querySelectorAll('[data-countdown]');

    countdownElements.forEach(element => {
        const targetDate = element.getAttribute('data-countdown');
        const timer = new CountdownTimer(targetDate, element);
        timer.start();
    });
});