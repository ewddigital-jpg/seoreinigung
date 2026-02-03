(function(){
    // Cookie Banner
    var cookie = document.getElementById('cookie');
    if(cookie && !localStorage.getItem('cookieConsent')){
        setTimeout(function(){ cookie.classList.add('show'); }, 1000);
    }
    window.acceptCookie = function(){
        localStorage.setItem('cookieConsent', '1');
        if(cookie) cookie.classList.remove('show');
    };
    window.rejectCookie = function(){
        localStorage.setItem('cookieConsent', '0');
        if(cookie) cookie.classList.remove('show');
    };
    
    // Mobile Menu
    var menuBtn = document.getElementById('menuBtn');
    var nav = document.getElementById('nav');
    if(menuBtn && nav){
        menuBtn.addEventListener('click', function(){
            nav.classList.toggle('active');
        });
    }
    
    // Smooth Scroll
    document.querySelectorAll('a[href^="#"]').forEach(function(a){
        a.addEventListener('click', function(e){
            var href = this.getAttribute('href');
            if(href !== '#'){
                e.preventDefault();
                var target = document.querySelector(href);
                if(target){
                    var offset = window.innerWidth < 768 ? 70 : 80;
                    window.scrollTo({
                        top: target.offsetTop - offset,
                        behavior: 'smooth'
                    });
                }
            }
            if(nav) nav.classList.remove('active');
        });
    });
    
    // Close mobile menu on link click
    document.querySelectorAll('nav a').forEach(function(a){
        a.addEventListener('click', function(){
            if(nav) nav.classList.remove('active');
        });
    });
    
    // Header shadow on scroll
    var header = document.querySelector('header');
    if(header){
        window.addEventListener('scroll', function(){
            header.style.boxShadow = window.scrollY > 50 ? '0 4px 20px rgba(0,0,0,0.08)' : 'none';
        }, {passive: true});
    }
    
    // Handle anchor links from other pages
    if(window.location.hash){
        setTimeout(function(){
            var target = document.querySelector(window.location.hash);
            if(target){
                var offset = window.innerWidth < 768 ? 70 : 80;
                window.scrollTo({
                    top: target.offsetTop - offset,
                    behavior: 'smooth'
                });
            }
        }, 100);
    }
})();
