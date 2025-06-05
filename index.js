        // Scroll Navigation Effect
        window.addEventListener('scroll', function() {
            const nav = document.querySelector('nav');
            if (window.scrollY > 50) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        });
        
        // Mobile Menu Toggle
        const menuBtn = document.querySelector('.mobile-menu-btn');
        const navLinks = document.querySelector('.nav-links');
        
        menuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            const icon = menuBtn.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
        
        // Close mobile menu when clicking a link
        const mobileLinks = document.querySelectorAll('.nav-links a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                const icon = menuBtn.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            });
        });
        
        // Custom cursor effect
        const cursor = document.querySelector('.cursor');
        const cursorDot = document.querySelector('.cursor-dot');
        
        document.addEventListener('mousemove', (e) => {
            const { clientX, clientY } = e;
            cursor.style.opacity = '1';
            cursorDot.style.opacity = '1';
            
            // Delayed position for outer cursor
            setTimeout(() => {
                cursor.style.left = `${clientX}px`;
                cursor.style.top = `${clientY}px`;
            }, 100);
            
            // Immediate position for inner cursor dot
            cursorDot.style.left = `${clientX}px`;
            cursorDot.style.top = `${clientY}px`;
        });
        
        // Cursor hover effect for clickable elements
        const clickables = document.querySelectorAll('a, button, input, textarea, .glass');
        clickables.forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.style.width = '50px';
                cursor.style.height = '50px';
                cursor.style.borderColor = 'var(--secondary)';
                cursorDot.style.width = '4px';
                cursorDot.style.height = '4px';
                cursorDot.style.backgroundColor = 'var(--secondary)';
            });
            
            el.addEventListener('mouseleave', () => {
                cursor.style.width = '40px';
                cursor.style.height = '40px';
                cursor.style.borderColor = 'var(--primary)';
                cursorDot.style.width = '8px';
                cursorDot.style.height = '8px';
                cursorDot.style.backgroundColor = 'var(--primary)';
            });
        });
        
        // Hide cursor when leaving window
        document.addEventListener('mouseout', (e) => {
            if (e.relatedTarget === null) {
                cursor.style.opacity = '0';
                cursorDot.style.opacity = '0';
            }
        });
        
        // Progress bar animation on scroll
        const skillSection = document.querySelector('#skills');
        const progressBars = document.querySelectorAll('.progress-bar');
        
        function showProgress() {
            const sectionPos = skillSection.getBoundingClientRect().top;
            const screenPos = window.innerHeight / 1.3;
            
            if (sectionPos < screenPos) {
                progressBars.forEach(bar => {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                });
                window.removeEventListener('scroll', showProgress);
            }
        }
        
        window.addEventListener('scroll', showProgress);
        
        // Form submission (you would typically handle this with a backend)
        const contactForm = document.querySelector('.contact-form form');
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Here you would typically send the form data to a server
            // For now, we'll just show a success message
            const formData = new FormData(contactForm);
            let formValues = {};
            
            for (let [key, value] of formData.entries()) {
                formValues[key] = value;
            }
            
            console.log('Form submitted:', formValues);
            
            // Reset the form
            contactForm.reset();
            
            // Show success message
            alert('Thanks for reaching out! I\'ll get back to you soon.');
        });