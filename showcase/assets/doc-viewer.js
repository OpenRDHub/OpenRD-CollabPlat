class DocViewer {
  constructor(options = {}) {
    this.contentEl = document.querySelector(options.contentSelector || '#doc-content');
    this.tocEl = document.querySelector(options.tocSelector || '#doc-toc');
    this.loadingEl = document.querySelector(options.loadingSelector || '#doc-loading');
    this.observer = null;
    this.activeLink = null;
  }

  async load(url) {
    if (this.loadingEl) this.loadingEl.style.display = 'flex';
    if (this.contentEl) this.contentEl.style.display = 'none';

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Failed to load: ${res.status}`);
      const md = await res.text();
      this.render(md);
    } catch (err) {
      if (this.contentEl) {
        this.contentEl.innerHTML = `<p style="color:var(--red)">Failed to load document: ${err.message}</p>`;
        this.contentEl.style.display = 'block';
      }
    } finally {
      if (this.loadingEl) this.loadingEl.style.display = 'none';
    }
  }

  render(md) {
    if (!this.contentEl) return;

    const html = marked.parse(md, {
      gfm: true,
      breaks: false
    });
    this.contentEl.innerHTML = html;
    this.contentEl.style.display = 'block';

    this.wrapTables();
    this.buildToc();
    this.setupScrollSpy();
  }

  wrapTables() {
    this.contentEl.querySelectorAll('table').forEach(table => {
      if (table.parentElement.classList.contains('table-wrap')) return;
      const wrapper = document.createElement('div');
      wrapper.className = 'table-wrap';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    });
  }

  buildToc() {
    if (!this.tocEl) return;

    const headings = this.contentEl.querySelectorAll('h2, h3');
    if (headings.length === 0) return;

    const list = document.createElement('ul');
    list.className = 'toc-list';

    headings.forEach((heading, i) => {
      const id = `section-${i}`;
      heading.id = id;

      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${id}`;
      a.textContent = heading.textContent;
      a.dataset.target = id;

      if (heading.tagName === 'H3') {
        a.classList.add('toc-h3');
      }

      li.appendChild(a);
      list.appendChild(li);
    });

    this.tocEl.innerHTML = '';
    this.tocEl.appendChild(list);
  }

  setupScrollSpy() {
    if (!this.tocEl) return;
    if (this.observer) this.observer.disconnect();

    const headings = this.contentEl.querySelectorAll('h2[id], h3[id]');
    if (headings.length === 0) return;

    this.observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          const link = this.tocEl.querySelector(`a[data-target="${id}"]`);
          if (link) {
            if (this.activeLink) this.activeLink.classList.remove('active');
            link.classList.add('active');
            this.activeLink = link;
          }
        }
      });
    }, {
      rootMargin: '-80px 0px -60% 0px',
      threshold: 0
    });

    headings.forEach(h => this.observer.observe(h));
  }
}

window.DocViewer = DocViewer;
