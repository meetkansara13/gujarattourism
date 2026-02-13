/* heritage.js
   Place: static/js/heritage.js
   Enhanced version
*/

(function(){
  /* Helpers */
  const qs = (s, ctx=document) => ctx.querySelector(s);
  const qsa = (s, ctx=document) => Array.from(ctx.querySelectorAll(s));

  /* --- Read More toggles --- */
  function initReadMore(){
    qsa('.history-card .read-more-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const card = btn.closest('.history-card');
        const full = card.querySelector('.full-text');
        const brief = card.querySelector('.brief-text');
        if(full.style.display === 'block'){
          full.style.display = 'none';
          if(brief) brief.style.display = '';
          btn.innerText = 'Read More';
        } else {
          full.style.display = 'block';
          if(brief) brief.style.display = 'none';
          btn.innerText = 'Read Less';
        }
      });
    });
  }

  /* --- Food search --- */
  function initFoodSearch(){
    const inp = qs('#food-search');
    if(!inp) return;
    inp.addEventListener('input', function(){
      const v = this.value.trim().toLowerCase();
      qsa('#food-list .food-card').forEach(card => {
        const title = (card.querySelector('h4')||{}).innerText?.toLowerCase() || '';
        const desc = (card.querySelector('.card-body p')||{}).innerText?.toLowerCase() || '';
        card.style.display = (title.includes(v) || desc.includes(v)) ? '' : 'none';
      });
    });
  }

  /* --- Tour select auto-price --- */
  function initTourSelect(){
    const sel = qs('#tour-select');
    const priceInput = qs('#price_input');
    if(!sel || !priceInput) return;

    function setPriceFromOption(opt){
      if(opt && opt.dataset.price){
        priceInput.value = '₹' + opt.dataset.price;
      } else {
        priceInput.value = '₹15000'; // default fallback
      }
    }

    sel.addEventListener('change', function(){
      const opt = this.options[this.selectedIndex];
      setPriceFromOption(opt);
    });

    // initialize with first option or fallback
    if(sel.options.length > 0){
      const opt = sel.options[sel.selectedIndex] || sel.options[0];
      setPriceFromOption(opt);
    } else {
      priceInput.value = '₹15000';
    }
  }

  /* --- AJAX booking --- */
  
function initBooking(){
  const btn = qs('#book-now');
  if(!btn) return;

  btn.addEventListener('click', async function(e){
    e.preventDefault();
    const tour_id = qs('#tour-select')?.value || '';
    const full_name = qs('#full_name')?.value.trim();
    const phone = qs('#phone')?.value.trim();
    const email = qs('#email')?.value.trim();
    const priceRaw = qs('#price_input')?.value.replace('₹','').trim() || '15000';
    const notes = qs('#notes')?.value.trim();

    if(!tour_id || !full_name || !phone){
      showMessage('Please fill in required fields.', false);
      return;
    }
    
    const formData = new FormData();
    formData.append('tour_id', tour_id);
    formData.append('full_name', full_name);
    formData.append('phone', phone);
    formData.append('email', email);
    formData.append('price', priceRaw);
    formData.append('notes', notes);

    const url = window.HERITAGE_BOOK_URL || '/book-heritage-tour/';
    const csrftoken = getCSRFToken();

    try {
      const res = await fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': csrftoken || '' }
      });

      if(res.status === 401){
        showMessage('Please login to book a tour.', false);
        // Optionally redirect to login page
        // window.location.href = '/accounts/login/?next=' + window.location.pathname;
        return;
      }

      const json = await res.json();
      if(res.ok && json.success){
        showMessage(json.message || 'heritagely approven', true);
        resetBookingForm();
      } else {
        showMessage(json.error || 'Booking failed, try again.', false);
      }

    } catch(err){
      console.error('Booking error:', err);
      showMessage('Error: ' + err.message, false);
    }
  });
}

  /* --- Tabs (backup if inline script missing) --- */
  function initTabs(){
    const tabButtons = qsa('.tab-btn');
    if(!tabButtons.length) return;
    tabButtons.forEach(b=>{
      b.addEventListener('click', ()=> {
        tabButtons.forEach(x=>x.classList.remove('active'));
        b.classList.add('active');
        qsa('.section').forEach(s=>s.style.display='none');
        const el = qs('#'+b.dataset.tab);
        if(el) el.style.display='block';
      });
    });
  }

  /* --- Init all --- */
  document.addEventListener('DOMContentLoaded', function(){
    initReadMore();
    initFoodSearch();
    initTourSelect();
    initBooking();
    initTabs();
  });

})();
