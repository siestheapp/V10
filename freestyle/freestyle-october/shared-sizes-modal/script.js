/* ===================================
   Demo Data
   =================================== */
const data = {
  currentUser: {
    id: "u_1",
    handle: "riley",
    initial: "R"
  }, // no avatar
  matchUser: {
    id: "u_2",
    handle: "ellaa76",
    avatarUrl: "../assets/img/videoframe_611.png"
  },
  product: {
    brand: "Anthropologie",
    name: "Somerset Chiffon Maxi Dress",
    // Use same product photo for both sides when no UGC available
    placeholderImageUrl: "../assets/img/videoframe_35967__1_-1760420352907__user1__Anthropologie__Somerset_Chiffon_Maxi_Dress__XXS-proxy-hero@3x.png",
    matchPhotoUrl: "../assets/img/videoframe_35967__1_-1760420352907__user1__Anthropologie__Somerset_Chiffon_Maxi_Dress__XXS-proxy-hero@3x.png"
  },
  sharedSizes: [
    { label: "S" }
  ]
};

/* ===================================
   DOM Elements
   =================================== */
const modal = document.getElementById('sharedSizesModal');
const modalCard = modal.querySelector('.modal-card');
const openBtn = document.getElementById('openModalBtn');
const closeBtn = modal.querySelector('.modal-close');
const overlay = modal.querySelector('.modal-overlay');
const seeClosetBtn = document.getElementById('seeClosetBtn');
const findMoreBtn = document.getElementById('findMoreBtn');

// Content elements
const matchHandleEl = document.getElementById('matchHandle');
const matchHandlePillEl = document.getElementById('matchHandlePill');
const matchHandleBtnEl = document.getElementById('matchHandleBtn');
const sizeCountEl = document.getElementById('sizeCount');
const currentUserAvatarEl = document.getElementById('currentUserAvatar');
const matchUserAvatarEl = document.getElementById('matchUserAvatar');
const currentUserImageEl = document.getElementById('currentUserImage');
const matchUserImageEl = document.getElementById('matchUserImage');
const currentUserSizesEl = document.getElementById('currentUserSizes');
const matchUserSizesEl = document.getElementById('matchUserSizes');
const productBrandEl = document.getElementById('productBrand');
const productNameEl = document.getElementById('productName');

/* ===================================
   Focus Trap State
   =================================== */
let previouslyFocusedElement = null;
const focusableSelectors = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

/* ===================================
   Render Modal Content
   =================================== */
function renderModalContent() {
  // Match user handle (appears in 3 places)
  const matchHandle = data.matchUser.handle;
  matchHandleEl.textContent = matchHandle;
  matchHandlePillEl.textContent = matchHandle;
  matchHandleBtnEl.textContent = matchHandle;

  // Size count (handle singular/plural)
  const sizeCount = data.sharedSizes.length;
  sizeCountEl.textContent = sizeCount;

  // Update "size" vs "sizes" in title
  const titleEl = document.getElementById('modalTitle');
  const sizeWord = sizeCount === 1 ? 'size' : 'sizes';
  titleEl.innerHTML = `You & <span id="matchHandle">${matchHandle}</span> share <span id="sizeCount">${sizeCount}</span> ${sizeWord}!`;

  // Current user avatar (initial only)
  const initialSpan = currentUserAvatarEl.querySelector('.avatar-initial');
  if (initialSpan) {
    initialSpan.textContent = data.currentUser.initial;
  }

  // Match user avatar
  matchUserAvatarEl.src = data.matchUser.avatarUrl;
  matchUserAvatarEl.alt = `${matchHandle}'s avatar`;

  // Product images
  renderProductImage(
    currentUserImageEl,
    data.product.placeholderImageUrl,
    'Product placeholder',
    true // isPlaceholder
  );

  renderProductImage(
    matchUserImageEl,
    data.product.matchPhotoUrl,
    `${matchHandle}'s ${data.product.name}`,
    false // isPlaceholder
  );

  // Size chips (show max 2, then +N)
  renderSizeChips(currentUserSizesEl, data.sharedSizes);
  renderSizeChips(matchUserSizesEl, data.sharedSizes);

  // Product info
  productBrandEl.textContent = data.product.brand;
  productNameEl.textContent = data.product.name;
}

/**
 * Render product image with fallback handling
 * @param {HTMLImageElement} imgEl - Image element
 * @param {string} imageUrl - Image URL
 * @param {string} altText - Alt text
 * @param {boolean} isPlaceholder - Whether this is the placeholder card
 */
