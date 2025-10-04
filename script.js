// 主题切换逻辑
function initializeThemeSwitcher() {
    const themeSwitcher = document.getElementById('theme-switcher');
    const htmlElement = document.documentElement;

    if (!themeSwitcher) return;
    
    // 按钮点击事件 (只负责切换 class 和保存状态)
    themeSwitcher.addEventListener('click', () => {
        htmlElement.classList.toggle('dark-mode');
        localStorage.setItem('theme', htmlElement.classList.contains('dark-mode') ? 'dark' : 'light');
    });

    // 页面加载时，根据本地存储恢复主题
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        htmlElement.classList.remove('dark-mode');
    } else {
        htmlElement.classList.add('dark-mode');
    }
}

// 异步加载公共组件 (页眉/页脚) 的函数
async function loadComponent(elementId, url) {
    try {
        const response = await fetch(url);
        if (response.ok) {
            const text = await response.text();
            document.getElementById(elementId).innerHTML = text;
        } else {
            console.error(`Error loading component from ${url}: ${response.statusText}`);
        }
    } catch (error) {
        console.error(`Network error when loading component from ${url}:`, error);
    }
}

// 网站主执行函数
async function main() {
    await Promise.all([
        loadComponent('header-placeholder', '_header.html'),
        loadComponent('footer-placeholder', '_footer.html')
    ]);

    // 等待页眉加载完毕后，再初始化其中的主题切换器
    initializeThemeSwitcher();
}

// script.js

// ... 您原有的 script.js 代码保持不变 ...

// --- ↓↓↓ 从这里开始添加分页功能代码 ↓↓↓ ---

// 当文档加载完成后，执行与分页相关的操作
document.addEventListener('DOMContentLoaded', () => {
    // 检查当前是否在作品集页面
    const galleryContainer = document.getElementById('gallery-container');
    if (!galleryContainer) {
        return; // 如果不在作品集页面，则不执行后续代码
    }

    // 1. 在这里管理你所有的照片
    // 以后增加或删除照片，只需要修改这个数组即可
    const allPhotos = [
        { src: 'src/images/sb01.webp', alt: '作品一描述' },
        { src: 'src/images/sb02.webp', alt: '作品二描述' },
        { src: 'src/images/sb03.webp', alt: '作品三描述' },
        { src: 'src/images/sb04.webp', alt: '作品四描述' },
        { src: 'src/images/sb05.webp', alt: '作品五描述' },
        { src: 'src/images/sb06.webp', alt: '作品六描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        { src: 'src/images/sb07.webp', alt: '作品七描述' },
        // --- 假设您未来增加了更多照片 ---
        // { src: 'https://via.placeholder.com/600x400/CCCCCC/FFFFFF?text=作品八', alt: '作品八描述' },
        // { src: 'https://via.placeholder.com/600x400/CCCCCC/FFFFFF?text=作品九', alt: '作品九描述' },
        // { src: 'https://via.placeholder.com/600x400/CCCCCC/FFFFFF?text=作品十', alt: '作品十描述' },
        // { src: 'https://via.placeholder.com/600x400/CCCCCC/FFFFFF?text=作品十一', alt: '作品十一描述' },
        // { src: 'https://via.placeholder.com/600x400/CCCCCC/FFFFFF?text=作品十二', alt: '作品十二描述' },
        // { src: 'https://via.placeholder.com/600x400/CCCCCC/FFFFFF?text=作品十三', alt: '作品十三描述' }
    ];

    const paginationContainer = document.getElementById('pagination-container');
    let currentPage = 1;
    const photosPerPage = 6; // 设置每页显示6张照片，您可以修改这个数字

    // 2. 根据当前页码显示照片的函数
    function displayPage(page) {
        galleryContainer.innerHTML = ''; // 清空当前所有照片
        currentPage = page;

        const startIndex = (page - 1) * photosPerPage;
        const endIndex = startIndex + photosPerPage;
        const photosToShow = allPhotos.slice(startIndex, endIndex);

        photosToShow.forEach(photo => {
            const item = document.createElement('div');
            item.className = 'gallery-item';
            item.innerHTML = `<img src="${photo.src}" alt="${photo.alt}">`;
            galleryContainer.appendChild(item);
        });
        
        // 更新分页按钮的激活状态
        updatePaginationButtons();
    }

    // 3. 创建并设置分页按钮的函数
    function setupPagination() {
        paginationContainer.innerHTML = ''; // 清空分页容器
        const pageCount = Math.ceil(allPhotos.length / photosPerPage);

        for (let i = 1; i <= pageCount; i++) {
            const btn = document.createElement('button');
            btn.innerText = i;
            btn.className = 'pagination-button';
            btn.addEventListener('click', () => {
                displayPage(i);
            });
            paginationContainer.appendChild(btn);
        }
    }
    
    // 4. 更新分页按钮激活样式的函数
    function updatePaginationButtons() {
        const buttons = document.querySelectorAll('.pagination-button');
        buttons.forEach((button, index) => {
            if ((index + 1) === currentPage) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }

    // 5. 初始化页面
    setupPagination();
    displayPage(1); // 默认显示第一页
});

document.addEventListener('DOMContentLoaded', main);
