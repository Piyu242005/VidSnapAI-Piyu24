// Gallery Search, Filter, and Sort Functionality

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const sortSelect = document.getElementById('sortSelect');
    const viewButtons = document.querySelectorAll('.view-btn');
    const galleryGrid = document.getElementById('galleryGrid');
    
    let currentFilter = 'all';
    let currentSort = 'date-desc';
    let currentView = 'grid';
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            filterAndSort(searchTerm, currentFilter, currentSort);
        });
    }
    
    // Filter buttons
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            filterAndSort(searchInput?.value.toLowerCase() || '', currentFilter, currentSort);
        });
    });
    
    // Sort functionality
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            currentSort = e.target.value;
            filterAndSort(searchInput?.value.toLowerCase() || '', currentFilter, currentSort);
        });
    }
    
    // View toggle
    viewButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            viewButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            
            if (galleryGrid) {
                galleryGrid.className = `gallery-${currentView}`;
                if (currentView === 'list') {
                    galleryGrid.classList.add('gallery-list-view');
                } else {
                    galleryGrid.classList.add('gallery-grid');
                }
            }
        });
    });
    
    function filterAndSort(searchTerm, filter, sort) {
        const items = Array.from(document.querySelectorAll('.gallery-item'));
        
        // Filter
        let filtered = items.filter(item => {
            const reelName = item.dataset.reelName.toLowerCase();
            const matchesSearch = !searchTerm || reelName.includes(searchTerm);
            
            if (!matchesSearch) return false;
            
            if (filter === 'all') return true;
            if (filter === 'recent') {
                // Show items from last 7 days
                const dateStr = item.querySelector('.reel-date')?.textContent.trim();
                if (!dateStr || dateStr === 'Unknown') return false;
                const itemDate = new Date(dateStr);
                const weekAgo = new Date();
                weekAgo.setDate(weekAgo.getDate() - 7);
                return itemDate >= weekAgo;
            }
            if (filter === 'popular') {
                const views = parseInt(item.querySelector('.view-count')?.textContent || 0);
                return views > 10; // Popular if more than 10 views
            }
            
            return true;
        });
        
        // Sort
        filtered.sort((a, b) => {
            const aName = a.dataset.reelName.toLowerCase();
            const bName = b.dataset.reelName.toLowerCase();
            const aDate = a.querySelector('.reel-date')?.textContent.trim() || '';
            const bDate = b.querySelector('.reel-date')?.textContent.trim() || '';
            
            if (sort === 'name-asc') {
                return aName.localeCompare(bName);
            } else if (sort === 'name-desc') {
                return bName.localeCompare(aName);
            } else if (sort === 'date-asc') {
                return new Date(aDate) - new Date(bDate);
            } else { // date-desc
                return new Date(bDate) - new Date(aDate);
            }
        });
        
        // Hide all items
        items.forEach(item => {
            item.style.display = 'none';
        });
        
        // Show filtered and sorted items
        filtered.forEach(item => {
            item.style.display = 'block';
        });
        
        // Update count
        const countEl = document.getElementById('reelCount');
        if (countEl) {
            countEl.textContent = filtered.length;
        }
    }
});