function renderProductImage(imgEl, imageUrl, altText, isPlaceholder) {
  const wrapper = imgEl.closest('.product-image');
  const fallbackIcon = wrapper.querySelector('.image-fallback');
  const communityBadge = wrapper.querySelector('.community-badge');

  if (!imageUrl) {
    // Show fallback icon
    imgEl.style.display = 'none';
    if (fallbackIcon) {
      fallbackIcon.hidden = false;
    }

    // If this is match photo, show community badge
    if (!isPlaceholder && communityBadge) {
      communityBadge.hidden = false;
    }
  } else {
    // Load image
    imgEl.src = imageUrl;
    imgEl.alt = altText;
    imgEl.style.display = 'block';
    if (fallbackIcon) {
      fallbackIcon.hidden = true;
    }

    // Handle image load error
    imgEl.onerror = () => {
      imgEl.style.display = 'none';
      if (fallbackIcon) {
        fallbackIcon.hidden = false;
      }
    };
  }
}

/**
 * Render size chips (max 2 visible, then +N)
 * @param {HTMLElement} containerEl - Container element
 * @param {Array} sizes - Array of size objects
 */
function renderSizeChips(containerEl, sizes) {
  containerEl.innerHTML = '';

  const maxVisible = 2;
  const visibleSizes = sizes.slice(0, maxVisible);
  const extraCount = Math.max(0, sizes.length - maxVisible);

  visibleSizes.forEach(size => {
    const chip = document.createElement('span');
    chip.className = 'size-chip';
    chip.textContent = size.label;
    containerEl.appendChild(chip);
  });

  if (extraCount > 0) {
    const extraChip = document.createElement('span');
    extraChip.className = 'size-chip';
    extraChip.textContent = `+${extraCount}`;
    containerEl.appendChild(extraChip);
  }
}

/* ===================================
   Modal Open/Close
   =================================== */
function openModal() {
  // Analytics hook point
  console.log('[Analytics] Modal opened', {
    matchUser: data.matchUser.id,
    product: data.product.name,
    sharedSizesCount: data.sharedSizes.length
  });

  // Store previously focused element
  previouslyFocusedElement = document.activeElement;

  // Render content
  renderModalContent();

  // Show modal
  modal.hidden = false;

  // Focus first focusable element inside modal
  requestAnimationFrame(() => {
    const firstFocusable = modalCard.querySelector(focusableSelectors);
    if (firstFocusable) {
      firstFocusable.focus();
    }
  });

  // Trap focus
  document.addEventListener('keydown', handleKeyDown);
  modalCard.addEventListener('keydown', handleFocusTrap);
}

function closeModal() {
  // Analytics hook point
  console.log('[Analytics] Modal closed');

  // Hide modal
  modal.hidden = true;

  // Remove event listeners
  document.removeEventListener('keydown', handleKeyDown);
  modalCard.removeEventListener('keydown', handleFocusTrap);

  // Restore focus
  if (previouslyFocusedElement) {
    previouslyFocusedElement.focus();
    previouslyFocusedElement = null;
  }
}

/* ===================================
   Focus Trap
   =================================== */
function handleFocusTrap(e) {
  if (e.key !== 'Tab') return;

  const focusableElements = Array.from(
    modalCard.querySelectorAll(focusableSelectors)
  ).filter(el => !el.disabled && el.offsetParent !== null);

  if (focusableElements.length === 0) return;

  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  if (e.shiftKey && document.activeElement === firstElement) {
    // Shift+Tab on first element -> go to last
    e.preventDefault();
    lastElement.focus();
  } else if (!e.shiftKey && document.activeElement === lastElement) {
    // Tab on last element -> go to first
    e.preventDefault();
    firstElement.focus();
  }
}

/* ===================================
   Keyboard Handling
   =================================== */
function handleKeyDown(e) {
  if (e.key === 'Escape') {
    closeModal();
  }
}

/* ===================================
   CTA Handlers
   =================================== */
function handleSeeCloset() {
  // Analytics hook point
  console.log('[Analytics] See closet clicked', {
    matchUser: data.matchUser.id
  });

  console.log('See closet:', data.matchUser.id);
  // In production: navigate to user's closet page
  // window.location.href = `/users/${data.matchUser.id}/closet`;
}

function handleFindMoreTwins() {
  // Analytics hook point
  console.log('[Analytics] Find more twins clicked');

  console.log('Find more twins');
  // In production: navigate to discovery/search
  // window.location.href = '/discover';
}

/* ===================================
   Event Listeners
   =================================== */
openBtn.addEventListener('click', openModal);
closeBtn.addEventListener('click', closeModal);
overlay.addEventListener('click', closeModal);
seeClosetBtn.addEventListener('click', handleSeeCloset);
findMoreBtn.addEventListener('click', handleFindMoreTwins);

/* ===================================
   Initialization
   =================================== */
// Pre-render content on page load for faster modal open
document.addEventListener('DOMContentLoaded', () => {
  console.log('[Init] Shared Sizes Modal ready');
});
