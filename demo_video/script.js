
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function get(id) {
    return document.getElementById(id);
}

function show(id) {
    const el = get(id);
    if (el) el.classList.add('active');
}

function hide(id) {
    const el = get(id);
    if (el) el.classList.remove('active');
}

async function runTimeline() {
    console.log("Animation Started");

    // Initial delay to ensure recording has started
    await wait(3000);

    // FRAME 1: Title Screen
    console.log("Frame 1: Title");
    show('scene-1');
    await wait(13597);
    hide('scene-1');

    // FRAME 2: AgentBeats Page Load
    console.log("Frame 2: Page Load");
    show('scene-2');
    const scrollArrow = document.querySelector('.scroll-arrow');
    await wait(2000);
    if (scrollArrow) scrollArrow.style.opacity = '0';
    const browserContent = document.querySelector('#scene-2 .browser-content');
    if (browserContent) {
        browserContent.scroll({ top: 100, behavior: 'smooth' });
    }
    await wait(20926);
    hide('scene-2');

    // FRAME 3: Leaderboard Overview
    console.log("Frame 3: Leaderboard");
    show('scene-3');
    await wait(100);

    const rows = document.querySelectorAll('#scene-3 .row:not(.header-row)');
    const stepTime3 = 22926 / 3;

    // Row 1
    rows[0].style.backgroundColor = 'rgba(16, 185, 129, 0.2)';
    document.querySelector('.callout').classList.remove('hidden');
    await wait(stepTime3);

    // Row 2
    rows[0].style.backgroundColor = '';
    document.querySelector('.callout').classList.add('hidden');
    rows[1].style.backgroundColor = 'rgba(245, 158, 11, 0.2)';
    await wait(stepTime3);

    // Row 3
    rows[1].style.backgroundColor = '';
    rows[2].style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
    await wait(stepTime3);
    rows[2].style.backgroundColor = '';
    hide('scene-3');


    // FRAME 4: Comparison Graphic 
    console.log("Frame 4: Comparison");
    show('scene-4');
    const time4 = 9231;
    document.querySelector('.card-1').classList.add('show');
    await wait(time4 * 0.3);
    document.querySelector('.card-2').classList.add('show');
    await wait(time4 * 0.3);
    document.querySelector('.card-3').classList.add('show');
    await wait(time4 * 0.4);
    hide('scene-4');

    // FRAME 5: How It Works 
    console.log("Frame 5: How it works");
    show('scene-5');
    const time5 = 15752;
    const testTypes = document.querySelectorAll('.type-item');
    for (let item of testTypes) {
        item.classList.add('show');
        await wait(time5 / 4);
    }
    await wait(time5 / 4);
    hide('scene-5');

    // FRAME 6: SOCBench Deep Dive 
    console.log("Frame 6: SOCBench");
    show('scene-6');
    const time6 = 12357;
    const greenChecks = document.querySelectorAll('#scene-6 .check-item');
    for (let item of greenChecks) {
        item.classList.add('show');
        await wait(time6 / 5);
    }
    await wait(time6 / 5);
    hide('scene-6');

    // FRAME 7: Home Automation
    console.log("Frame 7: Home Auto");
    show('scene-7');
    const time7 = 12598;
    await wait(time7 * 0.4);
    document.querySelector('.callout-warning').classList.remove('hidden');
    await wait(time7 * 0.6);
    hide('scene-7');

    // FRAME 8: Law Purple
    console.log("Frame 8: Law Purple");
    show('scene-8');
    const time8 = 12412;
    await wait(time8 * 0.4);
    document.querySelector('.do-not-deploy').classList.remove('hidden');
    await wait(time8 * 0.6);
    hide('scene-8');

    // FRAME 9: MITRE
    console.log("Frame 9: MITRE");
    show('scene-9');
    await wait(12060);
    hide('scene-9');

    // FRAME 10: GitHub
    console.log("Frame 10: GitHub");
    show('scene-10');
    const time10 = 13524;

    const steps = document.querySelectorAll('#scene-10 .step');
    const timer = document.querySelector('#scene-10 .timer');
    let secs = 0;

    // Distribute time across steps
    const stepTime = (time10 - 2000) / steps.length;

    for (let i = 0; i < steps.length; i++) {
        steps[i].classList.add('active');
        steps[i].querySelector('.icon').textContent = '🔄';
        await wait(stepTime);
        steps[i].classList.remove('active');
        steps[i].classList.add('done');
        steps[i].querySelector('.icon').textContent = '✅';

        secs += Math.floor(stepTime / 100);
        timer.textContent = `0m ${secs < 10 ? '0' + secs : secs}s`;
    }

    timer.textContent = "4m 32s";
    document.querySelector('#scene-10 .artifacts').classList.remove('hidden');
    await wait(2000);
    hide('scene-10');

    // FRAME 11: Submit
    console.log("Frame 11: Submit");
    show('scene-11');
    const time11 = 11160;
    document.querySelector('.step-new-1').classList.add('show');
    await wait(time11 * 0.2);
    document.querySelector('.step-new-2').classList.add('show');
    await wait(time11 * 0.2);
    document.querySelector('.step-new-3').classList.add('show');
    await wait(time11 * 0.2);
    document.querySelector('.toml-code').classList.remove('hidden');
    await wait(time11 * 0.2);
    document.querySelector('.toml-code').classList.add('hidden');
    document.querySelector('.step-new-4').classList.add('show');
    await wait(time11 * 0.2);
    hide('scene-11');

    // FRAME 12: Leaderboard 2 & Outro
    console.log("Frame 12/13/14: Outro");
    show('scene-12');
    const time12 = 11529;
    const podiums = document.querySelectorAll('.podium-row');
    podiums[0].classList.add('show');
    await wait(time12 * 0.3);
    podiums[1].classList.add('show');
    await wait(time12 * 0.3);
    podiums[2].classList.add('show');
    await wait(time12 * 0.4);
    hide('scene-12');

    show('scene-13');
    await wait(3000);
    hide('scene-13');

    show('scene-14');
    await wait(3000);

    // FINISHED
    document.getElementById('finished-flag').style.display = 'block';
    console.log("DONE");
}

// Robust start detection
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runTimeline);
} else {
    runTimeline();
}
