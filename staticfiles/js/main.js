// ========================================
// DARK MODE TOGGLE
// ========================================
document.addEventListener('DOMContentLoaded', function() {

    const themeToggle = document.getElementById('themeToggle');
    const themeIcon   = document.getElementById('themeIcon');
    const htmlEl      = document.documentElement;

    // Check saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlEl.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Toggle theme on click
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const current  = htmlEl.getAttribute('data-theme');
            const newTheme = current === 'light' ? 'dark' : 'light';
            htmlEl.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }

    // ========================================
    // IMAGE UPLOAD & FILE EXPLORER FIX
    // ========================================
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const previewImg = document.getElementById('previewImg');
    const uploadText = document.getElementById('uploadText');

    if (uploadArea && imageInput) {

        // Click on upload area opens file explorer
        uploadArea.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            imageInput.click();
        });

        // Drag over
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        // Drag leave
        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('dragover');
        });

        // Drop file
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) {
                showPreview(file);
                // Set file to input
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                imageInput.files = dataTransfer.files;
            }
        });

        // File input change
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                showPreview(file);
            }
        });
    }

    function showPreview(file) {
        // Validate file type
        const allowed = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!allowed.includes(file.type)) {
            alert('Only JPG and PNG images are allowed!');
            return;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('Image size must be less than 10MB!');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            if (previewImg) {
                previewImg.src          = e.target.result;
                previewImg.style.display = 'block';
            }
            if (uploadText) {
                uploadText.style.display = 'none';
            }
        };
        reader.readAsDataURL(file);
    }

    // ========================================
    // CONFIDENCE BAR ANIMATION
    // ========================================
    const fills = document.querySelectorAll('.confidence-fill');
    fills.forEach(function(fill) {
        const width = fill.getAttribute('data-width');
        setTimeout(function() {
            fill.style.width = width + '%';
        }, 300);
    });

    // ========================================
    // AUTO DISMISS ALERTS
    // ========================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.remove('show');
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 4000);
    });

    // ========================================
    // LOADING SPINNER ON FORM SUBMIT
    // ========================================
    const uploadForm     = document.getElementById('uploadForm');
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            if (imageInput && imageInput.files.length === 0) {
                e.preventDefault();
                alert('Please select an image first!');
                return;
            }
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }
        });
    }

    // ========================================
    // SMOOTH SCROLL
    // ========================================
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(
                this.getAttribute('href')
            );
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ========================================
    // NAVBAR SCROLL EFFECT
    // ========================================
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
            } else {
                navbar.style.boxShadow = '0 2px 15px rgba(0,0,0,0.2)';
            }
        }
    });

});