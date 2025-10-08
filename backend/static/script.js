// script.js (最终重构版)

/**
 * ----------------------------------------------------------------
 * 1. 公共函数 (在所有页面都会用到)
 * ----------------------------------------------------------------
 */

// 函数：异步加载公共组件 (页眉/页脚)
async function loadComponent(elementId, url) {
    try {
        const response = await fetch(url);
        if (response.ok) {
            document.getElementById(elementId).innerHTML = await response.text();
        } else {
            console.error(`Error loading component from ${url}: ${response.statusText}`);
        }
    } catch (error) {
        console.error(`Network error when loading component from ${url}:`, error);
    }
}

// 函数：初始化主题切换器 (需要在页眉加载后执行)
function initializeThemeSwitcher() {
    const themeSwitcher = document.getElementById('theme-switcher');
    const htmlElement = document.documentElement;

    if (!themeSwitcher) return;
    
    // 恢复本地存储的主题
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        htmlElement.classList.remove('dark-mode');
    } else {
        htmlElement.classList.add('dark-mode');
    }
    
    // 按钮点击事件
    themeSwitcher.addEventListener('click', () => {
        htmlElement.classList.toggle('dark-mode');
        localStorage.setItem('theme', htmlElement.classList.contains('dark-mode') ? 'dark' : 'light');
    });
}


/**
 * ----------------------------------------------------------------
 * 2. “关于我”页面的专属函数
 * ----------------------------------------------------------------
 */
async function loadAboutContent() {
    const aboutContainer = document.querySelector('.about-flex');
    if (!aboutContainer) return; // 如果页面上没有这个容器，就退出

    try {
        const response = await fetch('/api/about');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        
        // 填充数据
        document.getElementById('about-p1').textContent = data.paragraph1;
        document.getElementById('about-p2').textContent = data.paragraph2;
        document.getElementById('about-p3').innerHTML = `这个网站是我展示作品和分享想法的小天地。希望你喜欢这里的照片，也欢迎通过<a id="about-email" href="mailto:${data.email}">邮箱</a>与我交流。`;
        document.getElementById('about-image').src = data.imageUrl;

    } catch (error) {
        console.error("无法加载“关于我”的内容:", error);
        document.getElementById('about-p1').textContent = '内容加载失败，请稍后重试。';
    }
}


/**
 * ----------------------------------------------------------------
 * 3. “作品集”页面的专属函数
 * ----------------------------------------------------------------
 */
async function initializeGallery() {
    const galleryContainer = document.getElementById('gallery-container');
    if (!galleryContainer) return; // 如果页面上没有这个容器，就退出

    const paginationContainer = document.getElementById('pagination-container');
    const photosPerPage = 6;
    let currentPage = 1;
    let totalPhotos = 0;

    // (内部函数) 更新分页按钮的激活状态
    function updatePaginationButtons() {
        const buttons = document.querySelectorAll('.pagination-button');
        buttons.forEach((button, index) => {
            if ((index + 1) === currentPage) button.classList.add('active');
            else button.classList.remove('active');
        });
    }
    
    // (内部函数) 根据总数创建分页按钮
    function setupPagination() {
        paginationContainer.innerHTML = '';
        const pageCount = Math.ceil(totalPhotos / photosPerPage);
        for (let i = 1; i <= pageCount; i++) {
            const btn = document.createElement('button');
            btn.innerText = i;
            btn.className = 'pagination-button';
            btn.addEventListener('click', () => displayPage(i));
            paginationContainer.appendChild(btn);
        }
    }
    
    // (内部函数) 获取并显示某一页的照片
    async function displayPage(page) {
        currentPage = page;
        galleryContainer.innerHTML = '加载中...';
        try {
            const response = await fetch(`/api/photos?page=${page}&limit=${photosPerPage}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            totalPhotos = data.total_photos;
            galleryContainer.innerHTML = '';
            
            data.photos.forEach(photo => {
                const item = document.createElement('div');
                item.className = 'gallery-item';
                item.innerHTML = `<img src="${photo.url}" alt="${photo.alt}">`;
                galleryContainer.appendChild(item);
            });

        } catch (error) {
            console.error("无法加载作品:", error);
            galleryContainer.innerHTML = '<p>加载作品失败，请稍后重试。</p>';
        }
        updatePaginationButtons();
    }

    // 初始化流程
    try {
        const initialResponse = await fetch(`/api/photos?page=1&limit=1`);
        if (!initialResponse.ok) throw new Error('Failed to fetch initial data');
        const initialData = await initialResponse.json();

        totalPhotos = initialData.total_photos;
        setupPagination();
        await displayPage(1);

    } catch (error) {
        console.error("初始化作品集失败:", error);
        galleryContainer.innerHTML = '<p>无法连接到服务器。</p>';
    }
}


/**
 * ----------------------------------------------------------------
 * 4. 网站主入口 (所有逻辑从这里开始)
 * ----------------------------------------------------------------
 */
document.addEventListener('DOMContentLoaded', async () => {
    // 首先，加载所有页面都需要的公共部分 (页眉和页脚)
    await Promise.all([
        loadComponent('header-placeholder', '_header.html'),
        loadComponent('footer-placeholder', '_footer.html')
    ]);

    // 页眉加载完毕后，立刻初始化主题切换器
    initializeThemeSwitcher();

    // 然后，根据当前页面的特征，选择性地执行对应的专属函数
    // 这是一个更健壮的“路由”逻辑
    if (document.getElementById('gallery-container')) {
        initializeGallery();
    } else if (document.querySelector('.about-flex')) {
        loadAboutContent();
    }
    // 如果是首页(index.html)或其它页面，则不执行任何特殊操作
});