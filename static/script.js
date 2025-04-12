const quotes = [
  "O son of Kunti, the nonpermanent appearance of happiness and distress, and their disappearance in due course, are like the appearance and disappearance of winter and summer seasons. They arise from sense perception, O scion of Bharata, and one must learn to tolerate them without being disturbed. ~Source: Bhagavad-Geeta 2.14",
  "For the soul there is neither birth nor death at any time. He has not come into being, does not come into being, and will not come into being. He is unborn, eternal, ever-existing, and primeval. He is not slain when the body is slain. ~Source: Bhagavad-Geeta 2.20",
  // Add all other quotes here...
];

const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
document.getElementById("quote").textContent = randomQuote;

const loading = document.getElementById('loading');
const form = document.querySelector('form');

form.addEventListener('submit', () => {
  loading.style.display = 'block';
});

const textarea = document.querySelector('textarea');
textarea.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = this.scrollHeight + 'px';
});

const animateButton = function(e) {
  e.preventDefault;
  e.target.classList.remove('animate');
  e.target.classList.add('animate');
  setTimeout(() => e.target.classList.remove('animate'), 700);
};

const animData = {
  container: document.getElementById('loading'),
  renderer: 'svg',
  loop: true,
  autoplay: true,
  path: 'https://assets10.lottiefiles.com/packages/lf20_poqmycwy.json'
};

const anim = bodymovin.loadAnimation(animData);