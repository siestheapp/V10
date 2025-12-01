HTML (simplified excerpt)

Put this inside your size-twin-gallery.html card. Note the data-* attributes:

<!-- Carousel -->
<div class="twin-carousel" id="twinCarousel">
  <button class="nav prev" aria-label="Previous" id="prevBtn">‹</button>

  <div class="slides" id="slides">
    <!-- Slide 1 -->
    <div class="slide is-active"
         data-brand="Anthropologie"
         data-title="Somerset Maxi Dress"
         data-size="XS"
         data-comments="12"
         data-q="Is this petite or regular?"
         data-a="Regular!"
         data-shop="/shop/somerset-xs">
      <img src="/img/somerset-yellow.jpg" alt="Somerset Maxi Dress in XS on ellaa76">
    </div>

    <!-- Slide 2 -->
    <div class="slide"
         data-brand="Anthropologie"
         data-title="Peregrine Midi Dress"
         data-size="XS Petite"
         data-comments="7"
         data-q="How long is the skirt?"
         data-a="Hits mid-calf (I’m 5'3)."
         data-shop="/shop/peregrine-xs-petite">
      <img src="/img/peregrine-midi.jpg" alt="Peregrine Midi Dress in XS Petite on ellaa76">
    </div>

    <!-- Slide 3 -->
    <div class="slide"
         data-brand="LOFT"
         data-title="Versa Crepe Blazer"
         data-size="XXS Petite"
         data-comments="4"
         data-q="Sleeve length true petite?"
         data-a="Yes, lands at wrist."
         data-shop="/shop/loft-versa-crepe-xxs-petite">
      <img src="/img/loft-versa.jpg" alt="LOFT Versa Crepe Blazer in XXS Petite on ellaa76">
    </div>
  </div>

  <button class="nav next" aria-label="Next" id="nextBtn">›</button>
</div>

<!-- Info block driven by the active slide -->
<div class="tryon-info" id="tryonInfo">
  <div class="title">
    <strong id="brand">Anthropologie</strong>
    <span id="title">Somerset Maxi Dress</span>
    <span> — </span>
    <span id="size">XS</span>
  </div>

  <p class="hint">Swipe to see what else she wears.</p>

  <div class="cta-row">
    <a id="shopBtn" class="btn-primary" href="/shop/somerset-xs">Shop this item</a>
    <button class="btn-outline">See more from ellaa76</button>
  </div>

  <div class="dots" id="dots"></div>

  <!-- Comment teaser -->
  <button class="comment-teaser" id="commentTeaser" aria-label="Open comments">
    <div class="teaser-meta">Comments · <span id="cCount">12</span></div>
    <div class="teaser-line">
      <strong>Q:</strong> <span id="cQ">Is this petite or regular?</span>
      <span class="sep">·</span>
      <strong>A:</strong> <span id="cA">Regular!</span>
    </div>
    <div class="teaser-cta">See full thread &gt;</div>
  </button>
</div>


CSS: use your existing styles. (If you want my pill / dots styles again, I can paste them, but you already have the visual language in your screenshots.)

JS (drop-in, no dependencies)

This script wires the carousel, swipes, and info updates.

<script>
(function () {
  const slidesEl = document.getElementById('slides');
  const slideEls = Array.from(slidesEl.querySelectorAll('.slide'));
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');

  // Info elements
  const brandEl = document.getElementById('brand');
  const titleEl = document.getElementById('title');
  const sizeEl  = document.getElementById('size');
  const cCountEl = document.getElementById('cCount');
  const cQEl = document.getElementById('cQ');
  const cAEl = document.getElementById('cA');
  const shopBtn = document.getElementById('shopBtn');
  const dotsEl = document.getElementById('dots');

  let idx = slideEls.findIndex(el => el.classList.contains('is-active'));
  if (idx < 0) idx = 0;

  // Build dots
  dotsEl.innerHTML = slideEls.map((_, i) =>
    `<button class="dot${i===idx?' is-active':''}" data-dot="${i}" aria-label="Go to slide ${i+1}"></button>`
  ).join('');

  function applyFromSlide(i) {
    const s = slideEls[i];
    brandEl.textContent = s.dataset.brand || '';
    titleEl.textContent = s.dataset.title || '';
    sizeEl.textContent  = s.dataset.size || '';
    cCountEl.textContent = s.dataset.comments || '0';
    cQEl.textContent = s.dataset.q || '';
    cAEl.textContent = s.dataset.a || '';
    if (s.dataset.shop) shopBtn.setAttribute('href', s.dataset.shop);

    // toggle active class
    slideEls.forEach((el, k) => el.classList.toggle('is-active', k === i));
    // translate track (if you’re using a horizontal track)
    slidesEl.style.transform = `translateX(${-i * 100}%)`;

    // dots
    dotsEl.querySelectorAll('.dot').forEach((d, k) =>
      d.classList.toggle('is-active', k === i)
    );
  }

  function next() { idx = (idx + 1) % slideEls.length; applyFromSlide(idx); }
  function prev() { idx = (idx - 1 + slideEls.length) % slideEls.length; applyFromSlide(idx); }

  nextBtn.addEventListener('click', next);
  prevBtn.addEventListener('click', prev);

  // Dot navigation
  dotsEl.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-dot]');
    if (!btn) return;
    idx = parseInt(btn.dataset.dot, 10);
    applyFromSlide(idx);
  });

  // Touch swipe (basic)
  let startX = null;
  slidesEl.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, {passive:true});
  slidesEl.addEventListener('touchmove', e => {
    if (startX == null) return;
    const dx = e.touches[0].clientX - startX;
    if (Math.abs(dx) > 40) { dx < 0 ? next() : prev(); startX = null; }
  }, {passive:true});
  slidesEl.addEventListener('touchend', () => { startX = null; });

  // Keyboard (accessibility)
  slidesEl.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') prev();
  });

  // Initial paint
  applyFromSlide(idx);
})();
</script>


Track CSS hint: if you want a simple sliding track, use:

.twin-carousel { position: relative; overflow: hidden; }
.slides { display: flex; width: 100%; transition: transform 300ms ease; }
.slide { flex: 0 0 100%; }
.dot { width: 8px; height: 8px; border-radius: 9999px; background:#d1d5db; margin: 0 4px; }
.dot.is-active { width: 16px; background:#14b8a6; }